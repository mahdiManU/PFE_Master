import React, { useState, useEffect, useContext , useRef} from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './ProjectDetailsPage.css';
import { LanguageContext } from '../../contexts/language';


const ProjectDetailsPage = () => {
    const [diagrams, setDiagrams] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [newDiagram, setNewDiagram] = useState({ name: '', description: '', file: null });
    const [showModal, setShowModal] = useState(false);
    const [selectedDiagramId, setSelectedDiagramId] = useState(null);
    const { projectId } = useParams();
    const { currentLanguage } = useContext(LanguageContext);
    const [activeDropdown, setActiveDropdown] = useState(null);
    const navigate = useNavigate();
    const fileInputRef = useRef(null);


    const handleToggleDropdown = (diagramId) => {
        setActiveDropdown(activeDropdown === diagramId ? null : diagramId);
    };

    const content = currentLanguage === 'en' ? {
        diagrams: "Diagrams",
        name: "Name",
        description: "Description",
        verified: "Verified",
        file: "File",
        download: "Download",
        createNewDiagram: "Create a New Diagram",
        diagramName: "Diagram Name",
        diagramDescription: "Diagram Description",
        create: "Create Diagram",
        loadingDiagrams: "Loading diagrams...",
        errorFetchingDiagrams: "Error fetching diagrams.",
        failedToCreateDiagram: "Failed to create diagram.",
        pleaseSelectFile: "Please select a file.",
        chooseFile: "Choose file",
        delete: "Delete",
        update: "Update",
        actions: "Actions",
        confirmDelete: "Are you sure you want to delete this diagram?",
        cancel: "Cancel",
        confirm: "Confirm",
        view: "View"
    } : {
        diagrams: "Diagrammes",
        name: "Nom",
        description: "Description",
        verified: "Vérifié",
        file: "Fichier",
        download: "Télécharger",
        createNewDiagram: "Créer un nouveau diagramme",
        diagramName: "Nom du diagramme",
        diagramDescription: "Description du diagramme",
        create: "Créer Diagramme",
        loadingDiagrams: "Chargement des diagrammes...",
        errorFetchingDiagrams: "Erreur lors du chargement des diagrammes.",
        failedToCreateDiagram: "Échec de la création du diagramme.",
        pleaseSelectFile: "Veuillez sélectionner un fichier.",
        chooseFile: "Choisir un fichier",
        delete: "Supprimer",
        update: "Mettre à jour",
        actions: "Actions",
        confirmDelete: "Êtes-vous sûr de vouloir supprimer ce diagramme?",
        cancel: "Annuler",
        confirm: "Confirmer",
        view: "Voir"
    };

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (!event.target.closest('.dropdown')) {
                setActiveDropdown(null);
            }
        };
    
        document.addEventListener('mousedown', handleClickOutside);
    
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    const fetchDiagrams = async () => {
        setLoading(true);
        setError(null);

        try {
            const accessToken = localStorage.getItem('access');
            if (!accessToken) {
                throw new Error('Access token not found.');
            }

            const response = await axios.get(`http://127.0.0.1:8000/api/projects/${projectId}/diagrams`, {
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                },
            });

            setDiagrams(response.data);
        } catch (error) {
            setError(error.message || content.errorFetchingDiagrams);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDiagrams();
    }, [projectId]);

    const handleCreateDiagram = async (e) => {
        e.preventDefault();
        setError(null); // Reset error on new submission
    
        try {
            const accessToken = localStorage.getItem('access');
            if (!accessToken) {
                throw new Error('Access token not found.');
            }
    
            if (!newDiagram.file) {
                throw new Error(content.pleaseSelectFile);
            }
    
            const formData = new FormData();
            formData.append('name', newDiagram.name);
            formData.append('description', newDiagram.description);
            formData.append('file', newDiagram.file);
    
            const response = await axios.post(`http://127.0.0.1:8000/api/projects/${projectId}/create-diagrams/`, formData, {
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                    'Content-Type': 'multipart/form-data',
                },
            });
    
            setDiagrams([...diagrams, response.data]);
            setNewDiagram({ name: '', description: '', file: null });
            if (fileInputRef.current) {
                fileInputRef.current.value = ''; // Reset the file input value
            }
        } catch (error) {
            setError(error.message || content.failedToCreateDiagram);
        }
    };

    const handleDeleteDiagram = async (diagramId) => {
        try {
            const accessToken = localStorage.getItem('access');
            if (!accessToken) {
                throw new Error('Access token not found.');
            }

            await axios.delete(`http://127.0.0.1:8000/api/projects/${projectId}/diagrams/${diagramId}/`, {
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                },
            });

            setDiagrams(diagrams.filter(diagram => diagram.id !== diagramId));
        } catch (error) {
            setError(error.message || 'Failed to delete diagram.');
        }
    };

    const handleShowModal = (diagramId) => {
        setSelectedDiagramId(diagramId);
        setShowModal(true);
    };

    const handleCloseModal = () => {
        setShowModal(false);
        setSelectedDiagramId(null);
        setActiveDropdown(null);
    };

    const handleConfirmDelete = () => {
        if (selectedDiagramId) {
            handleDeleteDiagram(selectedDiagramId);
        }
        handleCloseModal();
    };

    const handleNavigateToVerification = (diagramId) => {
        navigate(`/dashboard/project/${projectId}/verify/${diagramId}`);
    };

    return (
        <div className="container">
            <div className="main-body">
                <div className="project-details">
                    {loading ? (
                        <p>{content.loadingDiagrams}</p>
                    ) : error ? (
                        <p>{error}</p>
                    ) : (
                        <div className="diagram-list">
                            <h3>{content.diagrams}:</h3>
                            <table className="diagram-table">
                                <thead>
                                    <tr>
                                        <th>{content.name}</th>
                                        <th>{content.description}</th>
                                        <th>{content.verified}</th>
                                        <th>{content.file}</th>
                                        <th></th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {diagrams.map((diagram) => (
                                        <tr key={diagram.id} className="diagram-item">
                                            <td>{diagram.name}</td>
                                            <td>{diagram.description}</td>
                                            <td>{diagram.verified ? '✔️' : '❌'}</td>
                                            <td><a href={`http://127.0.0.1:8000${diagram.file}`} target="_blank" rel="noopener noreferrer">{content.download}</a></td>
                                            <td>
                                                <div className="dropdown">
                                                    <button className="dropbtn" onClick={() => handleToggleDropdown(diagram.id)}>⋮</button>
                                                    {activeDropdown === diagram.id && (
                                                    <div className="dropdown-content">
                                                        <button onClick={() => handleShowModal(diagram.id)}>{content.delete}</button>
                                                        <button onClick={() => handleNavigateToVerification(diagram.id)}>{content.view}</button>
                                                    </div>
                                                    )}
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            <form onSubmit={handleCreateDiagram} className="create-diagram-form">
                                <h4>{content.createNewDiagram}</h4>
                                <input
                                    type="text"
                                    id="diagramName"
                                    placeholder={content.diagramName}
                                    value={newDiagram.name}
                                    onChange={(e) => setNewDiagram({ ...newDiagram, name: e.target.value })}
                                    required
                                    autoComplete="off"
                                />
                                <textarea
                                    id="diagramDescription"
                                    placeholder={content.diagramDescription}
                                    value={newDiagram.description}
                                    onChange={(e) => setNewDiagram({ ...newDiagram, description: e.target.value })}
                                    required
                                    autoComplete="off"
                                ></textarea>
                                <input
                                    type="file"
                                    id="diagramFile"
                                    accept=".bpmn"
                                    ref={fileInputRef} // Add this line
                                    onChange={(e) => setNewDiagram({ ...newDiagram, file: e.target.files[0] })}
                                    required
                                    autoComplete="off"
                                />
                                <button type="submit">{content.create}</button>
                            </form>
                        </div>
                    )}
                </div>
            </div>

            <div id="myModal" className={`modal ${showModal ? 'show' : ''}`} onClick={handleCloseModal}>
                <div className="modal-content" onClick={e => e.stopPropagation()}>
                    <span className="close" onClick={handleCloseModal}>&times;</span>
                    <p>{content.confirmDelete}</p>
                    <button className="button cancel" onClick={handleCloseModal}>{content.cancel}</button>
                    <button className="button confirm" onClick={handleConfirmDelete}>{content.confirm}</button>
                </div>
            </div>
        </div>
    );
};

export default ProjectDetailsPage;
