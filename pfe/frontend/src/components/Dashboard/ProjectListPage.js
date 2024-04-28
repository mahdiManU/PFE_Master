import React, { useState, useEffect } from 'react';
import axios from 'axios';
import CreateProjectForm from './CreateProjectForm';
import ProjectCard from './ProjectCard'; // Import the ProjectCard component
import './CardAndPage.css';


const ProjectListPage = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
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

    fetchProjects();
  }, []);

  return (
    <div className='project-list-page'>
      <CreateProjectForm />
      <h2>Projects</h2>
      <div className='projects-grid'>
        {loading && <p>Loading...</p>}
        {error && <p>{error}</p>}
        {projects.length === 0 && !loading && <p>No projects found.</p>}
        {projects.length > 0 && (
          <div className='project-cards'>
            {projects.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProjectListPage;
