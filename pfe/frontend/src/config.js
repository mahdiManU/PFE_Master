/**
 * config.js - the only place where the backend address is written.
 *
 * Development: the Django server runs on http://127.0.0.1:8000.
 * To use another server, create frontend/.env.local containing
 *     REACT_APP_API_BASE_URL=https://my-server.example.com
 * and restart `npm start`. No code change is needed.
 *
 * No trailing slash.
 */
export const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000";