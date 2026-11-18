import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import api from '../../api';
import './CreateProjectForm.css';

/** Form to create a project. `onCreated` is called after success (reloads the list). */
const CreateProjectForm = ({ onCreated }) => {
  const { t } = useTranslation();
  const [form, setForm] = useState({ name: '', description: '' });
  const [error, setError] = useState('');

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await api.post('/api/projects/', form);
      setForm({ name: '', description: '' });
      if (onCreated) onCreated();
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    }
  };

  return (
    <div className="create-project">
      <h3>{t('projects.createTitle')}</h3>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="name">{t('projects.nameLabel')}</label>
          <input type="text" id="name" name="name" value={form.name}
            onChange={handleChange} required autoComplete="off" />
        </div>
        <div>
          <label htmlFor="description">{t('projects.descriptionLabel')}</label>
          <textarea id="description" name="description" value={form.description}
            onChange={handleChange} required autoComplete="off" />
        </div>
        {error && <span className="error">{error}</span>}
        <button type="submit">{t('projects.submit')}</button>
      </form>
    </div>
  );
};

export default CreateProjectForm;