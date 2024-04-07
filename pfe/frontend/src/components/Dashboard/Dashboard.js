import React, {useState, useEffect} from 'react'
import { useSelector } from 'react-redux'
import NavDash from '../NavDash/NavDash'
import './Dashboard.css'
import BpmnViewer from 'bpmn-js';
import Sidebar from '../Sidebar/Sidebar';



const Dashboard = () => {

    const { userInfo } = useSelector((state) => state.auth)
    const [annotations, setAnnotations] = useState([]);

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
        const formData = new FormData();
        formData.append('document', document.querySelector('input[name="document"]').files[0]);
    
        fetch('http://127.0.0.1:8000/api/verify-diagram/', {
            method: 'POST',
            body: formData
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
    };

    const handleDiagram = () => {
        const formData = new FormData();
        formData.append('document', document.querySelector('input[name="document"]').files[0]);
    
        fetch('http://127.0.0.1:8000/api/diagram/', {
            method: 'POST',
            body: formData
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
                const overlays = bpmnViewer.get('overlays');
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
        setAnnotations(annotations);
    };
    return (
        <div>
            <NavDash />
            <div className="container">
               
                <div className="main-body">
                    <div className="promo_card">
                        <h1>Welcome, {userInfo.first_name} </h1>
                        
                        <input type="file" name="document"  onChange={handleDiagram}/>
                        <div id="canvas" style={{ width: '100%', height: '500px' }}></div>
                        <button onClick={handleVerifyDiagram}> Verify diagram</button>
                        
                    </div>
                   
                </div>
                <Sidebar annotations={annotations} />
    
            </div>
        </div>
    )
}

export default Dashboard