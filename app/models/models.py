from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, DateTime, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    short_name = Column(String(20))
    metadata_ = Column("metadata", JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    players = relationship("Player", back_populates="team")


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)
    external_id = Column(String(64))
    title = Column(String(255), nullable=False)
    sport = Column(String(50), nullable=False)
    venue = Column(String(255))
    start_time = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)
    home_team_id = Column(Integer, ForeignKey("teams.id"))
    away_team_id = Column(Integer, ForeignKey("teams.id"))
    status = Column(String(30), nullable=False, default="scheduled")
    metadata_ = Column("metadata", JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    home_team = relationship("Team", foreign_keys=[home_team_id])
    away_team = relationship("Team", foreign_keys=[away_team_id])
    events = relationship("Event", back_populates="match", cascade="all, delete-orphan")
    highlights = relationship("Highlight", back_populates="match", cascade="all, delete-orphan")


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    name = Column(String(120), nullable=False)
    role = Column(String(50))
    jersey_number = Column(Integer)
    metadata_ = Column("metadata", JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship("Team", back_populates="players")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    timestamp_seconds = Column(Integer, nullable=False)
    event_type = Column(String(50), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"))
    player_id = Column(Integer, ForeignKey("players.id"))
    secondary_player_id = Column(Integer, ForeignKey("players.id"))
    description = Column(Text)
    importance = Column(Integer, default=5)
    score_home_after = Column(Integer)
    score_away_after = Column(Integer)
    metadata_ = Column("metadata", JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    match = relationship("Match", back_populates="events")
    player = relationship("Player", foreign_keys=[player_id])
    secondary_player = relationship("Player", foreign_keys=[secondary_player_id])
    team = relationship("Team", foreign_keys=[team_id])


class Highlight(Base):
    __tablename__ = "highlights"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"))
    timestamp_seconds = Column(Integer, nullable=False)
    duration_seconds = Column(Integer, default=15)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    importance = Column(Integer, default=5)
    thumbnail_url = Column(Text)
    metadata_ = Column("metadata", JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    match = relationship("Match", back_populates="highlights")
    event = relationship("Event")


class PlayerStat(Base):
    __tablename__ = "player_stats"
    __table_args__ = (UniqueConstraint("match_id", "player_id"),)

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    stats = Column(JSONB, nullable=False, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    player = relationship("Player")


class MatchStat(Base):
    __tablename__ = "match_stats"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"))
    stats = Column(JSONB, nullable=False, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Rule(Base):
    __tablename__ = "rules"
    __table_args__ = (UniqueConstraint("sport", "rule_key"),)

    id = Column(Integer, primary_key=True)
    sport = Column(String(50), nullable=False)
    rule_key = Column(String(80), nullable=False)
    title = Column(String(255), nullable=False)
    explanation = Column(Text, nullable=False)
    examples = Column(JSONB)
    metadata_ = Column("metadata", JSONB, default={})


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True)
    user_key = Column(String(100), nullable=False)
    entity_type = Column(String(30), nullable=False)
    entity_id = Column(Integer, nullable=False)
    metadata_ = Column("metadata", JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
