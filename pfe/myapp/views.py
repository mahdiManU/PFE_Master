from django.shortcuts import render , HttpResponse
from django.core.files.storage import FileSystemStorage
from rest_framework.decorators import api_view
from rest_framework.response import Response
import re

def getids(bpmn_file_path):
   ids_list = []
   with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
   for line in lines:
        if ("<exclusiveGateway" in line):
         match = re.search(r'id="([^"]+)"', line)
         ids_list.append(match.group(1))
   return ids_list
def verif_logique(maliste,id):
  # Use regular expression to find all numbers in the string
    numbers = re.findall(r'\d+', maliste)
    unique_numbers = set(map(int, numbers))
    num = len(unique_numbers) -2
    nb1 = maliste.count("&#62") + maliste.count("superieur")
    nb2 = maliste.count("&#60") + maliste.count("inferieur")
    nb3 = maliste.count("=") + maliste.count("egal")
    if(((nb1 + nb2 + nb3) != 6) and num ==2):
        return "missing information : missing interval dans la getway avec l'id : "+id 
    else:
        return 0

def getways_ids2(bpmn_file_path):
   ids_list = []
   content = []
   with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
   ids_list = getids(bpmn_file_path)
   message = []
   for i in ids_list:
       for j in lines:
         if(("<sequenceFlow" in j) and (i in j)):
            test = re.search(r'name="([^"]+)"', j)
            if test:
             content.append(test.group(1))
       if(("&#62" in content.__str__()) or ("&#60" in content.__str__()) or ("=" in content.__str__()) or ("superieur" in content.__str__()) or ("inferieur" in content.__str__()) or ("egale" in content.__str__())):
          if("&#62" not in content.__str__() and ("superieur" not in content.__str__())):
            message.append("missing information : il manque le cas de superieur dans la getway avec l'id : "+i)
          if("&#60" not in content.__str__() and ("inferieur" not in content.__str__())):
            message.append("missing information : il manque le cas de inferieur dans la getway avec l'id : "+i)
          if("=" not in content.__str__() and ("egale" not in content.__str__())):
            message.append("missing information : il manque le cas de egale dans la getway avec l'id : "+i)
       if(verif_logique(content.__str__(),i)):
          message.append(verif_logique(content.__str__(),i))
       content = []        
   return message
def getways_ids(bpmn_file_path):
   ids_list = []
   with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
   for line in lines:
        if ("<exclusiveGateway" in line) and (("name=" not in line)):
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
                msg.append(re.search(r'<text>(.*?)</text>', lines[lines.index(line2)+1]).group(1)+ " condition manquante dans la getway avec l'id : "+id)
   return msg
 
def modify_bpmn_file(bpmn_file_path):
    with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
    id_values = getways_ids(bpmn_file_path)
    print(id_values)
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
           if ("<bpmndi:BPMNShape" in line) and (id in line):
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
    message1 = getways_ids2(bpmn_file_path)
    return message1 + message

def home(request):
    return render(request ,"myapp/home.html")
def upload(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()
        fs.save(uploaded_file.name,uploaded_file)
        annotation = modify_bpmn_file(fs.path(uploaded_file.name))
        with open(fs.path(uploaded_file.name+".txt"), 'a') as f:
            for i in annotation:
             f.write(i+" \n")
        return render(request, 'myapp/upload_success.html',{'file_name': uploaded_file.name,'annotation': annotation.__str__()})
    return render(request ,"myapp/upload.html")

