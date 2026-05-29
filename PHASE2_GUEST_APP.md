# Phase 2: Guest App mit QR-Code Access

## Übersicht

Phase 2 implementiert die Guest App - die zentrale Schnittstelle für Gäste, um Musikwünsche einzureichen, zu suchen und für Songs zu votieren.

## Neue Features

### 1. **QR-Code Access System**
- DJ generiert eindeutigen QR-Code pro Event
- Gäste scannen QR-Code (oder geben manuell Code ein)
- Sichere Session-ID wird generiert (gültig 24 Stunden)
- Automatische Gast-Zählung

**Endpoints:**
- `POST /api/guest/qr/validate` - QR-Code validieren und Session erstellen
- `GET /api/guest/session/:sessionId` - Session validieren
- `PUT /api/guest/session/:sessionId/name` - Gastnamen setzen
- `DELETE /api/guest/session/:sessionId` - Session beenden

### 2. **Music Search**
- Guests können nach Songtiteln und Künstlern suchen
- Full-Text-Suche in PostgreSQL
- Unterstützt deutsche Sprache
- Zeigt Dauer, Artist, Album an

**Endpoint:**
- `GET /api/guest/songs/search?query=...&eventId=...` - Lieder suchen

### 3. **Song Requests / Wishes**
- Gäste können Songs anfordern
- Verhindert Duplikate (ein Guest pro Song)
- Verbunden mit Event und Guest Session
- Status: pending → approved → playing → played

**Endpoints:**
- `POST /api/guest/events/:eventId/requests` - Song anfordern
- `GET /api/guest/requests/:wishId` - Song-Anfrage Details
- `DELETE /api/guest/requests/:wishId` - Eigene Anfrage löschen

### 4. **Voting System**
- Gäste können für Songs votieren
- Ein Vote pro Guest pro Song
- Live-Vote-Zählung
- Songs sortieren sich nach Votes

**Endpoints:**
- `POST /api/guest/requests/:wishId/vote` - Abstimmen
- `GET /api/guest/events/:eventId/queue` - Queue mit Vote-Counts abrufen

### 5. **Real-Time Queue Display**
- Live-Queue mit aktuellen Votes
- Auto-Refresh alle 5 Sekunden
- Sortierung nach Votes (Engagement-Ranking)

## Datenbankschema

### Guest Sessions Table
```sql
CREATE TABLE guest_sessions (
  id VARCHAR(255) PRIMARY KEY,           -- Eindeutige Session ID (8-stellig)
  event_id UUID NOT NULL,                -- Event Referenz
  guest_name VARCHAR(255),               -- Name des Gastes
  ip_address VARCHAR(45),                -- Client IP für Analytics
  expires_at TIMESTAMP NOT NULL,         -- Session Expiration (24h)
  created_at TIMESTAMP
);
```

### Event Queue Query
```sql
SELECT w.*, s.title, s.artist, s.duration,
       (SELECT COUNT(*) FROM votes WHERE wish_id = w.id) as vote_count
FROM wishes w
LEFT JOIN songs s ON w.song_id = s.id
WHERE w.event_id = $1 AND w.status IN ('pending', 'approved', 'playing')
ORDER BY w.vote_count DESC, w.created_at ASC;
```

## Frontend Architecture

### Pages & Components

```
GuestPage.jsx
├── Stages:
│   ├── QR Entry (QR-Code eingeben/scannen)
│   ├── Name Entry (Name eingeben)
│   └── Main (Search + Queue)
├── Search Section
│   ├── Search Form
│   └── Search Results
└── Queue Section
    ├── Queue List
    └── Vote Buttons
```

### Workflow

1. **QR Entry Stage**
   - Gast öffnet `http://localhost:8080/guest`
   - Scannt QR-Code oder gibt Code manuell ein
   - System validiert und erstellt Session

2. **Name Entry Stage**
   - Gast gibt seinen Namen ein
   - Name wird in Session gespeichert

3. **Main Stage (Search + Queue)**
   ```
   ┌─────────────────────────────────┐
   │  Musikwunsch - Event Name        │
   │  Welcome, Guest Name!            │
   ├────────────────┬────────────────┤
   │  SEARCH SONGS  │  QUEUE         │
   │  [Search Box]  │  1. Song1 (5V) │
   │  Results:      │     👍 Vote    │
   │  - Song1       │  2. Song2 (3V) │
   │    + Add       │     👍 Vote    │
   │  - Song2       │  3. Song3 (1V) │
   │    + Add       │     👍 Vote    │
   └────────────────┴────────────────┘
   ```

## Sicherheit & Limits

### Session Management
- Sessions ablaufen nach 24 Stunden
- Session IDs sind 8-stellige Hexadecimal-Codes
- Expiration prüfung auf allen Endpoints
- Guest Count Tracking verhindert Overselling

### Voting Protection
- Ein Vote pro Guest pro Song (UNIQUE constraint)
- Verhindert Vote-Manipulation
- IP-Logging für Analytics/Fraud-Detection

### Request Limits
- Duplikat-Song-Requests verhindert
- Guests können nur ihre eigenen Requests löschen
- Event Capacity Limits durchgesetzt

## API Beispiele

### 1. QR-Code Validieren
```bash
POST /api/guest/qr/validate
Content-Type: application/json

{
  "qrCode": "ABCD1234",
  "eventId": "uuid-..."
}

Response:
{
  "sessionId": "XYZ789AB",
  "eventId": "uuid-...",
  "eventName": "Friday Party",
  "expiresAt": "2026-05-30T01:40:41Z"
}
```

### 2. Songs Suchen
```bash
GET /api/guest/songs/search?query=adele&eventId=uuid-...

Response:
[
  {
    "id": 1,
    "title": "Hello",
    "artist": "Adele",
    "album": "25",
    "duration": 295
  },
  ...
]
```

### 3. Song Anfordern
```bash
POST /api/guest/events/:eventId/requests
Content-Type: application/json

{
  "songId": 1,
  "guestName": "John",
  "guestSessionId": "XYZ789AB"
}

Response:
{
  "wishId": "uuid-...",
  "status": "pending",
  "message": "Song request added"
}
```

### 4. Queue Abrufen
```bash
GET /api/guest/events/:eventId/queue

Response:
[
  {
    "id": "uuid-...",
    "title": "Hello",
    "artist": "Adele",
    "guest_name": "John",
    "status": "pending",
    "vote_count": 5
  },
  ...
]
```

## Testing Phase 2

### Manual Testing Steps

1. **QR Access Test**
   ```
   1. Öffne http://localhost:8080/guest
   2. Gib Event-QR-Code ein
   3. Gib deinen Namen ein
   4. System sollte dich zur Queue weiterleiten
   ```

2. **Search Test**
   ```
   1. Suche nach "adele"
   2. Sollte Songs anzeigen
   3. Klicke "+" um Song hinzuzufügen
   ```

3. **Voting Test**
   ```
   1. Füge einen Song hinzu
   2. Öffne Queue
   3. Klicke 👍 um zu votieren
   4. Vote Count sollte sich erhöhen
   ```

4. **Multiple Guest Test**
   ```
   1. Öffne zwei Tabs mit /guest
   2. Beide connecten zu gleichem Event
   3. Guest 1 votiert für Song
   4. Guest 2 sollte Update in realtime sehen
   ```

## Nächste Schritte (Phase 3)

- **DJ Dashboard** - Songs genehmigen/ablehnen
- **Now Playing** - Aktuell spielender Song
- **Song Finished** - Status zum "played" aktualisieren
- **WebSocket Real-Time** - Live-Updates statt Polling
- **Advanced Analytics** - Vote-Trends, Popular Songs

## Technische Details

### Database Indexes
- `idx_guest_sessions_event_id` - Schnelle Event-Lookups
- `idx_guest_sessions_expires_at` - Cleanup von abgelaufenen Sessions
- `idx_wishes_guest_session_id` - Gast-Requests abrufen
- Full-Text-Indexes auf songs (title, artist)

### Performance Optimizations
- Vote-Count wird bei Votes aktualisiert (denormalisiert)
- Queue-Sortierung nutzt indexed Spalten
- Session-Expiration mit DB-Constraints

### Error Handling
- QR-Code Validierung mit Event-Status Check
- Session-Expiration Checks
- Duplikat-Prevention auf DB-Level (UNIQUE constraints)
- Guest-Capacity Limits
