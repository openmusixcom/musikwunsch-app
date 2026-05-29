import { useState, useEffect } from 'react';
import '../styles/GuestPage.css';

const GuestPage = () => {
  const [stage, setStage] = useState('qr-entry'); // qr-entry, name-entry, main
  const [sessionId, setSessionId] = useState(null);
  const [eventId, setEventId] = useState(null);
  const [eventName, setEventName] = useState('');
  const [guestName, setGuestName] = useState('');
  const [qrCode, setQrCode] = useState('');
  const [error, setError] = useState('');
  const [queue, setQueue] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);

  // Validate QR Code
  const handleQRSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8080/api/guest/qr/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ qrCode, eventId: eventId || 'unknown' })
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || 'Invalid QR code');
        return;
      }

      setSessionId(data.sessionId);
      setEventId(data.eventId);
      setEventName(data.eventName);
      setStage('name-entry');
    } catch (err) {
      setError('Connection error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Set guest name
  const handleNameSubmit = async (e) => {
    e.preventDefault();
    if (!guestName.trim()) {
      setError('Please enter your name');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch(
        `http://localhost:8080/api/guest/session/${sessionId}/name`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ guestName })
        }
      );

      if (!response.ok) {
        setError('Failed to set name');
        return;
      }

      setStage('main');
      loadQueue();
    } catch (err) {
      setError('Connection error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Load queue
  const loadQueue = async () => {
    try {
      const response = await fetch(
        `http://localhost:8080/api/guest/events/${eventId}/queue`
      );
      const data = await response.json();
      setQueue(data);
    } catch (err) {
      console.error('Queue load error:', err);
    }
  };

  // Search songs
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8080/api/guest/songs/search?query=${encodeURIComponent(
          searchQuery
        )}&eventId=${eventId}`
      );
      const data = await response.json();
      setSearchResults(data);
    } catch (err) {
      setError('Search error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Add song request
  const handleAddRequest = async (songId, title) => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8080/api/guest/events/${eventId}/requests`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            songId,
            guestName,
            guestSessionId: sessionId
          })
        }
      );

      const data = await response.json();
      if (!response.ok) {
        setError(data.error || 'Failed to add request');
        return;
      }

      setError('');
      setSearchQuery('');
      setSearchResults([]);
      loadQueue();
    } catch (err) {
      setError('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Vote for song
  const handleVote = async (wishId) => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8080/api/guest/requests/${wishId}/vote`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ guestSessionId: sessionId })
        }
      );

      const data = await response.json();
      if (!response.ok) {
        setError(data.error || 'Failed to vote');
        return;
      }

      setError('');
      loadQueue();
    } catch (err) {
      setError('Vote error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Periodically reload queue
  useEffect(() => {
    if (stage === 'main') {
      loadQueue();
      const interval = setInterval(loadQueue, 5000);
      return () => clearInterval(interval);
    }
  }, [stage, eventId]);

  return (
    <div className="guest-page">
      {/* QR Entry Stage */}
      {stage === 'qr-entry' && (
        <div className="stage qr-entry-stage">
          <div className="stage-card">
            <h1>🎵 Musikwunsch Guest</h1>
            <p>Scan the QR code or enter the code from your DJ</p>

            <form onSubmit={handleQRSubmit}>
              <input
                type="text"
                placeholder="Enter QR code or event code"
                value={qrCode}
                onChange={(e) => setQrCode(e.target.value.toUpperCase())}
                autoFocus
              />
              <button type="submit" disabled={loading}>
                {loading ? 'Validating...' : 'Enter Event'}
              </button>
            </form>

            {error && <div className="error-message">{error}</div>}
          </div>
        </div>
      )}

      {/* Name Entry Stage */}
      {stage === 'name-entry' && (
        <div className="stage name-entry-stage">
          <div className="stage-card">
            <h2>Welcome to {eventName}</h2>
            <p>Please enter your name</p>

            <form onSubmit={handleNameSubmit}>
              <input
                type="text"
                placeholder="Your name"
                value={guestName}
                onChange={(e) => setGuestName(e.target.value)}
                autoFocus
              />
              <button type="submit" disabled={loading}>
                {loading ? 'Entering...' : 'Continue'}
              </button>
            </form>

            {error && <div className="error-message">{error}</div>}
          </div>
        </div>
      )}

      {/* Main Guest App */}
      {stage === 'main' && (
        <div className="stage main-stage">
          <div className="guest-header">
            <h1>{eventName}</h1>
            <p>Welcome, {guestName}!</p>
          </div>

          <div className="guest-container">
            {/* Search Section */}
            <div className="section search-section">
              <h3>Search Songs</h3>
              <form onSubmit={handleSearch}>
                <input
                  type="text"
                  placeholder="Search by title or artist..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
                <button type="submit" disabled={loading}>
                  {loading ? 'Searching...' : 'Search'}
                </button>
              </form>

              {error && <div className="error-message">{error}</div>}

              {searchResults.length > 0 && (
                <div className="search-results">
                  {searchResults.map((song) => (
                    <div key={song.id} className="song-item search-result">
                      <div className="song-info">
                        <strong>{song.title}</strong>
                        <p>{song.artist}</p>
                        {song.duration && <span className="duration">{Math.round(song.duration / 60)}min</span>}
                      </div>
                      <button
                        onClick={() => handleAddRequest(song.id, song.title)}
                        disabled={loading}
                      >
                        +
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Queue Section */}
            <div className="section queue-section">
              <h3>Queue ({queue.length})</h3>
              {queue.length === 0 ? (
                <p className="empty-queue">No songs requested yet</p>
              ) : (
                <div className="queue-list">
                  {queue.map((item, index) => (
                    <div key={item.id} className="queue-item">
                      <div className="rank">{index + 1}</div>
                      <div className="song-info">
                        <strong>{item.title}</strong>
                        <p>{item.artist}</p>
                        <small>by {item.guest_name}</small>
                      </div>
                      <div className="votes">
                        <span className="vote-count">{item.vote_count} votes</span>
                        <button
                          onClick={() => handleVote(item.id)}
                          className="vote-btn"
                          disabled={loading}
                        >
                          👍
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GuestPage;
