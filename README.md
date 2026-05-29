# 🎵 Musikwunsch DJ App

Eine moderne Web-Anwendung für musikgesteuerte Partyplanung. Gäste können Musikwünsche einreichen und dafür abstimmen, während der DJ alle Wünsche über ein Dashboard verwaltet.

## 📋 Projekt-Struktur

```
musikwunsch-app/
├── backend/              # Express.js + Node.js
│   ├── src/
│   │   ├── server.js    # Express Server
│   │   ├── routes/      # API Routes
│   │   ├── controllers/ # Business Logic
│   │   ├── models/      # Data Models
│   │   ├── middleware/  # Auth, etc.
│   │   ├── config/      # DB, Auth Config
│   │   └── migrations/  # DB Migrations
│   ├── package.json
│   ├── .env             # Environment Variables
│   └── .env.example
│
├── frontend/            # React + Vite
│   ├── src/
│   │   ├── pages/       # Route Pages
│   │   ├── components/  # UI Components
│   │   ├── hooks/       # Custom Hooks
│   │   ├── services/    # API Services
│   │   ├── store/       # State Management
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### Voraussetzungen

- Node.js 18+
- PostgreSQL 14+
- npm oder yarn

### 1. PostgreSQL Setup

```bash
# PostgreSQL starten (lokal oder Docker)
psql -U postgres

# Datenbank erstellen
CREATE DATABASE musikwunsch;
```

### 2. Backend Setup

```bash
cd backend
npm install

# Migrations durchführen
npm run migrate

# Server starten
npm run dev
```

Server läuft auf: `http://localhost:3000`

### 3. Frontend Setup

```bash
cd frontend
npm install

# Dev Server starten
npm run dev
```

App läuft auf: `http://localhost:5173`

## 📚 API Endpoints

### Auth
- `POST /api/auth/register` - Neues Konto erstellen
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Token erneuern

### Health Check
- `GET /api/health` - Server Status prüfen

## 🔐 Test-Accounts

```
Admin:
Email: admin@test.local
Password: admin123
Role: admin

DJ:
Email: dj@test.local
Password: dj123
Role: dj
```

## 📅 Implementation Plan

**Phase 1** (Wochen 1-3): ✅ Grundlagen, DB, Auth
- [x] Projekt-Struktur
- [x] PostgreSQL Setup
- [x] Auth System (Register, Login, JWT)
- [x] Backend Skeleton
- [x] Frontend Router & Pages

**Phase 2** (Wochen 4-6): Gäste-App
- [ ] Event-Zugang (QR-Code + PIN)
- [ ] Musiksuche
- [ ] Wünsche hinzufügen
- [ ] Voting System
- [ ] Offline-Modus

**Phase 3** (Wochen 7-9): DJ-Dashboard
- [ ] Wunschlisten-Verwaltung
- [ ] Status-Kontrolle
- [ ] Suche & Filter
- [ ] Event-Statistiken

**Phase 4** (Wochen 10-11): Echtzeit & Offline
- [ ] WebSocket/Socket.io
- [ ] Service Worker
- [ ] Push Notifications

**Phase 5** (Wochen 12-13): PayPal & Admin
- [ ] PayPal Integration
- [ ] Lizenzsystem
- [ ] Admin-Panel

**Phase 6** (Wochen 14-15): Testing & Deploy
- [ ] Tests schreiben
- [ ] Security Audit
- [ ] Hostinger Deployment

## 🔗 Weitere Ressourcen

- [Spezifikation](./MUSIKWUNSCH_SPEZIFIKATION.docx)
- [Tech-Stack](#tech-stack)

## 💻 Tech-Stack

- **Frontend**: React 18, Vite, React Router
- **Backend**: Express.js, Node.js
- **Database**: PostgreSQL
- **Auth**: JWT, bcryptjs
- **Echtzeit**: Socket.io
- **Hosting**: Hostinger VPS

## 📝 Lizenz

MIT

---

**Status**: Phase 1 - Grundlagen ✅
