from django.shortcuts import render , HttpResponse
from django.core.files.storage import FileSystemStorage
import re
def getways_ids(bpmn_file_path):
   ids_list = []
   with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
   for line in lines:
        if ("<exclusiveGateway" in line) and (("name=""" in line) or ("name=""" not in line)):
         match = re.search(r'id="([^"]+)"', line)
         ids_list.append(match.group(1))
   return ids_list
def get_annotation(bpmn_file_path,id):
   msg = []
   with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
   for line in lines:
        if ("<association" in line) and (id in line):
         match = re.search(r'targetRef="([^"]+)"', line)
         temp = match.group(1)
         for line2 in lines : 
             if temp in line2 and  '<textAnnotation' in line2:
                msg.append(re.search(r'<text>(.*?)</text>', lines[lines.index(line2)+1]).group(1))
   return msg
 
def modify_bpmn_file(bpmn_file_path):
    with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
    id_values = getways_ids(bpmn_file_path)
    modified_lines = []
    message = []
    for id in id_values:
       for line in lines:
           if (id in line)and("<exclusiveGateway" in line):
               if ("name=""" in line):
                  modified_line = re.sub(r'name=""', r'name="condition manquante ici"', line)
                  modified_lines.append(modified_line)
               elif ("name=""" not in line):
                  modified_line =re.sub(r'(id="[^"]+")', r'\1 name="condition manquante ici"', line)
                  modified_lines.append(modified_line)
           if "<bpmndi:BPMNShape" in line and id in line:
                line = line[:-2]+' bioc:stroke="#831311" bioc:fill="#ffcdd2" color:background-color="#ffcdd2" color:border-color="#831311">\n'
                modified_lines.append(line)
           elif ("<exclusiveGateway" not in line) or (id not in line):
              modified_lines.append(line) 
       message += get_annotation(bpmn_file_path,id)  
       with open(bpmn_file_path, 'w') as file:
            file.truncate(0)
            file.writelines(modified_lines)
       modified_lines = []
       with open(bpmn_file_path, 'r') as file:
            lines = file.readlines()
    return message
def home(request):
    return render(request ,"home.html")
def upload(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()
        fs.save(uploaded_file.name,uploaded_file)
        annotation = modify_bpmn_file(fs.path(uploaded_file.name)).__str__()
        return render(request, 'upload_success.html',{'file_name': uploaded_file.name,'annotation': annotation})
    return render(request ,"upload.html")

