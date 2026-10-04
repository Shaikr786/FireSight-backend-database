from pydantic import BaseModel, Field
from typing import Any, Optional


class TeamOut(BaseModel):
    id: int
    name: str
    short_name: Optional[str] = None

    class Config:
        from_attributes = True


class PlayerOut(BaseModel):
    id: int
    name: str
    role: Optional[str] = None
    jersey_number: Optional[int] = None
    team_id: Optional[int] = None

    class Config:
        from_attributes = True


class EventOut(BaseModel):
    id: int
    match_id: int
    timestamp_seconds: int
    event_type: str
    team_id: Optional[int] = None
    player_id: Optional[int] = None
    player_name: Optional[str] = None
    secondary_player_id: Optional[int] = None
    description: Optional[str] = None
    importance: int = 5
    score_home_after: Optional[int] = None
    score_away_after: Optional[int] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class HighlightOut(BaseModel):
    id: int
    match_id: int
    event_id: Optional[int] = None
    timestamp_seconds: int
    duration_seconds: int = 15
    title: str
    description: Optional[str] = None
    importance: int = 5

    class Config:
        from_attributes = True


class MatchOut(BaseModel):
    id: int
    title: str
    sport: str
    venue: Optional[str] = None
    duration_seconds: Optional[int] = None
    status: str
    home_team: Optional[TeamOut] = None
    away_team: Optional[TeamOut] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class ContextOut(BaseModel):
    """The single most important response for the whole product."""
    match_id: int
    timestamp_seconds: int
    score: dict[str, int]                    # {"home": 2, "away": 1}
    match_status: str
    recent_events: list[EventOut]
    nearby_highlights: list[HighlightOut]
    current_players_hint: list[PlayerOut] = []
    home_team: Optional[TeamOut] = None
    away_team: Optional[TeamOut] = None


class PlayerStatOut(BaseModel):
    player_id: int
    player_name: Optional[str] = None
    stats: dict[str, Any]

    class Config:
        from_attributes = True


class MatchStatOut(BaseModel):
    team_id: Optional[int] = None
    stats: dict[str, Any]

    class Config:
        from_attributes = True


class RuleOut(BaseModel):
    id: int
    sport: str
    rule_key: str
    title: str
    explanation: str
    examples: Optional[list[Any]] = None

    class Config:
        from_attributes = True


class AIAskRequest(BaseModel):
    question: str
    timestamp_seconds: int
    user_key: Optional[str] = None


class AIAskResponse(BaseModel):
    answer: str
    related_event_ids: list[int] = []
    suggested_actions: list[dict[str, Any]] = []   # e.g. [{"type":"seek","timestamp_seconds":412}]
    context_used: Optional[ContextOut] = None


class HighlightSearchRequest(BaseModel):
    query: str
    timestamp_seconds: Optional[int] = None
