import { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import api from '../../api';
import './UserManagement.css';

const EMPTY_FORM = { first_name: '', last_name: '', email: '', password: '', confirmPassword: '' };

/** Admin page: list, create and delete users (the backend allows admins only). */
const UserManagement = () => {
  const { t } = useTranslation();
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState('');

  const fetchUsers = useCallback(async () => {
    try {
      const { data } = await api.get('/api/users/');
      setUsers(data);
    } catch (e) {
      setError(t('users.error'));
    }
  }, [t]);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (form.password !== form.confirmPassword) return setError(t('users.passwordMismatch'));
    const { confirmPassword, ...payload } = form;
    try {
      await api.post('/api/users/', payload);
      setForm(EMPTY_FORM);
      fetchUsers();
    } catch (err) {
      const data = err.response?.data;
      setError(data ? Object.values(data).flat().join(' ') : t('users.error'));
    }
  };

  const deleteUser = async (id) => {
    if (!window.confirm(t('users.confirmDelete'))) return;
    try {
      await api.delete(`/api/users/${id}/`);
      setUsers((prev) => prev.filter((u) => u.id !== id));
    } catch (e) {
      setError(t('users.error'));
    }
  };

  return (
    <div className="container">
      <div className="main-body">
        <div className="user-list">
          <h1>{t('users.title')}</h1>
          {error && <p className="error">{error}</p>}
          <table className="user-table">
            <thead>
              <tr>
                <th>{t('users.email')}</th>
                <th>{t('users.firstName')}</th>
                <th>{t('users.lastName')}</th>
                <th>{t('users.projects')}</th>
                <th>{t('users.completed')}</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id}>
                  <td>{user.email}</td>
                  <td>{user.first_name}</td>
                  <td>{user.last_name}</td>
                  <td>{user.num_projects}</td>
                  <td>{user.num_completed_projects}</td>
                  <td>
                    <button className="action-button" onClick={() => deleteUser(user.id)}>
                      {t('common.delete')}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="create-user-form">
          <h2>{t('users.createNew')}</h2>
          <form onSubmit={handleSubmit}>
            <input type="text" name="first_name" placeholder={t('users.firstName')}
              value={form.first_name} onChange={handleChange} required />
            <input type="text" name="last_name" placeholder={t('users.lastName')}
              value={form.last_name} onChange={handleChange} required />
            <input type="email" name="email" placeholder={t('users.email')}
              value={form.email} onChange={handleChange} required />
            <input type="password" name="password" placeholder={t('users.password')}
              value={form.password} onChange={handleChange} required autoComplete="new-password" />
            <input type="password" name="confirmPassword" placeholder={t('users.confirmPassword')}
              value={form.confirmPassword} onChange={handleChange} required autoComplete="new-password" />
            <button type="submit">{t('users.create')}</button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default UserManagement;