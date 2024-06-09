import React, { useState,useEffect, useContext, useRef } from 'react';
import axios from 'axios';
import './CardAndPage.css';
import { LanguageContext } from '../../contexts/language';
import { Link } from 'react-router-dom';
import { FaEllipsisV } from 'react-icons/fa';

const ProjectCard = ({ project, onProjectUpdated, onProjectDeleted }) => {
  const { currentLanguage } = useContext(LanguageContext);
  const [isEditing, setIsEditing] = useState(false);
  const [editFormData, setEditFormData] = useState({
    name: project.name,
    description: project.description,
    owner: project.owner // Add the owner field
  });
  const [menuOpen, setMenuOpen] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const menuRef = useRef(null);

  const handleEditChange = (e) => {
    setEditFormData({ ...editFormData, [e.target.name]: e.target.value });
  };

  const handleUpdate = async () => {
    const accessToken = localStorage.getItem('access');
    if (!accessToken) {
      console.error('Access token not found.');
      return;
    }

    console.log('Updating project with data:', editFormData);

    try {
      const response = await axios.put(`http://127.0.0.1:8000/api/projects/${project.id}/`, editFormData, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      setIsEditing(false);
      onProjectUpdated(response.data);
    } catch (error) {
      console.error('Failed to update project:', error.response.data);
    }
  };

  const handleDelete = async () => {
    setShowDeleteModal(true);
  };

  const confirmDelete = () => {
    const accessToken = localStorage.getItem('access');
    if (!accessToken) {
      console.error('Access token not found.');
      return;
    }

    try {
      axios.delete(`http://127.0.0.1:8000/api/projects/${project.id}/`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      onProjectDeleted(project.id);
    } catch (error) {
      console.error('Failed to delete project:', error.message);
    }
    setShowDeleteModal(false);
  };

  const handleMenuToggle = () => {
    setMenuOpen(!menuOpen);
  };

  const handleClickOutside = (event) => {
    if (menuRef.current && !menuRef.current.contains(event.target)) {
      setMenuOpen(false);
    }

    if (!showDeleteModal) {
      return;
    }

    if (!event.target.closest('.modal-content')) {
      setShowDeleteModal(false);
    }
  };

  const handleCancelDelete = () => {
    setShowDeleteModal(false);
  };

  useEffect(() => {
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div className="project-card">
      {isEditing ? (
        <>
          <input
            type="text"
            name="name"
            value={editFormData.name}
            onChange={handleEditChange}
          />
          <textarea
            name="description"
            value={editFormData.description}
            onChange={handleEditChange}
          />
          <button onClick={handleUpdate}>
            {currentLanguage === 'en' ? 'Save' : 'Enregistrer'}
          </button>
          <button onClick={() => setIsEditing(false)}>
            {currentLanguage === 'en' ? 'Cancel' : 'Annuler'}
          </button>
        </>
      ) : (
        <>
          <div className="card-header">
            <h3 className="project__description">{project.name}</h3>
            <FaEllipsisV className="menu-icon" onClick={handleMenuToggle} />
            <div ref={menuRef} className={`menu ${menuOpen ? 'open' : ''}`}>
              <button onClick={() => setIsEditing(true)}>
                {currentLanguage === 'en' ? 'Edit' : 'Modifier'}
              </button>
              <button onClick={handleDelete}>
                {currentLanguage === 'en' ? 'Delete' : 'Supprimer'}
              </button>
            </div>
          </div>
          <p>{project.description}</p>
          <p className="diag_number">{currentLanguage === 'en' ? 'Number of Diagrams :' : 'Totale Diagrames :'} {project.num_diagrams}</p>
          <Link to={`/dashboard/project/${project.id}`} className="btn-details">
            {currentLanguage === 'en' ? 'Details' : 'Détails'}
          </Link>
        </>
      )}
      {showDeleteModal && (
        <div className="confirmation-modal">
          <div className="modal-content">
            <p>{currentLanguage === 'en' ? 'Are you sure you want to delete this project?' : 'Êtes-vous sûr de vouloir supprimer ce projet ?'}</p>
            <div className="modal-buttons">
              <button onClick={handleCancelDelete}>Cancel</button>
              <button onClick={confirmDelete}>Confirm</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectCard;
