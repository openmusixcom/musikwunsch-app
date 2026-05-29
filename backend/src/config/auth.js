import jwt from 'jsonwebtoken';
import bcryptjs from 'bcryptjs';

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';
const JWT_EXPIRY = process.env.JWT_EXPIRY || '24h';
const REFRESH_TOKEN_EXPIRY = process.env.REFRESH_TOKEN_EXPIRY || '7d';

// Hash password
export const hashPassword = async (password) => {
  return bcryptjs.hash(password, 10);
};

// Compare password
export const comparePassword = async (password, hash) => {
  return bcryptjs.compare(password, hash);
};

// Generate JWT
export const generateToken = (payload) => {
  return jwt.sign(payload, JWT_SECRET, { expiresIn: JWT_EXPIRY });
};

// Generate Refresh Token
export const generateRefreshToken = (payload) => {
  return jwt.sign(payload, JWT_SECRET + 'refresh', { expiresIn: REFRESH_TOKEN_EXPIRY });
};

// Verify JWT
export const verifyToken = (token) => {
  try {
    return jwt.verify(token, JWT_SECRET);
  } catch (error) {
    return null;
  }
};

// Verify Refresh Token
export const verifyRefreshToken = (token) => {
  try {
    return jwt.verify(token, JWT_SECRET + 'refresh');
  } catch (error) {
    return null;
  }
};
