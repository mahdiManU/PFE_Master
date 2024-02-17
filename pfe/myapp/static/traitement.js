function display(filename){
    alert('hello again');
    var diagramUrl = 'http://127.0.0.1:8000/media/'+filename;

// viewer instance
var bpmnViewer = new BpmnJS({
  container: '#canvas'
});
async function openDiagram(bpmnXML) {

  // import diagram
  try {

    await bpmnViewer.importXML(bpmnXML);
    var canvas = bpmnViewer.get('canvas');
    var overlays = bpmnViewer.get('overlays');
    canvas.zoom('fit-viewport');
    overlays.add('SCAN_OK', 'note', {
      position: {
        bottom: 0,
        right: 0
      },
      html: '<div class="diagram-note">Mixed up the labels?</div>'
    });
    canvas.addMarker('SCAN_OK', 'needs-discussion');
  } catch (err) {

    console.error('could not import BPMN 2.0 diagram', err);
  }
}
$.get(diagramUrl, openDiagram, 'text');
   }