import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import ProjectCard from './ProjectCard'; // Import the ProjectCard component
import './CardAndPage.css';
import CreateProjectForm from './CreateProjectForm';
import { LanguageContext } from '../../contexts/language';


const ProjectListPage = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { currentLanguage } = useContext(LanguageContext);

  const content = currentLanguage === 'en' ? {
    my: 'My Projects',
    loading: 'Loading....',
    noproject: 'No projects found.'
  } : {
    my: 'Mes Projets',
    loading: 'Chargement....',
    noproject: 'Aucun projet trouvé.'
  };

  const fetchProjects = async () => {
    setLoading(true);
    try {
        const accessToken = localStorage.getItem('access');
        if (!accessToken) {
            throw new Error('Access token not found.');
        }

        const response = await axios.get('http://127.0.0.1:8000/api/projects/', {
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        });
        setProjects(response.data);
    } catch (error) {
        setError(error.message || 'Failed to fetch projects.');
    }
    setLoading(false);
};

  useEffect(() => {
   
    fetchProjects();
  }, []);

  return (
    <div className='project-list-page'>
      
      <h2>{content.my}</h2>
      <div id='my-projects' className='projects-grid'>
        {loading && <p>{content.loading}</p>}
        {error && <p>{error}</p>}
        {projects.length === 0 && !loading && <p>{content.noproject}</p>}
        {projects.length > 0 && (
          <div className='project-cards'>
            {projects.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
        )}
      </div>
      <div id='create-project' className='formulaire'><CreateProjectForm fetchProjects={fetchProjects} /></div>
      
    </div>
  );
};

export default ProjectListPage;
