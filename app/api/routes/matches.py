from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models import Match, Event, Highlight, Player, PlayerStat, MatchStat, Rule
from app.schemas import (
    MatchOut, EventOut, HighlightOut, PlayerOut,
    PlayerStatOut, MatchStatOut, RuleOut, ContextOut,
    AIAskRequest, AIAskResponse, HighlightSearchRequest,
)
from app.services.context import get_context, get_next_big_moment, _event_to_out, _highlight_to_out

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("/{match_id}", response_model=MatchOut)
def read_match(match_id: int, db: Session = Depends(get_db)):
    match = (
        db.query(Match)
        .options(joinedload(Match.home_team), joinedload(Match.away_team))
        .filter(Match.id == match_id)
        .first()
    )
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return MatchOut(
        id=match.id,
        title=match.title,
        sport=match.sport,
        venue=match.venue,
        duration_seconds=match.duration_seconds,
        status=match.status,
        home_team=match.home_team,
        away_team=match.away_team,
        metadata=match.metadata_ or {},
    )


@router.get("/{match_id}/context", response_model=ContextOut)
def read_context(
    match_id: int,
    timestamp_seconds: int = Query(..., ge=0, description="Current video time in seconds"),
    db: Session = Depends(get_db),
):
    ctx = get_context(db, match_id, timestamp_seconds)
    if not ctx:
        raise HTTPException(status_code=404, detail="Match not found")
    return ctx


@router.get("/{match_id}/events", response_model=list[EventOut])
def list_events(
    match_id: int,
    event_type: str | None = None,
    min_importance: int | None = None,
    db: Session = Depends(get_db),
):
    q = (
        db.query(Event)
        .options(joinedload(Event.player))
        .filter(Event.match_id == match_id)
    )
    if event_type:
        q = q.filter(Event.event_type == event_type)
    if min_importance is not None:
        q = q.filter(Event.importance >= min_importance)
    events = q.order_by(Event.timestamp_seconds).all()
    return [_event_to_out(e) for e in events]


@router.get("/{match_id}/highlights", response_model=list[HighlightOut])
def list_highlights(match_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(Highlight)
        .filter(Highlight.match_id == match_id)
        .order_by(Highlight.importance.desc(), Highlight.timestamp_seconds)
        .all()
    )
    return [_highlight_to_out(h) for h in rows]


@router.get("/{match_id}/players", response_model=list[PlayerOut])
def list_players(match_id: int, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    team_ids = [t for t in (match.home_team_id, match.away_team_id) if t]
    players = db.query(Player).filter(Player.team_id.in_(team_ids)).all()
    return players


@router.get("/{match_id}/players/{player_id}", response_model=PlayerOut)
def read_player(match_id: int, player_id: int, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.get("/{match_id}/players/{player_id}/stats", response_model=PlayerStatOut)
def read_player_stats(match_id: int, player_id: int, db: Session = Depends(get_db)):
    row = (
        db.query(PlayerStat)
        .filter(PlayerStat.match_id == match_id, PlayerStat.player_id == player_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Stats not found")
    player = db.query(Player).filter(Player.id == player_id).first()
    return PlayerStatOut(
        player_id=player_id,
        player_name=player.name if player else None,
        stats=row.stats or {},
    )


@router.get("/{match_id}/stats", response_model=list[MatchStatOut])
def list_match_stats(match_id: int, db: Session = Depends(get_db)):
    rows = db.query(MatchStat).filter(MatchStat.match_id == match_id).all()
    return [MatchStatOut(team_id=r.team_id, stats=r.stats or {}) for r in rows]


@router.get("/{match_id}/next-big-moment", response_model=EventOut | None)
def next_big_moment(
    match_id: int,
    after_seconds: int = Query(0, ge=0),
    min_importance: int = Query(7, ge=1, le=10),
    db: Session = Depends(get_db),
):
    return get_next_big_moment(db, match_id, after_seconds, min_importance)


# ---------- AI placeholders (AI teammate will enhance) ----------

@router.post("/{match_id}/ai/ask", response_model=AIAskResponse)
def ai_ask(match_id: int, body: AIAskRequest, db: Session = Depends(get_db)):
    """
    Placeholder that returns grounded context + a simple deterministic answer.
    AI teammate should replace the answer generation with an LLM call
    while still using the context returned here.
    """
    ctx = get_context(db, match_id, body.timestamp_seconds)
    if not ctx:
        raise HTTPException(status_code=404, detail="Match not found")

    # Very simple deterministic fallback so the frontend works even without LLM
    if ctx.recent_events:
        last = ctx.recent_events[-1]
        answer = f"At {body.timestamp_seconds}s the score is {ctx.score['home']}-{ctx.score['away']}. "
        answer += f"Most recent event: {last.description or last.event_type}."
        related = [last.id]
        actions = []
        if last.event_type in ("goal", "wicket") and last.timestamp_seconds:
            actions.append({"type": "seek", "timestamp_seconds": last.timestamp_seconds})
    else:
        answer = f"Score is {ctx.score['home']}-{ctx.score['away']}. No major events in the last minute."
        related = []
        actions = []

    return AIAskResponse(
        answer=answer,
        related_event_ids=related,
        suggested_actions=actions,
        context_used=ctx,
    )


@router.post("/{match_id}/ai/recap", response_model=AIAskResponse)
def ai_recap(match_id: int, body: AIAskRequest, db: Session = Depends(get_db)):
    ctx = get_context(db, match_id, body.timestamp_seconds, recent_window=10_000)
    if not ctx:
        raise HTTPException(status_code=404, detail="Match not found")

    goals = [e for e in ctx.recent_events if e.event_type == "goal"]
    answer = f"Recap up to {body.timestamp_seconds}s. Current score {ctx.score['home']}-{ctx.score['away']}. "
    if goals:
        answer += f"{len(goals)} goal(s) so far: "
        answer += "; ".join(g.description or "Goal" for g in goals)
    else:
        answer += "No goals yet."

    return AIAskResponse(
        answer=answer,
        related_event_ids=[g.id for g in goals],
        suggested_actions=[],
        context_used=ctx,
    )


@router.post("/{match_id}/highlights/search", response_model=list[HighlightOut])
def search_highlights(match_id: int, body: HighlightSearchRequest, db: Session = Depends(get_db)):
    """
    Simple keyword search over highlight titles/descriptions.
    AI teammate can later replace this with embeddings / better NL understanding.
    """
    q = body.query.lower()
    rows = (
        db.query(Highlight)
        .filter(Highlight.match_id == match_id)
        .order_by(Highlight.importance.desc())
        .all()
    )
    filtered = [
        h for h in rows
        if q in (h.title or "").lower() or q in (h.description or "").lower()
    ]
    return [_highlight_to_out(h) for h in filtered]
