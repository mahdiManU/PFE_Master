import React, { useState, useEffect, useContext } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import './ProjectDetailsPage.css';
import { LanguageContext } from '../../contexts/language';

const ProjectDetailsPage = () => {
    const [diagrams, setDiagrams] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [newDiagram, setNewDiagram] = useState({ name: '', description: '', file: null });
    const { projectId } = useParams();
    const { currentLanguage } = useContext(LanguageContext);


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
        chooseFile: "Choose file"
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
        chooseFile: "Choisir un fichier"
    };

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
        } catch (error) {
            setError(error.message || content.failedToCreateDiagram);
        }
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
                                    </tr>
                                </thead>
                                <tbody>
                                    {diagrams.map((diagram) => (
                                        <tr key={diagram.id} className="diagram-item">
                                            <td>{diagram.name}</td>
                                            <td>{diagram.description}</td>
                                            <td>{diagram.verified ? '✔️' : '❌'}</td>
                                            <td><a href={diagram.file} target="_blank" rel="noopener noreferrer">{content.download}</a></td>
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
                                    onChange={(e) => setNewDiagram({ ...newDiagram, file: e.target.files[0] })}
                                    required
                                    autoComplete="off"
                                    aria-label={content.chooseFile}
                                />
                                <button type="submit">{content.create}</button>
                            </form>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ProjectDetailsPage;
