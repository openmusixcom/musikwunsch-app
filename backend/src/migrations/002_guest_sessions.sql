-- Guest Sessions table for QR code access
CREATE TABLE IF NOT EXISTS guest_sessions (
  id VARCHAR(255) PRIMARY KEY,
  event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
  guest_name VARCHAR(255),
  ip_address VARCHAR(45),
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_guest_sessions_event_id ON guest_sessions(event_id);
CREATE INDEX idx_guest_sessions_expires_at ON guest_sessions(expires_at);

-- Guest session activity log
CREATE TABLE IF NOT EXISTS guest_session_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id VARCHAR(255) NOT NULL REFERENCES guest_sessions(id) ON DELETE CASCADE,
  action VARCHAR(100) NOT NULL,
  details JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_guest_session_logs_session_id ON guest_session_logs(session_id);
