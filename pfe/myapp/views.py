from django.shortcuts import render , HttpResponse
from django.core.files.storage import FileSystemStorage
from rest_framework.decorators import api_view
from rest_framework.response import Response
import re
from django.http import JsonResponse
import uuid
import os
from django.conf import settings
from .mabib import *

def negative_event(bpmnfile):
   with open(bpmnfile, 'r') as file:
      lines = file.readlines()
   ids_list = []
   target_list=[]
   type_target = []
   list_finale = []
   for line in lines:
      if("<task" in line):
         match = re.search(r'id="([^"]+)"', line)
         ids_list.append(match.group(1))
   for id in ids_list:
      for line in lines:
         if((('sourceRef="'+id) in line)):
             target_list.append(re.search(r'targetRef="([^"]+)"', line).group(1))
      for i in target_list:
         
         type_target.append(get_element_type(i,bpmnfile))
      if(("intermediateThrowEvent" in type_target) and ("intermediateCatchEvent" not in type_target)):
         for i in target_list:
            
            if(get_element_type(i,bpmnfile) == "intermediateThrowEvent"):
               list_finale.append(i)
      target_list = []
      type_target = []
   return list_finale

def getway_exclusive_valide(bpmnfile,id):
   cpt=0
   with open(bpmnfile, 'r') as file:
      lines = file.readlines()
   for line in lines:
      if(('targetRef="'+id+'"') in line):
         cpt+=1
   if(cpt > 1):
      return False
   else:
      return True

def getid_picine(bpmn_file_path):
   ids_list = []
   with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
   for line in lines:
        if (("<participant" in line) and ("name=" not in line)):
         match = re.search(r'id="([^"]+)"', line)
         ids_list.append(match.group(1))
   return ids_list

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

def colorier_picine(id,liste):
   for i in liste:
      if((id in i) and ("<bpmndi:BPMNShape" in i)):
        i= i[:-2]+' bioc:stroke="#831311" bioc:fill="#ffcdd2" color:background-color="#ffcdd2" color:border-color="#831311">\n'
   return liste
 
def getways_ids2(bpmn_file_path,err):
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
            err += 1 
            message.append("erreur MI: il manque le cas de superieur")
          if("&#60" not in content.__str__() and ("inferieur" not in content.__str__())):
            err += 1 
            message.append("erreur MI: il manque le cas de inferieur")
          if("=" not in content.__str__() and ("egale" not in content.__str__())):
            err += 1 
            message.append("erreur MI: il manque le cas de egale")
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
         if(getway_exclusive_valide(bpmn_file_path,match.group(1))):
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
                msg.append("missing information : "+re.search(r'<text>(.*?)</text>', lines[lines.index(line2)+1]).group(1)+ " condition manquante dans la getway avec l'id : "+id)
   return msg

def modify_bpmn_file(bpmn_file_path):
    err = 0
    with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
    id_values = getways_ids(bpmn_file_path)
    ids_picine = getid_picine(bpmn_file_path)
    print(id_values)
    modified_lines = []
    message = []
    for id in id_values:
       err += 1
       with open(bpmn_file_path, 'r') as file:
         lines = file.readlines()
       for line in lines:
           if (id in line)and("<exclusiveGateway" in line):
               if ("name=""" in line):
                  modified_line = re.sub(r'name=""', r'name="erreur MI'+str(err)+'"', line)
                  modified_lines.append(modified_line)
               elif ("name=""" not in line):
                  modified_line =re.sub(r'(id="[^"]+")', r'\1 name="erreur MI'+str(err)+'"', line)
                  modified_lines.append(modified_line)
           if ("<bpmndi:BPMNShape" in line) and (id in line):
                line = line[:-2]+' bioc:stroke="#831311" bioc:fill="#ffcdd2" color:background-color="#ffcdd2" color:border-color="#831311">\n'
                modified_lines.append(line)
           elif ("<exclusiveGateway" not in line) or (id not in line):
              modified_lines.append(line) 
       message.append("erreur MI " +str(err)+" condition manquante :"+get_annotation(bpmn_file_path,id).__str__())  
       with open(bpmn_file_path, 'w') as file:
            file.truncate(0)
            file.writelines(modified_lines)
       modified_lines = []
    with open(bpmn_file_path, 'r') as file:
      lines2 = file.readlines()
    modified_lines = []
    if(ids_picine.__len__()>0):
      for i in ids_picine:
            for j in lines2:
              if((i in j) and ("name=" not in i) and ("<participant" in j)):
                err +=1
                modified_line =re.sub(r'(id="[^"]+")', r'\1 name="erreur MI '+str(err)+'"', j)
                modified_lines.append(modified_line)
                message.append("erreur MI " +str(err)+" role manquant")
              else:
                modified_lines.append(j)
      with open(bpmn_file_path, 'w') as file:
         file.truncate(0)
         print("hello")
         file.writelines(modified_lines)
    modified_lines = []
    with open(bpmn_file_path, 'r') as file:
      lines3 = file.readlines()
    negative = negative_event(bpmn_file_path)
    for id in negative:
       for line in lines3:
          if(("<intermediateThrowEvent" in line)and(id in line)):
             err += 1
             modified_line = re.sub(r'name=""', r'name="erreur MI'+str(err)+'"', line)
             message.append("erreur MI " +str(err)+" negative event")
             modified_lines.append(modified_line)
          elif ("<bpmndi:BPMNShape" in line) and (id in line):
                line = line[:-2]+' bioc:stroke="#831311" bioc:fill="#ffcdd2" color:background-color="#ffcdd2" color:border-color="#831311">\n'
                modified_lines.append(line)
          else:
             modified_lines.append(line)
    if(modified_lines):
     with open(bpmn_file_path, 'w') as file:
         file.truncate(0)
         file.writelines(modified_lines)
    message1 = getways_ids2(bpmn_file_path,err)
    return message1 + message 

def home(request):
    return render(request ,"myapp/home.html")

@api_view(['POST'])
def diagram(request):
    if request.method == 'POST' and 'document' in request.FILES:
        uploaded_file = request.FILES['document']

       # Save the uploaded file to a specific location
        fs = FileSystemStorage()
        
        myfile =os.path.splitext(uploaded_file.name)[0]
        fs.save(myfile+'first.bpmn',uploaded_file)
        #le fichier avec first a la fin c'est avant verification
        

       
        return JsonResponse({'filename': myfile+'first.bpmn'})
    else:
        return HttpResponse(status=400)

@api_view(['POST'])
def verify_diagram(request):
    if request.method == 'POST' and 'document' in request.FILES:
        uploaded_file = request.FILES['document']

       # Save the uploaded file to a specific location
        fs = FileSystemStorage()
        fs.save(uploaded_file.name,uploaded_file)
      
        annotation =message(fs.path(uploaded_file.name).__str__())
        annotation += modify_bpmn_file(fs.path(uploaded_file.name).__str__())
        print(annotation)
        with open(fs.path(uploaded_file.name+".txt"), 'a') as f:
            for i in annotation:
             f.write(i+" \n")
        

       
        return JsonResponse({'filename': uploaded_file.name, 'annotations': annotation})
    else:
        return HttpResponse(status=400)