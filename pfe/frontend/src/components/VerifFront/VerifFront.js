import React, {useState, useEffect } from 'react';
import './VerifFront.css';
import BpmnViewer from 'bpmn-js';

const VerifFront = () => {
    const [diagrams, setDiagrams] = useState([]);
    const [loading, setLoading] = useState(true);
    const [verifyClicked, setVerifyClicked] = useState(false);
  useEffect(() => {
    // Dynamically load the required CSS file
    const bpmnCssLink = document.createElement('link');
    bpmnCssLink.href = 'https://unpkg.com/bpmn-js@17.0.0/dist/assets/bpmn-js.css';
    bpmnCssLink.rel = 'stylesheet';
    document.head.appendChild(bpmnCssLink);

    // Dynamically load the required JavaScript file
    const bpmnJsScript = document.createElement('script');
    bpmnJsScript.src = 'https://unpkg.com/bpmn-js@17.0.0/dist/bpmn-navigated-viewer.development.js';
    document.body.appendChild(bpmnJsScript);

    // Cleanup function to remove the dynamically added elements
    return () => {
      document.head.removeChild(bpmnCssLink);
      document.body.removeChild(bpmnJsScript);
    };
  }, []);

  const handleVerifyDiagram = () => {
    setVerifyClicked(true);
    const formData = new FormData();
    formData.append('document', document.querySelector('input[name="document"]').files[0]);

    const accessToken = localStorage.getItem('access');
    if (!accessToken) {
        console.error('Access token not found.');
        return;
    }
    fetch('http://127.0.0.1:8000/api/verify-diagram/', {
        method: 'POST',
        body: formData,
        headers: {
            Authorization: `Bearer ${accessToken}`,
        },
    })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Failed to verify diagram');
            }
        })
        .then(data => {
            const canvas = document.querySelector('#canvas');
            canvas.innerHTML = ''; 
            // Assuming the response data contains the BPMN XML
            // Now you can display the diagram in the dashboard
            displayBPMNDiagram(data.filename);
            displayAnnotations(data.annotations);
        })
        .catch(error => {
            console.error("Error:", error);
        });
        setTimeout(() => {
            setLoading(false); // Simulation of verification completion
        }, 2000);
};

const handleDiagram = () => {
    setVerifyClicked(false);
    const formData = new FormData();
    formData.append('document', document.querySelector('input[name="document"]').files[0]);

    const accessToken = localStorage.getItem('access');
    if (!accessToken) {
        console.error('Access token not found.');
        return;
    }

    fetch('http://127.0.0.1:8000/api/diagram/', {
        method: 'POST',
        body: formData,
        headers: {
            Authorization: `Bearer ${accessToken}`,
        },
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Failed to verify diagram');
        }
    })
    .then(data => {
        const canvas = document.querySelector('#canvas');
        canvas.innerHTML = '';
        // Assuming the response data contains the BPMN XML
        // Now you can display the diagram in the dashboard
        displayBPMNDiagram(data.filename);
    })
    .catch(error => {
        console.error("Error:", error);
    });
};

const displayBPMNDiagram = (filename) => {
    const diagramUrl = 'http://127.0.0.1:8000/media/' + filename;

    // Create a new BPMN viewer instance
    const bpmnViewer = new BpmnViewer({
        container: '#canvas'
    });

    // Function to open and render the BPMN diagram
    const openDiagram = async (bpmnXML) => {
        try {
            // Import the BPMN XML and render the diagram
            await bpmnViewer.importXML(bpmnXML);
            const canvas = bpmnViewer.get('canvas');
           // const overlays = bpmnViewer.get('overlays');
            canvas.zoom('fit-viewport');
           
            
        } catch (err) {
            console.error('Could not import BPMN 2.0 diagram', err);
        }
    };

    fetch(diagramUrl)
.then(response => {
    if (!response.ok) {
        throw new Error('Failed to fetch BPMN diagram');
    }
    return response.text();
})
.then(bpmnXML => {
    // Once the BPMN XML is fetched, open and render the diagram
    openDiagram(bpmnXML);
})
.catch(error => {
    console.error('Error fetching BPMN diagram:', error);
});
};
const displayAnnotations = (annotations) => {
   // setAnnotations(annotations);
};
//<Sidebar annotations={annotations} />

  return (
    <div className="project-details-container">
            <div className="header">
                <h2><i>LegProV : Legal Process Verification</i></h2>
                <div className="button-container">
                    <label htmlFor="file" className="custom-file-input">Upload </label>
                    <input type="file" id="file" name="document" className="file-input" onChange={handleDiagram} />
                    <button onClick={handleVerifyDiagram}>Verify</button>
                </div>
            </div>
            <div className="content">
                <div className="diagram-container">
                    <div id="canvas" className="canvas"></div>
                </div>
                <div className="sidebar">
                    <h2>Results</h2>
                    <div className="result-item">
                        <div className="color-square yellow"></div>
                        <div>
                            <h5>Missing Information:</h5>
                            <p>MI 1: Undefined gatway</p>
                            <p>MI 2: Undefined role</p>
                        </div>
                    </div>
                    <div className="result-item">
                        <div className="color-square red"></div>
                        <div>
                            <h5>Structural Errors:</h5>
                            <p>S1: Nondeterministic deadlock</p>
                        </div>
                    </div>
                    <div className="result-item">
                        <div className="color-square purple"></div>
                        <div>
                            <h5>Contradictory:</h5>
                            <p>No error found</p>
                        </div>
                    </div>
                </div>
            </div>
            {verifyClicked && !loading && ( // Show View Report button only if Verify button is clicked and verification is completed
                <div className="view-report-container">
                    <button className="view-report-btn">View Report</button>
                </div>
            )}
        </div>


  );
};

export default VerifFront;
