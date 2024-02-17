from django.shortcuts import render , HttpResponse
from django.core.files.storage import FileSystemStorage
import re
def modify_bpmn_file(bpmn_file_path):
    with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
    id_value="kalo"
    modified_lines = []
    for line in lines:
        if ("<exclusiveGateway" in line) and (("name=""" in line) or ("name=""" not in line)):
         match = re.search(r'id="([^"]+)"', line)
         id_value = match.group(1)
         print(id_value)
         if ("name=""" in line):
           modified_line = re.sub(r'name=""', r'name="condition manquante ici"', line)
         else :
           modified_line =re.sub(r'(id="[^"]+")', r'\1 name="condition manquante ici"', line)
         modified_lines.append(modified_line)
        elif id_value in line and "<bpmndi:BPMNShape" in line:
          line = line[:-2]+' bioc:stroke="#831311" bioc:fill="#ffcdd2" color:background-color="#ffcdd2" color:border-color="#831311">\n'
          modified_lines.append(line)
        else:
          modified_lines.append(line)
    #print(modified_lines)
    with open(bpmn_file_path, 'w') as file:
        file.writelines(modified_lines)
# Create your views here.
def home(request):
    return render(request ,"home.html")
def upload(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()
        fs.save(uploaded_file.name,uploaded_file)
        modify_bpmn_file(fs.path(uploaded_file.name))
        return render(request, 'upload_success.html',{'file_name': uploaded_file.name})
    return render(request ,"upload.html")

