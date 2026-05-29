import express from 'express';
import * as guestController from '../controllers/guestController.js';
import * as wishController from '../controllers/wishController.js';
import * as eventController from '../controllers/eventController.js';
import { authMiddleware } from '../middleware/auth.js';

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
router.post('/events', authMiddleware, eventController.createEvent);
router.get('/events', authMiddleware, eventController.listEvents);
router.get('/events/:eventId', authMiddleware, eventController.getEventDetails);
router.put('/events/:eventId/status', authMiddleware, eventController.updateEventStatus);
router.get('/events/:eventId/qr', authMiddleware, eventController.generateQRCode);

export default router;
