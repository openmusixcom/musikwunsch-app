import { Pool } from 'pg';
import crypto from 'crypto';

const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
});

export const createEvent = async (req, res) => {
  try {
    const { name, guestLimit = 50 } = req.body;
    const djId = req.user.id;

    if (!name) {
      return res.status(400).json({ error: 'Event name is required' });
    }

    // Generate unique QR code
    const qrCode = crypto.randomBytes(4).toString('hex').toUpperCase();

    const result = await pool.query(
      'INSERT INTO events (dj_id, name, qr_code, guest_limit, status) VALUES ($1, $2, $3, $4, $5) RETURNING *',
      [djId, name, qrCode, guestLimit, 'draft']
    );

    res.json({
      event: result.rows[0],
      qrCode
    });
  } catch (error) {
    console.error('Event creation error:', error);
    res.status(500).json({ error: 'Failed to create event' });
  }
};

export const getEventDetails = async (req, res) => {
  try {
    const { eventId } = req.params;

    const result = await pool.query(
      'SELECT * FROM events WHERE id = $1',
      [eventId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Event not found' });
    }

    res.json(result.rows[0]);
  } catch (error) {
    console.error('Get event error:', error);
    res.status(500).json({ error: 'Failed to get event' });
  }
};

export const generateQRCode = async (req, res) => {
  try {
    const { eventId } = req.params;

    const event = await pool.query(
      'SELECT * FROM events WHERE id = $1',
      [eventId]
    );

    if (event.rows.length === 0) {
      return res.status(404).json({ error: 'Event not found' });
    }

    // Return QR code data as JSON (frontend will render it)
    const qrData = {
      eventId,
      qrCode: event.rows[0].qr_code
    };

    res.json({
      qrData: JSON.stringify(qrData),
      qrCode: event.rows[0].qr_code,
      eventId,
      eventName: event.rows[0].name
    });
  } catch (error) {
    console.error('QR code generation error:', error);
    res.status(500).json({ error: 'Failed to generate QR code' });
  }
};

export const updateEventStatus = async (req, res) => {
  try {
    const { eventId } = req.params;
    const { status } = req.body;
    const djId = req.user.id;

    if (!['draft', 'active', 'paused', 'completed'].includes(status)) {
      return res.status(400).json({ error: 'Invalid status' });
    }

    const result = await pool.query(
      'UPDATE events SET status = $1 WHERE id = $2 AND dj_id = $3 RETURNING *',
      [status, eventId, djId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Event not found' });
    }

    res.json(result.rows[0]);
  } catch (error) {
    console.error('Update event error:', error);
    res.status(500).json({ error: 'Failed to update event' });
  }
};

export const listEvents = async (req, res) => {
  try {
    const djId = req.user.id;

    const result = await pool.query(
      'SELECT * FROM events WHERE dj_id = $1 ORDER BY created_at DESC',
      [djId]
    );

    res.json(result.rows);
  } catch (error) {
    console.error('List events error:', error);
    res.status(500).json({ error: 'Failed to list events' });
  }
};
