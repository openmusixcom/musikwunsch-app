import { Pool } from 'pg';

const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
});

export const searchSongs = async (req, res) => {
  try {
    const { query, eventId } = req.query;

    if (!query) {
      return res.status(400).json({ error: 'Search query is required' });
    }

    if (!eventId) {
      return res.status(400).json({ error: 'Event ID is required' });
    }

    const result = await pool.query(
      `SELECT id, title, artist, album, duration
       FROM songs
       WHERE to_tsvector('german', title || ' ' || artist) @@ plainto_tsquery('german', $1)
       LIMIT 20`,
      [query]
    );

    res.json(result.rows);
  } catch (error) {
    console.error('Search error:', error);
    res.status(500).json({ error: 'Failed to search songs' });
  }
};

export const addSongRequest = async (req, res) => {
  try {
    const { eventId } = req.params;
    const { songId, guestName, guestSessionId } = req.body;

    if (!songId || !guestSessionId) {
      return res.status(400).json({ error: 'Song ID and session ID are required' });
    }

    // Verify event exists
    const eventCheck = await pool.query(
      'SELECT * FROM events WHERE id = $1',
      [eventId]
    );

    if (eventCheck.rows.length === 0) {
      return res.status(404).json({ error: 'Event not found' });
    }

    // Verify session is valid
    const sessionCheck = await pool.query(
      'SELECT * FROM guest_sessions WHERE id = $1 AND event_id = $2 AND expires_at > NOW()',
      [guestSessionId, eventId]
    );

    if (sessionCheck.rows.length === 0) {
      return res.status(403).json({ error: 'Invalid or expired session' });
    }

    // Check if guest already requested this song for this event
    const existingRequest = await pool.query(
      'SELECT * FROM wishes WHERE event_id = $1 AND song_id = $2 AND guest_session_id = $3',
      [eventId, songId, guestSessionId]
    );

    if (existingRequest.rows.length > 0) {
      return res.status(400).json({ error: 'You already requested this song' });
    }

    // Create wish/request
    const result = await pool.query(
      `INSERT INTO wishes (event_id, song_id, guest_name, guest_session_id, status)
       VALUES ($1, $2, $3, $4, 'pending')
       RETURNING id`,
      [eventId, songId, guestName || 'Guest', guestSessionId]
    );

    res.json({
      wishId: result.rows[0].id,
      status: 'pending',
      message: 'Song request added'
    });
  } catch (error) {
    console.error('Add request error:', error);
    res.status(500).json({ error: 'Failed to add song request' });
  }
};

export const voteForSong = async (req, res) => {
  try {
    const { wishId } = req.params;
    const { guestSessionId } = req.body;

    if (!guestSessionId) {
      return res.status(400).json({ error: 'Session ID is required' });
    }

    // Verify wish exists
    const wishCheck = await pool.query(
      'SELECT * FROM wishes WHERE id = $1',
      [wishId]
    );

    if (wishCheck.rows.length === 0) {
      return res.status(404).json({ error: 'Song request not found' });
    }

    // Check if guest already voted
    const existingVote = await pool.query(
      'SELECT * FROM votes WHERE wish_id = $1 AND guest_session_id = $2',
      [wishId, guestSessionId]
    );

    if (existingVote.rows.length > 0) {
      return res.status(400).json({ error: 'You already voted for this song' });
    }

    // Add vote
    await pool.query(
      'INSERT INTO votes (wish_id, guest_session_id) VALUES ($1, $2)',
      [wishId, guestSessionId]
    );

    // Update vote count
    const voteCount = await pool.query(
      'SELECT COUNT(*) as count FROM votes WHERE wish_id = $1',
      [wishId]
    );

    await pool.query(
      'UPDATE wishes SET vote_count = $1 WHERE id = $2',
      [parseInt(voteCount.rows[0].count), wishId]
    );

    res.json({
      voteCount: parseInt(voteCount.rows[0].count),
      message: 'Vote added'
    });
  } catch (error) {
    console.error('Vote error:', error);
    res.status(500).json({ error: 'Failed to vote' });
  }
};

export const removeSongRequest = async (req, res) => {
  try {
    const { wishId } = req.params;
    const { guestSessionId } = req.body;

    // Verify ownership
    const wishCheck = await pool.query(
      'SELECT * FROM wishes WHERE id = $1 AND guest_session_id = $2',
      [wishId, guestSessionId]
    );

    if (wishCheck.rows.length === 0) {
      return res.status(404).json({ error: 'Song request not found or unauthorized' });
    }

    // Delete wish and associated votes
    await pool.query('DELETE FROM votes WHERE wish_id = $1', [wishId]);
    await pool.query('DELETE FROM wishes WHERE id = $1', [wishId]);

    res.json({ success: true });
  } catch (error) {
    console.error('Remove request error:', error);
    res.status(500).json({ error: 'Failed to remove song request' });
  }
};

export const getWishDetails = async (req, res) => {
  try {
    const { wishId } = req.params;

    const result = await pool.query(
      `SELECT w.*, s.title, s.artist, s.album, s.duration,
              (SELECT COUNT(*) FROM votes WHERE wish_id = w.id) as vote_count
       FROM wishes w
       LEFT JOIN songs s ON w.song_id = s.id
       WHERE w.id = $1`,
      [wishId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Song request not found' });
    }

    res.json(result.rows[0]);
  } catch (error) {
    console.error('Get wish error:', error);
    res.status(500).json({ error: 'Failed to get song request details' });
  }
};
