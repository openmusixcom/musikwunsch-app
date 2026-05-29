# Phase 2 Testing Guide

## Prerequisites
1. Docker containers deployed on Hostinger VPS and running
2. Backend API accessible at http://87.106.215.187.nip.io
3. Database migrations have been run (001_initial_schema.sql, 002_guest_sessions.sql)

## Test Workflow

### 1. Create a DJ Event (Requires DJ Authentication)
```bash
# Register/Login as DJ
curl -X POST http://87.106.215.187.nip.io/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dj@test.local",
    "password": "testpass123",
    "role": "dj"
  }'

# Response will include token - save this
# Then create an event:
curl -X POST http://87.106.215.187.nip.io/api/guest/events \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "name": "Test Event",
    "guestLimit": 50
  }'

# Response will include QR code
```

### 2. Load Sample Songs
The database needs songs for testing. SSH into the VPS and run:
```bash
ssh root@187.124.20.215
docker exec musikwunsch-db psql -U musikwunsch -d musikwunsch -c "
INSERT INTO songs (title, artist, album, duration, genre) VALUES
('Hello', 'Adele', '25', 295, 'Pop'),
('Shape of You', 'Ed Sheeran', '÷', 233, 'Pop'),
('Blinding Lights', 'The Weeknd', 'After Hours', 200, 'Synthwave'),
('As It Was', 'Harry Styles', 'Harry''s House', 167, 'Pop'),
('Rolling Stone', 'Bob Dylan', 'Like a Rolling Stone', 369, 'Rock'),
('Imagine', 'John Lennon', 'Imagine', 183, 'Rock'),
('Bohemian Rhapsody', 'Queen', 'A Night at the Opera', 354, 'Rock'),
('Stairway to Heaven', 'Led Zeppelin', 'Led Zeppelin IV', 482, 'Rock'),
('Smells Like Teen Spirit', 'Nirvana', 'Nevermind', 301, 'Grunge'),
('Purple Haze', 'Jimi Hendrix', 'Are You Experienced', 175, 'Rock');
"
```

### 3. Activate Event
```bash
curl -X PUT http://87.106.215.187.nip.io/api/guest/events/{eventId}/status \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"status": "active"}'
```

### 4. Guest QR Validation Test
```bash
curl -X POST http://87.106.215.187.nip.io/api/guest/qr/validate \
  -H "Content-Type: application/json" \
  -d '{
    "qrCode": "YOUR_QR_CODE",
    "eventId": "YOUR_EVENT_ID"
  }'

# Response should include sessionId
```

### 5. Search Songs Test
```bash
curl http://87.106.215.187.nip.io/api/guest/songs/search?query=adele&eventId=YOUR_EVENT_ID

# Response should include songs matching "adele"
```

### 6. Add Song Request Test
```bash
curl -X POST http://87.106.215.187.nip.io/api/guest/events/{eventId}/requests \
  -H "Content-Type: application/json" \
  -d '{
    "songId": 1,
    "guestName": "John",
    "guestSessionId": "YOUR_SESSION_ID"
  }'
```

### 7. Vote for Song Test
```bash
curl -X POST http://87.106.215.187.nip.io/api/guest/requests/{wishId}/vote \
  -H "Content-Type: application/json" \
  -d '{"guestSessionId": "YOUR_SESSION_ID"}'
```

### 8. Get Queue Test
```bash
curl http://87.106.215.187.nip.io/api/guest/events/{eventId}/queue

# Response should show songs sorted by vote count
```

## Frontend Testing

1. Open http://87.106.215.187.nip.io/guest
2. Enter QR code from your event
3. Enter your name
4. Search for songs (e.g., "adele")
5. Click + to add a song request
6. View the queue and voting

## Database Verification

Connect to PostgreSQL:
```bash
docker exec -it musikwunsch-db psql -U musikwunsch -d musikwunsch
```

Check tables:
```sql
SELECT * FROM songs LIMIT 5;
SELECT * FROM guest_sessions;
SELECT * FROM wishes;
SELECT * FROM votes;
```

## Common Issues

### "Event is not active"
- Ensure event status is updated to 'active' before guests can join

### "Invalid QR code or event"
- Verify the QR code matches the event's qr_code field
- Check that eventId is correct

### No songs in search results
- Verify songs table has been populated
- Check that the song title/artist matches the search query

### "Session expired or invalid"
- Sessions expire after 24 hours
- Create a new session with QR validation
