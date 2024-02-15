alert("hello");
function display_bpmn(){
    var bpmnViewer = new BpmnJS({ container: '#bpmn-container' });

    // Load BPMN file
    fetch('your-bpmn-file.bpmn')
        .then(response => response.text())
        .then(xml => {
            // Display BPMN diagram
            bpmnViewer.importXML(xml, function(err) {
                if (err) {
                    console.error('Error rendering BPMN diagram', err);
                } else {
                    console.log('BPMN diagram rendered successfully');
                }
            });
        })
        .catch(error => console.error('Error fetching BPMN file', error));
}