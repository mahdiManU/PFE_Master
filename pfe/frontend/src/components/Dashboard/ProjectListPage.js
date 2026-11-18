import { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import api from '../../api';
import ProjectCard from './ProjectCard';
import CreateProjectForm from './CreateProjectForm';
import './CardAndPage.css';
import { useLocation } from 'react-router-dom';

/** List of the user's projects plus the "new project" form. */
const ProjectListPage = () => {
  const { hash } = useLocation();
  const { t } = useTranslation();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchProjects = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const { data } = await api.get('/api/projects/');
      setProjects(data);
    } catch (e) {
      setError(t('projects.errorFetch'));
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => {
    if (!loading && hash) document.getElementById(hash.slice(1))?.scrollIntoView({ behavior: 'smooth' });
  }, [loading, hash]);

  useEffect(() => { fetchProjects(); }, [fetchProjects]);

  const handleUpdated = (updated) =>
    setProjects((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
  const handleDeleted = (id) =>
    setProjects((prev) => prev.filter((p) => p.id !== id));

  return (
    <div className="project-list-page">
      <h2>{t('projects.mine')}</h2>
      <div id="my-projects" className="projects-grid">
        {loading && <p>{t('common.loading')}</p>}
        {error && <p>{error}</p>}
        {!loading && !error && projects.length === 0 && <p>{t('projects.none')}</p>}
        {projects.length > 0 && (
          <div className="project-cards">
            {projects.map((project) => (
              <ProjectCard key={project.id} project={project}
                onProjectUpdated={handleUpdated} onProjectDeleted={handleDeleted} />
            ))}
          </div>
        )}
      </div>
      <div id="create-project" className="formulaire">
        <CreateProjectForm onCreated={fetchProjects} />
      </div>
    </div>
  );
};

export default ProjectListPage;