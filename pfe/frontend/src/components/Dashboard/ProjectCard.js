import { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { FaEllipsisV } from 'react-icons/fa';
import api from '../../api';
import './CardAndPage.css';

/** One project card with edit / delete menu. */
const ProjectCard = ({ project, onProjectUpdated, onProjectDeleted }) => {
  const { t } = useTranslation();
  const [isEditing, setIsEditing] = useState(false);
  const [form, setForm] = useState({ name: project.name, description: project.description });
  const [menuOpen, setMenuOpen] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const menuRef = useRef(null);

  // Close the menu when clicking elsewhere.
  useEffect(() => {
    const onClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) setMenuOpen(false);
    };
    document.addEventListener('mousedown', onClickOutside);
    return () => document.removeEventListener('mousedown', onClickOutside);
  }, []);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleUpdate = async () => {
    try {
      const { data } = await api.put(`/api/projects/${project.id}/`, form);
      setIsEditing(false);
      onProjectUpdated(data);
    } catch (e) {
      console.error('Failed to update project:', e.response?.data || e.message);
    }
  };

  const confirmDelete = async () => {
    try {
      await api.delete(`/api/projects/${project.id}/`);
      onProjectDeleted(project.id);
    } catch (e) {
      console.error('Failed to delete project:', e.message);
    }
    setShowDeleteModal(false);
  };

  return (
    <div className="project-card">
      {isEditing ? (
        <>
          <input type="text" name="name" value={form.name} onChange={handleChange} />
          <textarea name="description" value={form.description} onChange={handleChange} />
          <button onClick={handleUpdate}>{t('common.save')}</button>
          <button onClick={() => setIsEditing(false)}>{t('common.cancel')}</button>
        </>
      ) : (
        <>
          <div className="card-header">
            <h3 className="project__description">{project.name}</h3>
            <FaEllipsisV className="menu-icon" onClick={() => setMenuOpen(!menuOpen)} />
            <div ref={menuRef} className={`menu ${menuOpen ? 'open' : ''}`}>
              <button onClick={() => { setIsEditing(true); setMenuOpen(false); }}>{t('common.edit')}</button>
              <button onClick={() => { setShowDeleteModal(true); setMenuOpen(false); }}>{t('common.delete')}</button>
            </div>
          </div>
          <p>{project.description}</p>
          <p className="diag_number">{t('projects.diagramCount')} {project.num_diagrams}</p>
          <Link to={`/dashboard/project/${project.id}`} className="btn-details">
            {t('common.details')}
          </Link>
        </>
      )}

      {showDeleteModal && (
        <div className="confirmation-modal" onClick={() => setShowDeleteModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <p>{t('projects.confirmDelete')}</p>
            <div className="modal-buttons">
              <button onClick={() => setShowDeleteModal(false)}>{t('common.cancel')}</button>
              <button onClick={confirmDelete}>{t('common.confirm')}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectCard;