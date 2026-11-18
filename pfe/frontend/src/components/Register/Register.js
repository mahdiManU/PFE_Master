import { useState } from 'react';
import axios from 'axios';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { API_BASE_URL } from '../../config';
import '../Login/Login.css';

const EMPTY = { first_name: '', last_name: '', email: '', password: '', re_password: '' };

/** Public sign-up form (Djoser: POST /api/v1/auth/users/). */
const Register = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (form.password !== form.re_password) return setError(t('register.mismatch'));
    setLoading(true);
    try {
      await axios.post(`${API_BASE_URL}/api/v1/auth/users/`, form);
      navigate('/login', { state: { registered: true } });
    } catch (err) {
      const data = err.response?.data;
      setError(data && typeof data === 'object'
        ? Object.values(data).flat().join(' ')
        : t('register.error'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login">
      <h2>{t('register.title')}</h2>
      <form onSubmit={handleSubmit}>
        {error && <span className="error">{error}</span>}
        <label htmlFor="first_name">{t('register.firstName')}</label>
        <input id="first_name" name="first_name" value={form.first_name} onChange={handleChange} required />
        <label htmlFor="last_name">{t('register.lastName')}</label>
        <input id="last_name" name="last_name" value={form.last_name} onChange={handleChange} required />
        <label htmlFor="email">{t('login.email')}</label>
        <input id="email" type="email" name="email" value={form.email} onChange={handleChange} required />
        <label htmlFor="password">{t('login.password')}</label>
        <input id="password" type="password" name="password" value={form.password}
          onChange={handleChange} required autoComplete="new-password" />
        <label htmlFor="re_password">{t('register.confirmPassword')}</label>
        <input id="re_password" type="password" name="re_password" value={form.re_password}
          onChange={handleChange} required autoComplete="new-password" />
        <button type="submit" disabled={loading}>
          {loading ? t('common.loading') : t('register.submit')}
        </button>
      </form>
      <p style={{ marginTop: '1em' }}>
        {t('register.haveAccount')} <Link to="/login" className="link">{t('login.signIn')}</Link>
      </p>
    </div>
  );
};

export default Register;