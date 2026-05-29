import { Pool } from 'pg';
import crypto from 'crypto';

const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
});

// Generate guest session ID (short code like ABCD1234)
const generateSessionId = () => {
  return crypto.randomBytes(4).toString('hex').toUpperCase().slice(0, 8);
};

export const validateQRCode = async (req, res) => {
  try {
    const { qrCode, eventId } = req.body;

    if (!qrCode || !eventId) {
      return res.status(400).json({ error: 'QR code and event ID required' });
    }

    // Check if event exists and is active
    const eventResult = await pool.query(
      'SELECT * FROM events WHERE id = $1 AND qr_code = $2',
      [eventId, qrCode]
    );

    if (eventResult.rows.length === 0) {
      return res.status(404).json({ error: 'Invalid QR code or event' });
    }

    const event = eventResult.rows[0];

    if (event.status !== 'active') {
      return res.status(403).json({ error: 'Event is not active' });
    }

    if (event.active_guests_count >= event.guest_limit) {
      return res.status(403).json({ error: 'Event is full' });
    }

    // Create guest session (valid for 24 hours)
    const sessionId = generateSessionId();
    const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000);

    await pool.query(
      'INSERT INTO guest_sessions (id, event_id, ip_address, expires_at) VALUES ($1, $2, $3, $4)',
      [sessionId, eventId, req.ip, expiresAt]
    );

    // Update active guest count
    await pool.query(
      'UPDATE events SET active_guests_count = active_guests_count + 1 WHERE id = $1',
      [eventId]
    );

    res.json({
      sessionId,
      eventId,
      eventName: event.name,
      expiresAt
    });
  } catch (error) {
    console.error('QR validation error:', error);
    res.status(500).json({ error: 'Failed to validate QR code' });
  }
};

export const validateSession = async (req, res) => {
  try {
    const { sessionId } = req.params;

    const result = await pool.query(
      'SELECT * FROM guest_sessions WHERE id = $1 AND expires_at > NOW()',
      [sessionId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Session expired or invalid' });
    }

    const session = result.rows[0];

    // Get event details
    const eventResult = await pool.query(
      'SELECT * FROM events WHERE id = $1',
      [session.event_id]
    );

    res.json({
      valid: true,
      sessionId,
      eventId: session.event_id,
      eventName: eventResult.rows[0].name,
      expiresAt: session.expires_at
    });
  } catch (error) {
    console.error('Session validation error:', error);
    res.status(500).json({ error: 'Failed to validate session' });
  }
};

export const updateSessionName = async (req, res) => {
  try {
    const { sessionId } = req.params;
    const { guestName } = req.body;

    if (!guestName) {
      return res.status(400).json({ error: 'Guest name is required' });
    }

    const result = await pool.query(
      'UPDATE guest_sessions SET guest_name = $1 WHERE id = $2 RETURNING *',
      [guestName, sessionId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Session not found' });
    }

    res.json(result.rows[0]);
  } catch (error) {
    console.error('Update session error:', error);
    res.status(500).json({ error: 'Failed to update session' });
  }
};

export const endSession = async (req, res) => {
  try {
    const { sessionId } = req.params;

    // Get event ID first
    const sessionResult = await pool.query(
      'SELECT event_id FROM guest_sessions WHERE id = $1',
      [sessionId]
    );

    if (sessionResult.rows.length === 0) {
      return res.status(404).json({ error: 'Session not found' });
    }

    const eventId = sessionResult.rows[0].event_id;

    // Delete session
    await pool.query(
      'DELETE FROM guest_sessions WHERE id = $1',
      [sessionId]
    );

    // Decrease active guest count
    await pool.query(
      'UPDATE events SET active_guests_count = GREATEST(0, active_guests_count - 1) WHERE id = $1',
      [eventId]
    );

    res.json({ success: true });
  } catch (error) {
    console.error('End session error:', error);
    res.status(500).json({ error: 'Failed to end session' });
  }
};

export const getEventQueue = async (req, res) => {
  try {
    const { eventId } = req.params;

    const result = await pool.query(
      `SELECT w.*, s.title, s.artist, s.duration,
              (SELECT COUNT(*) FROM votes WHERE wish_id = w.id) as vote_count
       FROM wishes w
       LEFT JOIN songs s ON w.song_id = s.id
       WHERE w.event_id = $1 AND w.status IN ('pending', 'approved', 'playing')
       ORDER BY w.vote_count DESC, w.created_at ASC`,
      [eventId]
    );

    res.json(result.rows);
  } catch (error) {
    console.error('Get queue error:', error);
    res.status(500).json({ error: 'Failed to get queue' });
  }
};
