import React, { useState, useEffect, useRef, useContext } from 'react';
import { useParams } from 'react-router-dom';
import BpmnViewer from 'bpmn-js/lib/NavigatedViewer';
import './DiagramDetails.css';
import { LanguageContext } from '../../contexts/language';

const DiagramDetails = () => {
  const { id } = useParams();
  const [view, setView] = useState('diagram');
  const diagramContainerRef = useRef(null);

  const { currentLanguage } = useContext(LanguageContext);

  const content = currentLanguage === 'en' ? {
    viewDiagram: 'View Diagram',
    viewVerifiedDiagram: 'View Verified Diagram',
    viewReport: 'Download Report'
  } : {
    viewDiagram: 'Voir le diagramme',
    viewVerifiedDiagram: 'Voir le diagramme vérifié',
    viewReport: 'Télécharger le rapport'
  };

  const diagramPath = `http://127.0.0.1:8000/media/3diagrams_example/${id}/Processus.bpmn`;
  const verifiedDiagramPath = `http://127.0.0.1:8000/media/3diagrams_example/${id}/verified_diagram.bpmn`;
  const reportPath = `http://127.0.0.1:8000/media/3diagrams_example/${id}/report.docx`;

  useEffect(() => {
    let viewer;

    const renderDiagram = async (diagramPath) => {
      if (viewer) {
        viewer.destroy();
      }
      viewer = new BpmnViewer({ container: diagramContainerRef.current });
      const response = await fetch(diagramPath);
      const diagramXML = await response.text();
      try {
        await viewer.importXML(diagramXML);
        viewer.get('canvas').zoom('fit-viewport');
      } catch (err) {
        console.error('could not render BPMN diagram', err);
      }
    };

    if (view === 'diagram') {
      renderDiagram(diagramPath);
    } else if (view === 'verified') {
      renderDiagram(verifiedDiagramPath);
    }

    return () => {
      if (viewer) {
        viewer.destroy();
      }
    };
  }, [view, diagramPath, verifiedDiagramPath]);

  return (
    <div className="diagram-details">
      <div className="diagram-buttons">
        <button onClick={() => setView('diagram')}><b>{content.viewDiagram}</b> </button>
        <button onClick={() => setView('verified')}><b>{content.viewVerifiedDiagram}</b></button>
        <button onClick={() => setView('report')}><b>{content.viewReport}</b></button>
      </div>
      <div className="diagram-content">
        {(view === 'diagram' || view === 'verified') && (
          <div ref={diagramContainerRef} className="diagram-container"></div>
        )}
        {view === 'report' && <iframe src={reportPath} title="Report" />}
      </div>
    </div>
  );
}

export default DiagramDetails;
