-- Sample Data for Wipeout & Chill
-- Run this after 001_initial_schema.sql to populate with fun, beginner-friendly data

-- Insert a sample location (Chicago-inspired)
INSERT INTO locations (name, timezone, address) 
VALUES ('Lake Shore Location', 'America/Chicago', '123 Lake Shore Drive, Chicago, IL')
ON CONFLICT DO NOTHING;

-- Sample Boards with fun, beginner-friendly names
-- These will automatically use the location created above
INSERT INTO boards (location_id, name, brand, size, status, condition) VALUES
((SELECT id FROM locations WHERE name = 'Lake Shore Location'), 'The Windy City Wipeout', 'Beginner Friendly', '9''0', 'available', 'excellent'),
((SELECT id FROM locations WHERE name = 'Lake Shore Location'), 'Da Bears Board', 'Chicago Special', '8''6', 'available', 'good'),
((SELECT id FROM locations WHERE name = 'Lake Shore Location'), 'Lake Michigan Dreamer', 'Great Lakes', '9''6', 'available', 'excellent'),
((SELECT id FROM locations WHERE name = 'Lake Shore Location'), 'The Fall Classic', 'Autumn Collection', '8''0', 'available', 'good'),
((SELECT id FROM locations WHERE name = 'Lake Shore Location'), 'Movie Night Special', 'Entertainment Series', '7''6', 'available', 'good'),
((SELECT id FROM locations WHERE name = 'Lake Shore Location'), 'Beginner''s Luck', 'First Timer', '10''0', 'available', 'excellent'),
((SELECT id FROM locations WHERE name = 'Lake Shore Location'), 'The Wipeout Warrior', 'Adventure Line', '8''6', 'available', 'good'),
((SELECT id FROM locations WHERE name = 'Lake Shore Location'), 'Chicago Pride', 'Windy City', '9''0', 'available', 'excellent'),
((SELECT id FROM locations WHERE name = 'Lake Shore Location'), 'The October Surfer', 'Fall Collection', '8''0', 'available', 'good'),
((SELECT id FROM locations WHERE name = 'Lake Shore Location'), 'Film Buff Board', 'Cinema Series', '7''6', 'available', 'good')
ON CONFLICT DO NOTHING;
