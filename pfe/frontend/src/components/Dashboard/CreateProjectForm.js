import React, { useState, useContext } from 'react';
import axios from 'axios';
import './CreateProjectForm.css'
import { useSelector} from 'react-redux'
import { LanguageContext } from '../../contexts/language';

const CreateProjectForm = ({ onSuccess,fetchProjects }) => {
  const [formData, setFormData] = useState({ name: '', description: '' });
  const [setError] = useState(null);
  const { userInfo } = useSelector((state) => state.auth)
  const { currentLanguage } = useContext(LanguageContext);

  const content = currentLanguage === 'en' ? {
    name: 'Name of Project :',
    description: 'Description :',
    create: 'Create a New Project',
    submit: 'Create Project'
  } : {
    name: 'Nom Du Projet :',
    description: 'Description :',
    create: 'Créer Un Nouveau Projet',
    submit: 'Crée Projet'
  };
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const createProject = async (projectData) => {
    try {
      const accessToken = localStorage.getItem('access');
      if (!accessToken) {
        throw new Error('Access token not found.');
      }
  
      // Include owner field in the projectData
      projectData.owner = userInfo.id;
      
      
      const response = await axios.post('http://127.0.0.1:8000/api/projects/', projectData, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
  
      return response.data;
    } catch (error) {
      setError(error.message || 'Failed to create project.');
      throw error;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const createdProject = await createProject(formData);
      console.log('Project created:', createdProject);
      fetchProjects();
      // Call the onSuccess callback if provided
      if (onSuccess) {
        onSuccess(createdProject);
      }
      // Clear the form fields after successful project creation
      setFormData({ name: '', description: '' });
    } catch (error) {
      console.error('Error creating project:', error);
      // You can handle errors (e.g., display an error message)
    }
  };

  return (
    <div className="create-project">
      <h3>{content.create}</h3>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="name">{content.name}</label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            autoComplete="off" 
          />
        </div>
        <div>
          <label htmlFor="description">{content.description}</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            required
            autoComplete="off" 
          />
        </div>
        <button type="submit">{content.submit}</button>
      </form>
    </div>
  );
};

export default CreateProjectForm;
