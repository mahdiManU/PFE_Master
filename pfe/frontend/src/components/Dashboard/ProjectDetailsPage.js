import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import api from '../../api';
import { API_BASE_URL } from '../../config';
import './ProjectDetailsPage.css';

/** One project: its diagrams (download, view/verify, delete) and the upload form. */
const ProjectDetailsPage = () => {
  const { t } = useTranslation();
  const { projectId } = useParams();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const [projectName, setProjectName] = useState('');
  const [diagrams, setDiagrams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [newDiagram, setNewDiagram] = useState({ name: '', description: '', file: null });
  const [activeDropdown, setActiveDropdown] = useState(null);
  const [diagramToDelete, setDiagramToDelete] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [project, list] = await Promise.all([
        api.get(`/api/projects/${projectId}/`),
        api.get(`/api/projects/${projectId}/diagrams/`),
      ]);
      setProjectName(project.data.name);
      setDiagrams(list.data);
    } catch (e) {
      setError(t('project.errorFetch'));
    } finally {
      setLoading(false);
    }
  }, [projectId, t]);

  useEffect(() => { load(); }, [load]);

  // Close the row menu when clicking elsewhere.
  useEffect(() => {
    const onClickOutside = (e) => {
      if (!e.target.closest('.dropdown')) setActiveDropdown(null);
    };
    document.addEventListener('mousedown', onClickOutside);
    return () => document.removeEventListener('mousedown', onClickOutside);
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setError('');
    if (!newDiagram.file) return setError(t('project.selectFile'));
    const formData = new FormData();
    formData.append('name', newDiagram.name);
    formData.append('description', newDiagram.description);
    formData.append('file', newDiagram.file);
    try {
      await api.post(`/api/projects/${projectId}/create-diagrams/`, formData);
      setNewDiagram({ name: '', description: '', file: null });
      if (fileInputRef.current) fileInputRef.current.value = '';
      load();
    } catch (err) {
      setError(t('project.errorCreate'));
    }
  };

  const confirmDelete = async () => {
    try {
      await api.delete(`/api/projects/${projectId}/diagrams/${diagramToDelete}/`);
      setDiagrams((prev) => prev.filter((d) => d.id !== diagramToDelete));
    } catch (err) {
      setError(t('project.errorDelete'));
    }
    setDiagramToDelete(null);
    setActiveDropdown(null);
  };

  return (
    <div className="container">
      <div className="main-body">
        <div className="project-details">
          <h2 className="project-name">{projectName}</h2>
          {loading ? (
            <p>{t('project.loading')}</p>
          ) : (
            <div className="diagram-list">
              {error && <p className="error">{error}</p>}
              <h3>{t('project.diagrams')}:</h3>
              <table className="diagram-table">
                <thead>
                  <tr>
                    <th>{t('project.name')}</th>
                    <th>{t('project.description')}</th>
                    <th>{t('project.verified')}</th>
                    <th>{t('project.file')}</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {diagrams.map((diagram) => (
                    <tr key={diagram.id} className="diagram-item">
                      <td>{diagram.name}</td>
                      <td>{diagram.description}</td>
                      <td>{diagram.verified ? '✔️' : '❌'}</td>
                      <td>
                        <a href={`${API_BASE_URL}${diagram.file}`} target="_blank" rel="noopener noreferrer">
                          {t('project.download')}
                        </a>
                      </td>
                      <td>
                        <div className="dropdown">
                          <button className="dropbtn"
                            onClick={() => setActiveDropdown(activeDropdown === diagram.id ? null : diagram.id)}>⋮</button>
                          {activeDropdown === diagram.id && (
                            <div className="dropdown-content">
                              <button onClick={() => setDiagramToDelete(diagram.id)}>{t('common.delete')}</button>
                              <button onClick={() => navigate(`/dashboard/project/${projectId}/verify/${diagram.id}`)}>
                                {t('common.view')}
                              </button>
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <form onSubmit={handleCreate} className="create-diagram-form">
                <h4>{t('project.createNew')}</h4>
                <input type="text" placeholder={t('project.diagramName')} value={newDiagram.name}
                  onChange={(e) => setNewDiagram({ ...newDiagram, name: e.target.value })}
                  required autoComplete="off" />
                <textarea placeholder={t('project.diagramDescription')} value={newDiagram.description}
                  onChange={(e) => setNewDiagram({ ...newDiagram, description: e.target.value })}
                  required autoComplete="off" />
                <input type="file" accept=".bpmn" ref={fileInputRef}
                  onChange={(e) => setNewDiagram({ ...newDiagram, file: e.target.files[0] })} required />
                <button type="submit">{t('project.create')}</button>
              </form>
            </div>
          )}
        </div>
      </div>

      <div className={`modal ${diagramToDelete ? 'show' : ''}`} onClick={() => setDiagramToDelete(null)}>
        <div className="modal-content" onClick={(e) => e.stopPropagation()}>
          <span className="close" onClick={() => setDiagramToDelete(null)}>&times;</span>
          <p>{t('project.confirmDelete')}</p>
          <button className="button cancel" onClick={() => setDiagramToDelete(null)}>{t('common.cancel')}</button>
          <button className="button confirm" onClick={confirmDelete}>{t('common.confirm')}</button>
        </div>
      </div>
    </div>
  );
};

export default ProjectDetailsPage;