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

// Links and contact details shown on the home page and in the footer.
export const THESIS_URL =
  'https://drive.google.com/file/d/1IBiMTWhAx35wgCvrkxI9Kne-wt94nL82/view?usp=sharing';
export const REPO_URL = 'https://github.com/mahdiManU/PFE_Master';
export const CONTACT_EMAIL = 'imenerabahi25@gmail.com';  