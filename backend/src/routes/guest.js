import express from 'express';
import * as guestController from '../controllers/guestController.js';
import * as wishController from '../controllers/wishController.js';
import * as eventController from '../controllers/eventController.js';
import { verifyToken } from '../middleware/auth.js';

const router = express.Router();

// QR Code validation (no auth required)
router.post('/qr/validate', guestController.validateQRCode);

// Guest session routes (no auth required)
router.get('/session/:sessionId', guestController.validateSession);
router.put('/session/:sessionId/name', guestController.updateSessionName);
router.delete('/session/:sessionId', guestController.endSession);

// Event queue (no auth required)
router.get('/events/:eventId/queue', guestController.getEventQueue);

// Song search (no auth required)
router.get('/songs/search', wishController.searchSongs);

// Song request routes (no auth required)
router.post('/events/:eventId/requests', wishController.addSongRequest);
router.get('/requests/:wishId', wishController.getWishDetails);
router.delete('/requests/:wishId', wishController.removeSongRequest);

// Voting (no auth required)
router.post('/requests/:wishId/vote', wishController.voteForSong);

// DJ/Admin routes (require authentication)
router.post('/events', verifyToken, eventController.createEvent);
router.get('/events', verifyToken, eventController.listEvents);
router.get('/events/:eventId', verifyToken, eventController.getEventDetails);
router.put('/events/:eventId/status', verifyToken, eventController.updateEventStatus);
router.get('/events/:eventId/qr', verifyToken, eventController.generateQRCode);

export default router;
