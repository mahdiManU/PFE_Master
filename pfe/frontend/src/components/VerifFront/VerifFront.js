import { useCallback, useEffect, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import NavigatedViewer from 'bpmn-js/lib/NavigatedViewer';
import 'bpmn-js/dist/assets/diagram-js.css';
import 'bpmn-js/dist/assets/bpmn-js.css';
import api from '../../api';
import { API_BASE_URL } from '../../config';
import './VerifFront.css';

const EMPTY = { missingInformation: [], structuralErrors: [], contradictory: [] };
const KIND = { MI: 'missingInformation', S: 'structuralErrors', C: 'contradictory' };

/**
 * The backend returns messages like "Erreur MI 1# Missing condition #...".
 * Keep only the code (MI / S / C + number) and the error type for the side panel.
 */
function parseAnnotations(list) {
  const result = { missingInformation: [], structuralErrors: [], contradictory: [] };
  list.forEach((line) => {
    const [head, type = ''] = line.split('#');
    const m = head.match(/(?:Erreur|Error)\s+(MI|S|C)\s*(\d+)/i);
    if (m) {
      const code = m[1].toUpperCase();
      result[KIND[code]].push(`${code} ${m[2]}: ${type.trim()}`);
    }
  });
  return result;
}

/** Diagram viewer + verification: shows the diagram, runs the check, lists the errors. */
const VerifFront = () => {
  const { t } = useTranslation();
  const { projectId, diagramId } = useParams();
  const canvasRef = useRef(null);
  const viewerRef = useRef(null);

  const [annotations, setAnnotations] = useState(EMPTY);
  const [verified, setVerified] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [uploadedFile, setUploadedFile] = useState(null); // set when the user picks a local file
  const [reportUrl, setReportUrl] = useState(null);

  // One viewer for the lifetime of the page.
  useEffect(() => {
    viewerRef.current = new NavigatedViewer({ container: canvasRef.current });
    return () => viewerRef.current.destroy();
  }, []);

  const showXml = useCallback(async (xml) => {
    try {
      await viewerRef.current.importXML(xml);
      viewerRef.current.get('canvas').zoom('fit-viewport');
    } catch (e) {
      console.error('Could not import BPMN 2.0 diagram', e);
    }
  }, []);

  const showUrl = useCallback(async (url) => {
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch BPMN diagram');
    await showXml(await response.text());
  }, [showXml]);

  // Load the diagram stored in the database.
  useEffect(() => {
    if (!projectId || !diagramId) return;
    api.get(`/api/projects/${projectId}/diagrams/${diagramId}/`)
      .then(({ data }) => showUrl(data.file))
      .catch(() => setError(t('verif.errorLoad')));
  }, [projectId, diagramId, showUrl, t]);

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    setUploadedFile(file);
    setVerified(false);
    setAnnotations(EMPTY);
    setError('');
    const reader = new FileReader();
    reader.onload = (e) => showXml(e.target.result);
    reader.readAsText(file);
  };

  const handleVerify = async () => {
    setLoading(true);
    setError('');
    try {
      let data;
      if (uploadedFile) {
        const formData = new FormData();
        formData.append('file', uploadedFile);
        ({ data } = await api.post('/api/upload/verify/', formData));
      } else {
        ({ data } = await api.post(`/api/projects/${projectId}/diagrams/${diagramId}/verify/`));
      }
      await showUrl(`${API_BASE_URL}${data.filename}?t=${Date.now()}`);
      setAnnotations(parseAnnotations(data.annotations));
      setReportUrl(data.report_url);
      setVerified(true);
    } catch (e) {
      setError(t('verif.errorVerify'));
    } finally {
      setLoading(false);
    }
  };

  const renderGroup = (title, items, colour) => (
    <div className="result-item">
      <div className={`color-square ${colour}`}></div>
      <div>
        <h5>{title}</h5>
        {items.length > 0
          ? items.map((item, i) => <p key={i}>{item}</p>)
          : <p>{t('verif.noErrors')}</p>}
      </div>
    </div>
  );

  return (
    <div className="project-details-container">
      <div className="header">
        <Link to={`/dashboard/project/${projectId}`} className="back-arrow">&larr; {t('verif.back')}</Link>
        <h2><i>{t('verif.title')}</i></h2>
        <div className="button-container">
          <label htmlFor="file" className="custom-file-input">{t('verif.upload')}</label>
          <input type="file" id="file" accept=".bpmn" className="file-input" onChange={handleFileUpload} />
          <button onClick={handleVerify} disabled={loading}>
            {loading ? t('common.loading') : t('verif.verify')}
          </button>
        </div>
      </div>

      {error && <p className="error">{error}</p>}

      <div className="content">
        <div className="diagram-container">
          <div ref={canvasRef} id="canvas" className="canvas"></div>
        </div>
        <div className="sidebar">
          <h2>{t('verif.results')}</h2>
          {verified && !loading && (
            <>
              {renderGroup(t('verif.mi'), annotations.missingInformation, 'yellow')}
              {renderGroup(t('verif.s'), annotations.structuralErrors, 'red')}
              {renderGroup(t('verif.c'), annotations.contradictory, 'purple')}
            </>
          )}
        </div>
      </div>

      {verified && !loading && reportUrl && (
        <div className="view-report-container">
          <button className="view-report-btn"
            onClick={() => window.open(`${API_BASE_URL}${reportUrl}`, '_blank')}>
            {t('verif.report')}
          </button>
        </div>
      )}
    </div>
  );
};

export default VerifFront;