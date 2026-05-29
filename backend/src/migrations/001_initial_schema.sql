-- Users table (Admin + DJ)
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'dj')),
  brand_color VARCHAR(7) DEFAULT '#FF6B35',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- Events table
CREATE TABLE IF NOT EXISTS events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  dj_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  qr_code VARCHAR(50) UNIQUE NOT NULL,
  pin VARCHAR(10),
  status VARCHAR(50) NOT NULL CHECK (status IN ('draft', 'active', 'paused', 'completed')) DEFAULT 'draft',
  license_type VARCHAR(50) NOT NULL CHECK (license_type IN ('free', 'event', 'time')) DEFAULT 'free',
  license_expires_at TIMESTAMP,
  guest_limit INT DEFAULT 10,
  active_guests_count INT DEFAULT 0,
  now_playing_id UUID,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_events_dj_id ON events(dj_id);
CREATE INDEX idx_events_qr_code ON events(qr_code);
CREATE INDEX idx_events_status ON events(status);

-- Songs table (lokale Musikbibliothek)
CREATE TABLE IF NOT EXISTS songs (
  id BIGSERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  artist VARCHAR(255) NOT NULL,
  album VARCHAR(255),
  duration INT,
  genre VARCHAR(100),
  search_vector TSVECTOR,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_songs_title ON songs USING GIN(to_tsvector('german', title));
CREATE INDEX idx_songs_artist ON songs USING GIN(to_tsvector('german', artist));

-- Wishes table
CREATE TABLE IF NOT EXISTS wishes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
  song_id BIGINT REFERENCES songs(id),
  guest_name VARCHAR(255),
  guest_session_id VARCHAR(255),
  status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'approved', 'playing', 'played', 'declined')) DEFAULT 'pending',
  vote_count INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_wishes_event_id ON wishes(event_id);
CREATE INDEX idx_wishes_status ON wishes(status);
CREATE INDEX idx_wishes_guest_session_id ON wishes(guest_session_id);

-- Votes table
CREATE TABLE IF NOT EXISTS votes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  wish_id UUID NOT NULL REFERENCES wishes(id) ON DELETE CASCADE,
  guest_session_id VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(wish_id, guest_session_id)
);

CREATE INDEX idx_votes_wish_id ON votes(wish_id);

-- Licenses table
CREATE TABLE IF NOT EXISTS licenses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id UUID REFERENCES events(id) ON DELETE CASCADE,
  type VARCHAR(50) NOT NULL CHECK (type IN ('free', 'event', 'time')),
  price DECIMAL(10, 2),
  starts_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_licenses_event_id ON licenses(event_id);

-- Payments table
CREATE TABLE IF NOT EXISTS payments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  dj_id UUID NOT NULL REFERENCES users(id),
  license_id UUID NOT NULL REFERENCES licenses(id),
  paypal_order_id VARCHAR(255) UNIQUE,
  status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'completed', 'failed', 'refunded')) DEFAULT 'pending',
  amount DECIMAL(10, 2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_payments_dj_id ON payments(dj_id);
CREATE INDEX idx_payments_status ON payments(status);
