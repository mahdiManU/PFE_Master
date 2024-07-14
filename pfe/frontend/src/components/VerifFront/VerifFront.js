import React, { useState, useEffect, useContext } from 'react';
import './VerifFront.css';
import BpmnViewer from 'bpmn-js';
import { useParams, Link } from 'react-router-dom'; // Import Link from react-router-dom
import { LanguageContext } from '../../contexts/language';

const VerifFront = () => {
    const { currentLanguage } = useContext(LanguageContext);
    const { projectId, diagramId } = useParams();
    const [diagramUrl, setDiagramUrl] = useState(null);
    const [annotations, setAnnotations] = useState({
        missingInformation: [],
        structuralErrors: [],
        contradictory: [],
    });
    const [loading, setLoading] = useState(true);
    const [verifyClicked, setVerifyClicked] = useState(false);
    const [uploadedFile, setUploadedFile] = useState(null);
    const [isUploaded, setIsUploaded] = useState(false); // Track if the diagram is uploaded
    const [reportUrl, setReportUrl] = useState(null);

    const content = currentLanguage === 'en' ? {
        upload: "Upload",
        verify: "Verify",
        results: "Results",
        back: "Back",
        report: "Download Report",
        mi: "Missing Information:",
        s: "Structural Errors:",
        c: "Contradictory:",
        noErrors: "No errors found"
    } : {
        upload: "Importer",
        verify: "Vérifier",
        results: "Résultats",
        back: "Retour",
        report: "Télécharger Rapport",
        mi: "Informations manquantes :",
        s: "Erreurs Structurelles :",
        c: "Contradictions :",
        noErrors: "Pas d'erreur"
    };

    useEffect(() => {
        const bpmnCssLink = document.createElement('link');
        bpmnCssLink.href = 'https://unpkg.com/bpmn-js@17.0.0/dist/assets/bpmn-js.css';
        bpmnCssLink.rel = 'stylesheet';
        document.head.appendChild(bpmnCssLink);

        const bpmnJsScript = document.createElement('script');
        bpmnJsScript.src = 'https://unpkg.com/bpmn-js@17.0.0/dist/bpmn-navigated-viewer.development.js';
        document.body.appendChild(bpmnJsScript);

        return () => {
            document.head.removeChild(bpmnCssLink);
            document.body.removeChild(bpmnJsScript);
        };
    }, []);

    useEffect(() => {
        const fetchDiagram = async () => {
            setLoading(true);
            try {
                const accessToken = localStorage.getItem('access');
                const response = await fetch(`http://127.0.0.1:8000/api/projects/${projectId}/diagrams/${diagramId}`, {
                    headers: {
                        Authorization: `Bearer ${accessToken}`,
                    },
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch diagram');
                }

                const data = await response.json();
                setDiagramUrl(data.file);
                setIsUploaded(false); // Set to false when diagram is fetched from database
                setLoading(false);
            } catch (error) {
                console.error('Error fetching diagram:', error);
                setLoading(false);
            }
        };

        if (projectId && diagramId) {
            fetchDiagram();
        }
    }, [projectId, diagramId]);

    useEffect(() => {
        if (diagramUrl) {
            const canvas = document.querySelector('#canvas');
            canvas.innerHTML = ''; 
            displayBPMNDiagram(diagramUrl);
        }
    }, [diagramUrl]);

    const handleVerifyDiagram = async () => {
        setVerifyClicked(true);
        setLoading(true);

        try {
            const accessToken = localStorage.getItem('access');
            let response;
            if (isUploaded) {
                // Verify uploaded diagram
                const formData = new FormData();
                formData.append('file', uploadedFile);

                response = await fetch(`http://127.0.0.1:8000/api/upload/verify/`, {
                    method: 'POST',
                    headers: {
                        Authorization: `Bearer ${accessToken}`,
                    },
                    body: formData,
                });
            } else {
                // Verify diagram from database
                response = await fetch(`http://127.0.0.1:8000/api/projects/${projectId}/diagrams/${diagramId}/verify/`, {
                    method: 'POST',
                    headers: {
                        Authorization: `Bearer ${accessToken}`,
                    },
                });
            }

            if (!response.ok) {
                throw new Error('Failed to verify diagram');
            }

            const data = await response.json();
            const canvas = document.querySelector('#canvas');
            canvas.innerHTML = ''; 
            displayBPMNDiagram('http://127.0.0.1:8000' + data.filename);
            setAnnotations(parseAnnotations(data.annotations));
            setReportUrl(data.report_url);
            setLoading(false);
        } catch (error) {
            console.error('Error verifying diagram:', error);
            setLoading(false);
        }
    };

    const handleFileUpload = (event) => {
        setVerifyClicked(false);
        const file = event.target.files[0];
        if (file) {
            setUploadedFile(file);
            setIsUploaded(true); // Set to true when a file is uploaded
            setAnnotations({ 
                missingInformation: [], 
                structuralErrors: [], 
                contradictory: [] 
            }); // Clear annotations
            const reader = new FileReader();
            reader.onload = (e) => {
                const xml = e.target.result;
                const canvas = document.querySelector('#canvas');
                canvas.innerHTML = '';
                displayBPMNDiagramFromXML(xml);
            };
            reader.readAsText(file);
        }
    };

    const parseAnnotations = (annotations) => {
        const parsedAnnotations = {
            missingInformation: [],
            structuralErrors: [],
            contradictory: [],
        };

        annotations.forEach(annotation => {
            const parts = annotation.split('#');
            const errorType = parts[0].split(' ')[1]; // "MI" or "S" or "C"
            const errorCode = parts[0].split(' ')[2]; // Error code like "1"

            if (errorType === 'MI') {
                parsedAnnotations.missingInformation.push(`MI ${errorCode}: ${parts[1].trim()}`);
            } else if (errorType === 'S') {
                parsedAnnotations.structuralErrors.push(`S ${errorCode}: ${parts[1].trim()}`);
            } else if (errorType === 'C') {
                parsedAnnotations.contradictory.push(`C ${errorCode}: ${parts[1].trim()}`);
            }
        });

        return parsedAnnotations;
    };

    const displayBPMNDiagram = (url) => {
        const bpmnViewer = new BpmnViewer({
            container: '#canvas',
        });

        const openDiagram = async (bpmnXML) => {
            try {
                await bpmnViewer.importXML(bpmnXML);
                const canvas = bpmnViewer.get('canvas');
                canvas.zoom('fit-viewport');
            } catch (err) {
                console.error('Could not import BPMN 2.0 diagram', err);
            }
        };

        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch BPMN diagram');
                }
                return response.text();
            })
            .then(bpmnXML => {
                openDiagram(bpmnXML);
            })
            .catch(error => {
                console.error('Error fetching BPMN diagram:', error);
            });
    };

    const displayBPMNDiagramFromXML = (xml) => {
        const bpmnViewer = new BpmnViewer({
            container: '#canvas',
        });

        const openDiagram = async (bpmnXML) => {
            try {
                await bpmnViewer.importXML(bpmnXML);
                const canvas = bpmnViewer.get('canvas');
                canvas.zoom('fit-viewport');
            } catch (err) {
                console.error('Could not import BPMN 2.0 diagram', err);
            }
        };

        openDiagram(xml);
    };

    return (
        <div className="project-details-container">
            <div className="header">
                <Link to={`/dashboard/project/${projectId}`} className="back-arrow">&larr; {content.back}</Link>
                <h2><i>LegProV : Legal Process Verification</i></h2>
                <div className="button-container">
                    <label htmlFor="file" className="custom-file-input">{content.upload} </label>
                    <input type="file" id="file" accept=".bpmn" name="document" className="file-input" onChange={handleFileUpload} />
                    <button onClick={handleVerifyDiagram}>{content.verify}</button>
                </div>
            </div>
            <div className="content">
                <div className="diagram-container">
                    <div id="canvas" className="canvas"></div>
                </div>
                <div className="sidebar">
    <h2>{content.results}</h2>
    {verifyClicked && !loading ? (
        <>
            <div className="result-item">
                <div className="color-square yellow"></div>
                <div>
                    <h5>{content.mi}</h5>
                    {annotations.missingInformation.length > 0 ? (
                        annotations.missingInformation.map((item, index) => (
                            <p key={index}>{item}</p>
                        ))
                    ) : (
                        <p>{content.noErrors}</p>
                    )}
                </div>
            </div>
            <div className="result-item">
                <div className="color-square red"></div>
                <div>
                    <h5>{content.s}</h5>
                    {annotations.structuralErrors.length > 0 ? (
                        annotations.structuralErrors.map((item, index) => (
                            <p key={index}>{item}</p>
                        ))
                    ) : (
                        <p>{content.noErrors}</p>
                    )}
                </div>
            </div>
            <div className="result-item">
                <div className="color-square purple"></div>
                <div>
                    <h5>{content.c}</h5>
                    {annotations.contradictory.length > 0 ? (
                        annotations.contradictory.map((item, index) => (
                            <p key={index}>{item}</p>
                        ))
                    ) : (
                        <p>{content.noErrors}</p>
                    )}
                </div>
            </div>
        </>
    ) : null}
</div>

            </div>
            {verifyClicked && !loading && (
                <div className="view-report-container">
                    <button className="view-report-btn" onClick={() => window.open(`http://127.0.0.1:8000${reportUrl}`, '_blank')}>
                        {content.report}
                    </button>
                </div>
            )}
        </div>
    );
};

export default VerifFront;
