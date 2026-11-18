/**
 * api.js - axios client for the Django backend.
 * Adds the JWT access token to every request. Use it instead of raw axios:
 *     import api from '../../api';
 *     const { data } = await api.get('/api/projects/');
 */
import axios from 'axios';
import { API_BASE_URL } from './config';

const api = axios.create({ baseURL: API_BASE_URL });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;