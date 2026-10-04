-- FireSight Sports — Sample Seed Data
-- One realistic football (soccer) match, ~12 minutes of action, 30+ events
-- Video should be a matching ~12 min highlight / condensed match clip

-- ============================================================
-- TEAMS
-- ============================================================
INSERT INTO teams (id, name, short_name) VALUES
(1, 'North United', 'NUFC'),
(2, 'South Rovers', 'SRFC')
ON CONFLICT DO NOTHING;

-- ============================================================
-- MATCH
-- ============================================================
INSERT INTO matches (id, title, sport, venue, duration_seconds, home_team_id, away_team_id, status, metadata) VALUES
(1, 'North United vs South Rovers — Friendly', 'football', 'City Arena', 720, 1, 2, 'completed',
 '{"competition": "Demo Cup", "video_file": "sample_match.mp4"}'::jsonb)
ON CONFLICT DO NOTHING;

-- ============================================================
-- PLAYERS
-- ============================================================
INSERT INTO players (id, team_id, name, role, jersey_number) VALUES
-- North United
(1, 1, 'Alex Rivera',   'forward',    9),
(2, 1, 'Jamie Cole',    'midfielder', 8),
(3, 1, 'Sam Ortiz',     'defender',   4),
(4, 1, 'Chris Nolan',   'goalkeeper', 1),
(5, 1, 'Taylor Brooks', 'forward',    11),
-- South Rovers
(6, 2, 'Jordan Lee',    'forward',    10),
(7, 2, 'Morgan Blake',  'midfielder', 6),
(8, 2, 'Casey Quinn',   'defender',   5),
(9, 2, 'Riley Santos',  'goalkeeper', 1),
(10,2, 'Avery Patel',   'forward',    7)
ON CONFLICT DO NOTHING;

-- ============================================================
-- EVENTS  (timestamp_seconds = seconds from start of video)
-- importance 1-10 (10 = biggest moments)
-- ============================================================
INSERT INTO events (match_id, timestamp_seconds, event_type, team_id, player_id, secondary_player_id, description, importance, score_home_after, score_away_after, metadata) VALUES
(1,  25,  'kickoff',      NULL, NULL, NULL, 'Match kicks off', 3, 0, 0, '{}'),
(1,  68,  'chance',       1, 1, 2, 'Rivera forces a good save from Santos', 5, 0, 0, '{}'),
(1, 112,  'corner',       1, 2, NULL, 'Corner for North United', 3, 0, 0, '{}'),
(1, 145,  'goal',         1, 1, 2, 'GOAL! Alex Rivera finishes a low cross from Cole', 10, 1, 0, '{"assist":"Jamie Cole"}'),
(1, 148,  'celebration',  1, 1, NULL, 'Rivera celebrates with the home fans', 4, 1, 0, '{}'),
(1, 190,  'foul',         2, 8, 1, 'Quinn brings down Rivera — free kick', 4, 1, 0, '{}'),
(1, 210,  'freekick',     1, 2, NULL, 'Cole free-kick just over the bar', 5, 1, 0, '{}'),
(1, 255,  'chance',       2, 6, 7, 'Lee goes close after a quick one-two', 6, 1, 0, '{}'),
(1, 280,  'save',         1, 4, 6, 'Great save by Nolan from Lee’s shot', 7, 1, 0, '{}'),
(1, 310,  'yellow_card',  2, 8, NULL, 'Yellow card for Casey Quinn', 5, 1, 0, '{}'),
(1, 340,  'substitution', 1, 5, 3, 'Brooks replaces Ortiz', 3, 1, 0, '{}'),
(1, 365,  'goal',         2, 6, 7, 'GOAL! Jordan Lee equalises with a powerful header', 10, 1, 1, '{"assist":"Morgan Blake"}'),
(1, 370,  'celebration',  2, 6, NULL, 'Lee runs to the away end', 4, 1, 1, '{}'),
(1, 400,  'chance',       1, 5, 2, 'Brooks forces another save', 5, 1, 1, '{}'),
(1, 430,  'corner',       2, 7, NULL, 'Corner for South Rovers', 3, 1, 1, '{}'),
(1, 455,  'goal',         1, 5, 2, 'GOAL! Taylor Brooks restores the lead with a sharp finish', 10, 2, 1, '{"assist":"Jamie Cole"}'),
(1, 460,  'celebration',  1, 5, NULL, 'Brooks slides on his knees', 4, 2, 1, '{}'),
(1, 500,  'foul',         1, 2, 6, 'Cole fouls Lee — free kick in dangerous area', 5, 2, 1, '{}'),
(1, 520,  'freekick',     2, 7, NULL, 'Blake free-kick saved by Nolan', 6, 2, 1, '{}'),
(1, 550,  'yellow_card',  1, 2, NULL, 'Yellow card for Jamie Cole', 4, 2, 1, '{}'),
(1, 580,  'chance',       2, 10, 6, 'Patel hits the side netting', 5, 2, 1, '{}'),
(1, 610,  'substitution', 2, 10, 8, 'Patel comes on for Quinn', 3, 2, 1, '{}'),
(1, 640,  'chance',       1, 1, 5, 'Rivera again — blocked on the line', 7, 2, 1, '{}'),
(1, 670,  'goal',         2, 6, 10, 'GOAL! Lee levels again with a late strike', 10, 2, 2, '{"assist":"Avery Patel"}'),
(1, 675,  'celebration',  2, 6, NULL, 'Dramatic equaliser — Lee is mobbed', 5, 2, 2, '{}'),
(1, 700,  'chance',       1, 5, 2, 'Brooks heads just wide in the final minute', 6, 2, 2, '{}'),
(1, 715,  'fulltime',     NULL, NULL, NULL, 'Full time — 2-2 thriller', 8, 2, 2, '{}')
ON CONFLICT DO NOTHING;

-- ============================================================
-- HIGHLIGHTS (derived from key events)
-- ============================================================
INSERT INTO highlights (match_id, event_id, timestamp_seconds, duration_seconds, title, description, importance) VALUES
(1, (SELECT id FROM events WHERE timestamp_seconds=145 LIMIT 1), 140, 20, 'Rivera opens the scoring', 'Alex Rivera finishes a low cross from Jamie Cole', 10),
(1, (SELECT id FROM events WHERE timestamp_seconds=365 LIMIT 1), 360, 20, 'Lee equalises', 'Jordan Lee powers a header into the net', 10),
(1, (SELECT id FROM events WHERE timestamp_seconds=455 LIMIT 1), 450, 20, 'Brooks restores the lead', 'Taylor Brooks with a sharp finish', 10),
(1, (SELECT id FROM events WHERE timestamp_seconds=670 LIMIT 1), 665, 25, 'Lee’s late equaliser', 'Dramatic late goal from Jordan Lee', 10),
(1, (SELECT id FROM events WHERE timestamp_seconds=280 LIMIT 1), 275, 15, 'Nolan’s big save', 'Chris Nolan denies Lee with a diving save', 7)
ON CONFLICT DO NOTHING;

-- ============================================================
-- PLAYER STATS (simplified)
-- ============================================================
INSERT INTO player_stats (match_id, player_id, stats) VALUES
(1, 1, '{"goals":1,"assists":0,"shots":4,"shots_on_target":3,"passes":28}'::jsonb),
(1, 2, '{"goals":0,"assists":2,"shots":1,"shots_on_target":0,"passes":45}'::jsonb),
(1, 5, '{"goals":1,"assists":0,"shots":3,"shots_on_target":2,"passes":18}'::jsonb),
(1, 4, '{"saves":4,"goals_conceded":2,"punches":1}'::jsonb),
(1, 6, '{"goals":2,"assists":0,"shots":5,"shots_on_target":4,"passes":22}'::jsonb),
(1, 7, '{"goals":0,"assists":1,"shots":2,"shots_on_target":1,"passes":38}'::jsonb),
(1, 10,'{"goals":0,"assists":1,"shots":2,"shots_on_target":0,"passes":15}'::jsonb)
ON CONFLICT DO NOTHING;

-- ============================================================
-- MATCH STATS
-- ============================================================
INSERT INTO match_stats (match_id, team_id, stats) VALUES
(1, 1, '{"possession":54,"shots":11,"shots_on_target":6,"corners":5,"fouls":8}'::jsonb),
(1, 2, '{"possession":46,"shots":9,"shots_on_target":5,"corners":3,"fouls":11}'::jsonb),
(1, NULL, '{"total_goals":4,"total_yellow_cards":2}'::jsonb)
ON CONFLICT DO NOTHING;

-- ============================================================
-- RULES (examples)
-- ============================================================
INSERT INTO rules (sport, rule_key, title, explanation, examples) VALUES
('football', 'offside', 'Offside',
 'A player is in an offside position if any of their body parts (except hands/arms) is closer to the opponents’ goal line than both the ball and the second-last opponent when the ball is played to them.',
 '["A forward receives the ball while beyond the last defender","Goal ruled out for offside"]'::jsonb),
('football', 'yellow_card', 'Yellow Card',
 'A caution (yellow card) is shown for unsporting behaviour, dissent, persistent fouls, delaying the restart, etc. Two yellow cards in one match result in a red card and sending-off.',
 '["Hard tackle from behind","Deliberate handball to stop an attack"]'::jsonb),
('football', 'penalty', 'Penalty Kick',
 'Awarded when a foul that would normally be a direct free kick is committed by a defending player inside their own penalty area.',
 '["Foul inside the box","Handball by defender on the goal line"]'::jsonb)
ON CONFLICT DO NOTHING;
