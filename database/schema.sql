-- FireSight Sports — PostgreSQL Schema
-- Source of truth for match understanding (no computer vision on video)

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- CORE TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS teams (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(120) NOT NULL,
    short_name      VARCHAR(20),
    metadata        JSONB DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS matches (
    id                  SERIAL PRIMARY KEY,
    external_id         VARCHAR(64),
    title               VARCHAR(255) NOT NULL,
    sport               VARCHAR(50)  NOT NULL,          -- cricket | football | basketball ...
    venue               VARCHAR(255),
    start_time          TIMESTAMPTZ,
    duration_seconds    INTEGER,
    home_team_id        INTEGER REFERENCES teams(id),
    away_team_id        INTEGER REFERENCES teams(id),
    status              VARCHAR(30)  NOT NULL DEFAULT 'scheduled',  -- scheduled | live | completed
    metadata            JSONB DEFAULT '{}'::jsonb,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS players (
    id              SERIAL PRIMARY KEY,
    team_id         INTEGER REFERENCES teams(id),
    name            VARCHAR(120) NOT NULL,
    role            VARCHAR(50),                        -- batsman | bowler | all-rounder | forward ...
    jersey_number   INTEGER,
    metadata        JSONB DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- EVENTS  (most important table — video sync key)
-- ============================================================

CREATE TABLE IF NOT EXISTS events (
    id                      SERIAL PRIMARY KEY,
    match_id                INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    timestamp_seconds       INTEGER NOT NULL,           -- seconds from start of video
    event_type              VARCHAR(50)  NOT NULL,      -- goal | wicket | four | six | foul | card ...
    team_id                 INTEGER REFERENCES teams(id),
    player_id               INTEGER REFERENCES players(id),
    secondary_player_id     INTEGER REFERENCES players(id),  -- assist / bowler etc.
    description             TEXT,
    importance              INTEGER DEFAULT 5 CHECK (importance BETWEEN 1 AND 10),
    score_home_after        INTEGER,
    score_away_after        INTEGER,
    metadata                JSONB DEFAULT '{}'::jsonb,
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_events_match_ts
    ON events (match_id, timestamp_seconds);

CREATE INDEX IF NOT EXISTS idx_events_type
    ON events (match_id, event_type);

CREATE INDEX IF NOT EXISTS idx_events_importance
    ON events (match_id, importance DESC);

-- ============================================================
-- HIGHLIGHTS
-- ============================================================

CREATE TABLE IF NOT EXISTS highlights (
    id                  SERIAL PRIMARY KEY,
    match_id            INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    event_id            INTEGER REFERENCES events(id),
    timestamp_seconds   INTEGER NOT NULL,
    duration_seconds    INTEGER DEFAULT 15,
    title               VARCHAR(255) NOT NULL,
    description         TEXT,
    importance          INTEGER DEFAULT 5,
    thumbnail_url       TEXT,
    metadata            JSONB DEFAULT '{}'::jsonb,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_highlights_match_ts
    ON highlights (match_id, timestamp_seconds);

-- ============================================================
-- STATS
-- ============================================================

CREATE TABLE IF NOT EXISTS player_stats (
    id          SERIAL PRIMARY KEY,
    match_id    INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    player_id   INTEGER NOT NULL REFERENCES players(id),
    stats       JSONB NOT NULL DEFAULT '{}'::jsonb,     -- flexible per sport
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (match_id, player_id)
);

CREATE TABLE IF NOT EXISTS match_stats (
    id          SERIAL PRIMARY KEY,
    match_id    INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    team_id     INTEGER REFERENCES teams(id),           -- NULL = overall match
    stats       JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- RULES (for “Explain the rule”)
-- ============================================================

CREATE TABLE IF NOT EXISTS rules (
    id          SERIAL PRIMARY KEY,
    sport       VARCHAR(50) NOT NULL,
    rule_key    VARCHAR(80) NOT NULL,
    title       VARCHAR(255) NOT NULL,
    explanation TEXT NOT NULL,
    examples    JSONB,
    metadata    JSONB DEFAULT '{}'::jsonb,
    UNIQUE (sport, rule_key)
);

-- ============================================================
-- FAVORITES (prototype / local user)
-- ============================================================

CREATE TABLE IF NOT EXISTS favorites (
    id          SERIAL PRIMARY KEY,
    user_key    VARCHAR(100) NOT NULL,                  -- device or anonymous id
    entity_type VARCHAR(30)  NOT NULL,                  -- player | team
    entity_id   INTEGER      NOT NULL,
    metadata    JSONB DEFAULT '{}'::jsonb,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
