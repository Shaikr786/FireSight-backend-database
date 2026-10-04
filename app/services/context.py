"""
Context Service — the heart of FireSight.

Given match_id + timestamp_seconds, build a compact structured context
that the AI and frontend can trust.
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.models import Match, Event, Highlight, Player
from app.schemas import ContextOut, EventOut, HighlightOut, TeamOut, PlayerOut


def _event_to_out(e: Event) -> EventOut:
    return EventOut(
        id=e.id,
        match_id=e.match_id,
        timestamp_seconds=e.timestamp_seconds,
        event_type=e.event_type,
        team_id=e.team_id,
        player_id=e.player_id,
        player_name=e.player.name if e.player else None,
        secondary_player_id=e.secondary_player_id,
        description=e.description,
        importance=e.importance or 5,
        score_home_after=e.score_home_after,
        score_away_after=e.score_away_after,
        metadata=e.metadata_ or {},
    )


def _highlight_to_out(h: Highlight) -> HighlightOut:
    return HighlightOut(
        id=h.id,
        match_id=h.match_id,
        event_id=h.event_id,
        timestamp_seconds=h.timestamp_seconds,
        duration_seconds=h.duration_seconds or 15,
        title=h.title,
        description=h.description,
        importance=h.importance or 5,
    )


def get_context(
    db: Session,
    match_id: int,
    timestamp_seconds: int,
    recent_window: int = 60,
    highlight_window: int = 120,
) -> ContextOut | None:
    """
    Build full context at a given video timestamp.

    - recent_events: events in the last `recent_window` seconds (including current)
    - score: taken from the latest event that has score_home_after / score_away_after
    - nearby_highlights: highlights within ± highlight_window seconds
    """
    match = (
        db.query(Match)
        .options(
            joinedload(Match.home_team),
            joinedload(Match.away_team),
        )
        .filter(Match.id == match_id)
        .first()
    )
    if not match:
        return None

    # Events up to current timestamp (for score) and recent window
    events_q = (
        db.query(Event)
        .options(joinedload(Event.player))
        .filter(Event.match_id == match_id)
        .filter(Event.timestamp_seconds <= timestamp_seconds)
        .order_by(Event.timestamp_seconds.desc())
    )

    all_past = events_q.all()

    # Score = most recent event that recorded a score
    score_home, score_away = 0, 0
    for e in all_past:
        if e.score_home_after is not None and e.score_away_after is not None:
            score_home = e.score_home_after
            score_away = e.score_away_after
            break

    # Recent events (last N seconds)
    recent = [
        e for e in all_past
        if e.timestamp_seconds >= max(0, timestamp_seconds - recent_window)
    ]
    # Keep chronological order for the response
    recent = list(reversed(recent))

    # Nearby highlights
    highlights = (
        db.query(Highlight)
        .filter(Highlight.match_id == match_id)
        .filter(
            and_(
                Highlight.timestamp_seconds >= max(0, timestamp_seconds - highlight_window),
                Highlight.timestamp_seconds <= timestamp_seconds + highlight_window,
            )
        )
        .order_by(Highlight.importance.desc(), Highlight.timestamp_seconds)
        .limit(10)
        .all()
    )

    # Simple current players hint: players involved in recent high-importance events
    player_ids = set()
    for e in recent:
        if e.player_id:
            player_ids.add(e.player_id)
        if e.secondary_player_id:
            player_ids.add(e.secondary_player_id)

    current_players = []
    if player_ids:
        players = db.query(Player).filter(Player.id.in_(player_ids)).all()
        current_players = [
            PlayerOut(
                id=p.id,
                name=p.name,
                role=p.role,
                jersey_number=p.jersey_number,
                team_id=p.team_id,
            )
            for p in players
        ]

    return ContextOut(
        match_id=match_id,
        timestamp_seconds=timestamp_seconds,
        score={"home": score_home, "away": score_away},
        match_status=match.status,
        recent_events=[_event_to_out(e) for e in recent],
        nearby_highlights=[_highlight_to_out(h) for h in highlights],
        current_players_hint=current_players,
        home_team=TeamOut.model_validate(match.home_team) if match.home_team else None,
        away_team=TeamOut.model_validate(match.away_team) if match.away_team else None,
    )


def get_next_big_moment(
    db: Session,
    match_id: int,
    after_seconds: int,
    min_importance: int = 7,
) -> EventOut | None:
    """Return the next high-importance event after the given timestamp."""
    e = (
        db.query(Event)
        .options(joinedload(Event.player))
        .filter(Event.match_id == match_id)
        .filter(Event.timestamp_seconds > after_seconds)
        .filter(Event.importance >= min_importance)
        .order_by(Event.timestamp_seconds)
        .first()
    )
    return _event_to_out(e) if e else None
