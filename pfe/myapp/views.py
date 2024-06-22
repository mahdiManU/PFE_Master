from django.shortcuts import render , HttpResponse
from django.core.files.storage import FileSystemStorage
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.files.storage import default_storage
import re
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
import uuid
import os
from rest_framework import serializers
import shutil
from django.conf import settings
from .mabib import *
from .mabib import trouver_article
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework import generics, permissions
from .models import Project,Diagram
from .serializers import ProjectSerializer, DiagramSerializer
from django.db.models import Count
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import PermissionDenied
import logging
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from .rapport import *
from .contradiction import *
from .rapportEng import *
from .add import *

@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'csrfToken': request.META.get('CSRF_COOKIE')})

class ProjectListCreateAPIView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(owner=user)

    def perform_create(self, serializer):
        # Save the project
        project = serializer.save(owner=self.request.user)
        
        # Create directories
        user_directory = os.path.join('media', f'user_{self.request.user.id}')
        project_directory = os.path.join(user_directory, f'project_{project.id}')
        os.makedirs(project_directory, exist_ok=True)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ProjectDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(owner=user)

    def dispatch(self, request, *args, **kwargs):
        project_id = kwargs.get('pk')
        if not Project.objects.filter(id=project_id).exists():
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        project = self.get_object()
        project_id = project.id
        
        # Delete the project's directory
        user_directory = os.path.join('media', f'user_{self.request.user.id}')
        project_directory = os.path.join(user_directory, f'project_{project_id}')
        if os.path.exists(project_directory):
            shutil.rmtree(project_directory)
        
        # Call the parent delete method to delete the project
        return super().delete(request, *args, **kwargs)

class DiagramListCreateAPIView(generics.ListCreateAPIView):
    queryset = Diagram.objects.all()
    serializer_class = DiagramSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return Diagram.objects.filter(project_id=project_id)

    def perform_create(self, serializer):
        project_id = self.kwargs['project_id']
        project = Project.objects.get(id=project_id)
        diagram = serializer.save(project=project)

        # Ensure no `diagram_None` folder is left behind
        project_directory = os.path.join(settings.MEDIA_ROOT, f'user_{project.owner.id}', f'project_{project.id}')
        none_directory = os.path.join(project_directory, 'diagram_None')

        if os.path.exists(none_directory):
            try:
                os.rmdir(none_directory)
            except OSError:
                print(f"Could not remove non-empty folder: {none_directory}")

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logging.error(f"Invalid data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class DiagramDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Diagram.objects.all()
    serializer_class = DiagramSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        diagram_id = self.kwargs['id']
        return Diagram.objects.filter(project_id=project_id, id=diagram_id)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        project_id = instance.project_id
        
        if project_id is not None:
            # Delete diagram folder
            diagram_folder_path = os.path.join('media', f'user_{request.user.id}', f'project_{project_id}', f'diagram_{instance.id}')
            if os.path.exists(diagram_folder_path):
                shutil.rmtree(diagram_folder_path)

            # Perform the actual destroy operation
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "Project ID is missing for the diagram."})
    
def get_project_diagrams(request, project_id):
    try:
        # Retrieve diagrams associated with the specified project ID
        diagrams = Diagram.objects.filter(project_id=project_id)
        # Serialize the diagrams data
        serialized_diagrams = [{'id': diagram.id, 'name': diagram.name, 'description':diagram.description, 'file': diagram.file.url, 'verified': diagram.verified} for diagram in diagrams]
        # Return the serialized diagrams data as JSON response
        return JsonResponse(serialized_diagrams, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_nom_taches_role(bpmnfile,id):
   taches = []
   liste_elements = get_flow_node_refs_from_lane(bpmnfile,id)
   for i in liste_elements:
     print(i)
     print(get_element_type(i,bpmnfile))
     if("Activity" in i):
       taches.append(get_task(bpmnfile,i))
   return taches
def get_participant_id_for_task(file_path, task_id):
    # Lire le fichier XML ligne par ligne
    with open(file_path, 'r') as file:
        lines = file.readlines()
        xml_content = ''.join(lines)
    
    # Fonction pour extraire la valeur d'un attribut XML
    def extract_attribute(xml, attribute):
        attr_start = f'{attribute}="'
        start_idx = xml.find(attr_start)
        if start_idx != -1:
            start_idx += len(attr_start)
            end_idx = xml.find('"', start_idx)
            return xml[start_idx:end_idx]
        return None

    # Trouver la tâche avec l'ID donné
    task_start = f'<task id="{task_id}"'
    task_idx = xml_content.find(task_start)
    if task_idx == -1:
        return None
    
    # Trouver le processus contenant cette tâche
    process_start = '<process '
    process_end = '</process>'
    
    process_idx = xml_content.find(process_start)
    while process_idx != -1:
        process_end_idx = xml_content.find(process_end, process_idx) + len(process_end)
        process_xml = xml_content[process_idx:process_end_idx]
        
        # Vérifier si le processus contient cette tâche
        if task_start in process_xml:
            process_id = extract_attribute(process_xml, 'id')
            break
        process_idx = xml_content.find(process_start, process_end_idx)
    
    if process_id is None:
        return None
    
    # Trouver le participant contenant ce processus
    participant_start = '<participant '
    participant_end = '/>'
    
    participant_idx = xml_content.find(participant_start)
    while participant_idx != -1:
        participant_end_idx = xml_content.find(participant_end, participant_idx) + len(participant_end)
        participant_xml = xml_content[participant_idx:participant_end_idx]
        
        # Vérifier si le participant contient ce processus
        if f'processRef="{process_id}"' in participant_xml:
            return extract_attribute(participant_xml, 'id')
        
        participant_idx = xml_content.find(participant_start, participant_end_idx)
    
    return None
def get_flow_node_refs_from_lane(bpmn_file_path, lane_id):
    flow_node_refs = []
    with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
    
    lane_start = False
    for line in lines:
        # Check for the start of the specific lane
        if f'<lane id="{lane_id}"' in line:
            lane_start = True
        
        # If within the lane, look for flowNodeRef elements
        if lane_start:
            if "<flowNodeRef>" in line:
                match = re.search(r'<flowNodeRef>(.*?)</flowNodeRef>', line)
                if match:
                    flow_node_refs.append(match.group(1))
            
            # Check for the end of the lane
            if "</lane>" in line:
                lane_start = False
    
    return flow_node_refs
def clean_list(string_list):
    # Utiliser un ensemble pour éliminer les doublons, puis filtrer les chaînes vides
    return list({s for s in string_list if s})
def supprimer_doublons(liste):
    vue = []
    resultat = []
    for element in liste:
        if element not in vue:
            resultat.append(element)
            vue.append(element)
    return resultat
def get_lane_id_from_flow_node(bpmn_file_path, flow_node_id):
    lane_id = ""
    with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
    
    for line in lines:
        if "<lane id=" in line:
            lane_match = re.search(r'<lane id="([^"]+)"', line)
            if lane_match:
                current_lane_id = lane_match.group(1)
        
        if "<flowNodeRef>" in line and flow_node_id in line:
            flow_node_match = re.search(r'<flowNodeRef>(.*?)</flowNodeRef>', line)
            if flow_node_match and flow_node_match.group(1) == flow_node_id:
                lane_id = current_lane_id
                break
    
    return lane_id
def get_annotation_proxy(bpmnfile,id):
   loi = []
   id_list = []
   with open(bpmnfile, 'r') as file:
      lines = file.readlines()
   for line in lines:
      if((('sourceRef="'+id) in line) ):
         id_list.append(re.search(r'targetRef="([^"]+)"', line).group(1))
      if((('targetRef="'+id) in line)):
         id_list.append(re.search(r'sourceRef="([^"]+)"', line).group(1))
   id_lane = get_participant_id_for_task(bpmnfile,id)
   #print('basta' + id_lane)
   loi.append(get_annotation_for_participant(bpmnfile,id_lane))
    
   

   for i in id_list:
      loi.append(get_annotation2(bpmnfile,i))
   loi.append(get_annotation2(bpmnfile,id))
   loi.append(get_annotation2(bpmnfile,get_lane_id_from_flow_node(bpmnfile,id)))
   return supprimer_doublons(loi)
def get_annotation_role(bpmnfile,id):
   finale = []
   tache_liste = get_flow_node_refs_from_lane(bpmnfile,id)
   for i in tache_liste:
       finale.append(get_annotation3(bpmnfile,i))
       finale.append(get_annotation2(bpmnfile,i))
   return clean_list(finale)
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
      if(("intermediateCatchEvent" in type_target) and ("intermediateCatchEvent" not in type_target)):
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
        if ((("<participant" in line) and ("name=" not in line)) or (("<lane " in line) and ("name=" not in line))):
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
def verif_logique(bpmnfile,maliste,id):
  # Use regular expression to find all numbers in the string
    numbers = re.findall(r'\d+', maliste)
    unique_numbers = set(map(int, numbers))
    num = len(unique_numbers) -2
    nb1 = maliste.count("&#62") + maliste.count("superieur")
    nb2 = maliste.count("&#60") + maliste.count("inferieur")
    nb3 = maliste.count("=") + maliste.count("egal")
    if(((nb1 + nb2 + nb3) != 6) and num ==2):
        if(get_annotation2(bpmnfile,id)):
           return "missing information : interval manquant voire article :"+get_annotation(bpmnfile,id).__str__()
        else:
           return "missing information : interval manquant"
    else:
        return 0
def get_annotation2(bpmn_file_path,id):
   msg = ""
   with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
   for line in lines:
        if ("<association" in line) and (id in line):
         match = re.search(r'sourceRef="([^"]+)"', line)
         temp = match.group(1)
         for line2 in lines : 
             if temp in line2 and  '<textAnnotation' in line2:
                msg = re.search(r'<text>(.*?)</text>', lines[lines.index(line2)+1])
                if (msg):
                    return msg.group(1)
   return msg
def colorier_task(bpmnfile,id_task):
     new_lines = []
     with open(bpmnfile, 'r') as file:
        lines = file.readlines()
     for i in lines:
         if(("<bpmndi:BPMNShape" in i) and (id_task in i) and ("bioc:stroke" not in i)):
             modified_line =i[:-2]+' bioc:stroke="#6b3c00" bioc:fill="#ffe0b2" color:background-color="#ffe0b2" color:border-color="#6b3c00">\n'
             new_lines.append(modified_line)
         else:
             new_lines.append(i)
     with open(bpmnfile, 'w') as file:
         file.truncate(0)
         file.writelines(new_lines)
def colorier_picine(id,liste):
   for i in liste:
      if((id in i) and ("<bpmndi:BPMNShape" in i)):
        i= i[:-2]+' bioc:stroke="#831311" bioc:fill="#ffcdd2" color:background-color="#ffcdd2" color:border-color="#831311">\n'
   return liste
def getways_ids2(bpmn_file_path,err):
   ids_list = []
   content = []
   messageENG = []
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
            messageENG.append("Error MI"+err+"# the upper case is missing# see the article "+get_annotation(bpmn_file_path,i).__str__())
            message.append("erreur MI"+err+"# il manque le cas de superieur# voire l'article "+get_annotation(bpmn_file_path,i).__str__())
          if("&#60" not in content.__str__() and ("inferieur" not in content.__str__())):
            err += 1
            messageENG.append("Error MI"+err+"# the lower case is missing# see the article "+get_annotation(bpmn_file_path,i).__str__()) 
            message.append("erreur MI"+err+"#: il manque le cas de inferieur# voire l'article "+get_annotation(bpmn_file_path,i).__str__())
          if("=" not in content.__str__() and ("egale" not in content.__str__())):
            err += 1 
            messageENG.append("Error MI"+err+"# the case of equal is missing# see the article "+get_annotation(bpmn_file_path,i).__str__()) 
            message.append("erreur MI"+err+"#: il manque le cas de egale# voire l'article "+get_annotation(bpmn_file_path,i).__str__())
       if(verif_logique(bpmn_file_path,content.__str__(),i)):
          message.append(verif_logique(bpmn_file_path,content.__str__(),i))
       content = []        
   return message , messageENG
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
                msg.append("missing information : "+re.search(r'<text>(.*?)</text>', lines[lines.index(line2)+1]).group(1))
   return msg
def get_annotation3(bpmn_file_path,id):
   msg = []
   with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
   for line in lines:
        if ("<association" in line) and (id in line):
         match = re.search(r'targetRef="([^"]+)"', line)
         temp = match.group(1)
         for line2 in lines : 
             if temp in line2 and  '<textAnnotation' in line2:
                return re.search(r'<text>(.*?)</text>', lines[lines.index(line2)+1]).group(1)
def get_all_tasks(bpmnfile):
    allTasks = []
    with open(bpmnfile, 'r') as file:
        lines = file.readlines()
    for i in lines:
        if("<task" in i):
            match = re.search(r'id="([^"]+)"', i)
            allTasks.append(match.group(1))
    return allTasks
def modify_bpmn_file(bpmn_file_path):
    print('hello')
    err = 0
    with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
    id_values = getways_ids(bpmn_file_path)
    ids_picine = getid_picine(bpmn_file_path)
    
    modified_lines = []
    message = []
    messageENG =[]
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
                line = line[:-2]+' bioc:stroke="#6b3c00" bioc:fill="#ffe0b2" color:background-color="#ffe0b2" color:border-color="#6b3c00">\n'
                modified_lines.append(line)
           elif ("<exclusiveGateway" not in line) or (id not in line):
              modified_lines.append(line) 
       if(get_annotation_proxy(bpmn_file_path,id).__len__() > 0):
          messageENG.append("Error MI " +str(err)+"# Missing condition #"+"Condition not specified in the article : "+get_annotation_proxy(bpmn_file_path,id).__str__()+"#Revise the article : "+get_annotation_proxy(bpmn_file_path,id).__str__()+" and Add the appropriate condition") 
          message.append("Erreur MI " +str(err)+"# Condition manquante #"+"Condition non preciser dans l'article : "+get_annotation_proxy(bpmn_file_path,id).__str__()+"#Reviser l'article : "+get_annotation_proxy(bpmn_file_path,id).__str__()+" et Ajouter la condition adéquate")  
       else:
          messageENG.append("Error MI " +str(err)+"# Missing condition #This part is not annotated on the diagram#Add the correct condition")
          message.append("Erreur MI " +str(err)+"# Condition manquante #Cette partie est Non annoter sur le diagramme#Ajouter la condition adéquate")
       with open(bpmn_file_path, 'w') as file:
            file.truncate(0)
            file.writelines(modified_lines)
       modified_lines = []
    with open(bpmn_file_path, 'r') as file:
      lines2 = file.readlines()
    modified_lines = []
    if(ids_picine.__len__()>0):
      for i in ids_picine:
            with open(bpmn_file_path, 'r') as file:
                 lines2 = file.readlines()
            modified_lines = []
            for j in lines2:
              if((i in j) and ("<bpmndi:BPMNShape" in j)):
                err +=1
                modified_line =j[:-2]+' bioc:stroke="#6b3c00" bioc:fill="#ffe0b2" color:background-color="#ffe0b2" color:border-color="#6b3c00">\n'
                
                modified_lines.append(modified_line)
                if(get_annotation_role(bpmn_file_path,i).__len__() >0):
                 print("chikour" + get_annotation_role(bpmn_file_path,i).__str__() )
                 messageENG.append("Error MI " +str(err)+"# Missing role # Role not specified in the article : "+get_annotation_role(bpmn_file_path,i).__str__()+"#Revise the article : "+get_annotation_role(bpmn_file_path,i).__str__()+" Add the appropriate role to these tasks :"+get_nom_taches_role(bpmn_file_path,i).__str__())
                 message.append("Erreur MI " +str(err)+"# Role manquant # Role non précisé dans l'article : "+get_annotation_role(bpmn_file_path,i).__str__()+"#Reviser l'article : "+get_annotation_role(bpmn_file_path,i).__str__()+" Ajouter le rôle adéquat a ces taches :"+get_nom_taches_role(bpmn_file_path,i).__str__())
                else:
                 messageENG.append("Error MI " +str(err)+"# Missing role #Cette partie est Non annoter sur le diagramme#Add the correct role" )
                 message.append("Erreur MI " +str(err)+"# Role manquant #Cette partie est Non annoter sur le diagramme#Ajouter le rôle adéquat" )
              else:
                modified_lines.append(j)
      
            with open(bpmn_file_path, 'w') as file:
              file.truncate(0)
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
                line = line[:-2]+' bioc:stroke="#6b3c00" bioc:fill="#ffe0b2" color:background-color="#ffe0b2" color:border-color="#6b3c00">\n'
                modified_lines.append(line)
          else:
             modified_lines.append(line)
    if(modified_lines):
     with open(bpmn_file_path, 'w') as file:
         file.truncate(0)
         file.writelines(modified_lines)
    with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
    modified_lines = []
    all_tasks = get_all_tasks(bpmn_file_path)
    for i in all_tasks:
        cpt = 0
        for line in lines:
            if(('sourceRef="'+i+'"') in line):
                cpt += 1
        if(cpt == 0):
            err+=1
            messageENG.append("Error MI " +str(err)+"# Legal vacuum #"+"Legal vacuum in the article : "+get_annotation_proxy(bpmn_file_path,i).__str__()+"#Revise the article : "+get_annotation_proxy(bpmn_file_path,i).__str__()+" and Add adequate information")  
            message.append("Erreur MI " +str(err)+"# Vide juridique #"+"Vide juridique dans l'article : "+get_annotation_proxy(bpmn_file_path,i).__str__()+"#Reviser l'article : "+get_annotation_proxy(bpmn_file_path,i).__str__()+" et Ajouter des informations adéquates")  
            #message.append("Erreur MI " +str(err)+"# Vide juridique # Vide juridique dans l'article : "+get_annotation_proxy(bpmn_file_path,i).__str__()+" # Reviser l'article : "+get_annotation_proxy(bpmn_file_path,i).__str__()+" Ajouter des information à :"+get_annotation_proxy(bpmn_file_path,i).__str__())
            print(message.__str__())
            colorier_task(bpmn_file_path,i)
    message1 , message2= getways_ids2(bpmn_file_path,err)
    return message1 + message , message2+messageENG 
def home(request):
    return render(request ,"myapp/home.html")

def upload(request):
    if request.method == 'POST':
       # testPDF()
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()
        fs.save(uploaded_file.name,uploaded_file)
        myfile =os.path.splitext(uploaded_file.name)[0]
        fs.save(myfile+'first.bpmn',uploaded_file)
       # print(fs.path('loi3.txt'))
        #le fichier avec first a la fin c'est avant verification
        
        arts = message(fs.path(uploaded_file.name).__str__(),fs.path(myfile+'first.bpmn'),fs.path('loi3.txt').__str__())
        
        with open(fs.path(uploaded_file.name+".txt"), 'a') as f:
            for i in arts:
             f.write(i+" \n")
        annotation ,annotationENG= modify_bpmn_file(fs.path(uploaded_file.name).__str__())
        liste_finale = arts + annotation
        report_name = uploaded_file.name + '.docx'
        #report_name_eng = uploaded_file.name +'ENG'+ '.docx'
        report_path = os.path.join(settings.MEDIA_ROOT, report_name)
        #report_pathENG = os.path.join(settings.MEDIA_ROOT, report_name_eng)
        generer_rapport(liste_finale, report_path,uploaded_file.name)
        #generer_rapportENG(liste_finale,report_pathENG)
        with open(fs.path(uploaded_file.name+".txt"), 'a') as f:
            for i in annotation:
             f.write(i+" \n")
        return render(request, 'myapp/new.html',{'file_name': uploaded_file.name,'file_name2' : myfile+'first.bpmn','annotation': annotation.__str__()})
    return render(request ,"myapp/upload.html")






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

logger = logging.getLogger(__name__)


@api_view(['POST'])
def verify_diagram(request, project_id, diagram_id):
    try:
        logger.info(f"Verifying diagram {diagram_id} for project {project_id}")

        # Fetch the diagram object
        diagram = Diagram.objects.get(id=diagram_id, project_id=project_id)

        # Construct paths
        user_folder = f'user_{request.user.id}'
        project_folder = f'project_{project_id}'
        diagram_folder = f'diagram_{diagram_id}'
        diagram_folder_path = os.path.join(settings.MEDIA_ROOT, user_folder, project_folder, diagram_folder)

        # Ensure the diagram directory exists
        if not os.path.exists(diagram_folder_path):
            logger.error(f"Diagram directory not found: {diagram_folder_path}")
            return HttpResponse(status=404, content="Diagram directory not found")

        # Find the BPMN file in the directory
        diagram_file = next((file_name for file_name in os.listdir(diagram_folder_path) if file_name.endswith('.bpmn')), None)

        # Ensure a diagram file is found
        if not diagram_file:
            logger.error("Diagram file not found")
            return HttpResponse(status=404, content="Diagram file not found")

        # Path to the original diagram file
        original_file_path = os.path.join(diagram_folder_path, diagram_file)
        logger.info(f"Original file path: {original_file_path}")

        # Copy the original file to create a verified version
        verified_file_path = os.path.join(diagram_folder_path, 'verified_diagram.bpmn')
        shutil.copyfile(original_file_path, verified_file_path)

        # Perform verification on the copied file
        arts ,artsENG = message(verified_file_path, verified_file_path, os.path.join(settings.MEDIA_ROOT, 'loi3.txt'))
        annotation ,annotationENG= modify_bpmn_file(verified_file_path)
        err_contradiction , err_contradictionENG= erreur_contradiction(verified_file_path)
        liste_finale = arts + annotation + err_contradiction
        liste_finaleENG = artsENG + annotationENG+ err_contradictionENG

        # Generate report
        report_name = 'report.docx'
        report_nameENG = 'reportENG.docx'
        report_path = os.path.join(diagram_folder_path, report_name)
        report_pathENG = os.path.join(diagram_folder_path, report_nameENG)
        generer_rapport(liste_finale, report_path, diagram_file)
        generer_rapportENG(liste_finaleENG, report_pathENG, diagram_file)

        # Save annotations to a file
        with open(os.path.join(diagram_folder_path, "diagram_annotations.txt"), 'a') as f:
            for item in annotation:
                f.write(item + "\n")

        # Update diagram status
        diagram.verified = True
        diagram.save()

        logger.info("Diagram verified successfully")

        # Construct the URL to the verified file
        verified_file_url = default_storage.url(os.path.join(user_folder, project_folder, diagram_folder, 'verified_diagram.bpmn'))
        report_file_url = default_storage.url(os.path.join(user_folder, project_folder, diagram_folder, report_name))

        return JsonResponse({'filename': verified_file_url, 'report_url': report_file_url, 'annotations': liste_finale})
    
    except Diagram.DoesNotExist:
        logger.error(f"Diagram {diagram_id} does not exist for project {project_id}")
        return HttpResponse(status=404, content=f"Diagram {diagram_id} does not exist for project {project_id}")

    except Exception as e:
        logger.error(f"Error verifying diagram: {e}", exc_info=True)
        return HttpResponse(status=500, content="Internal Server Error")
    

def get_diagram(request, project_id, diagram_id):
    try:
        diagram = Diagram.objects.get(id=diagram_id, project_id=project_id)
        diagram_folder_path = os.path.join(settings.MEDIA_ROOT, f'user_{request.user.id}', f'project_{project_id}', f'diagram_{diagram_id}')
        
        if diagram.verified:
            diagram_path = os.path.join(diagram_folder_path, 'verified_diagram.bpmn')
        else:
            diagram_path = os.path.join(diagram_folder_path, 'diagram.bpmn')
        
        if os.path.exists(diagram_path):
            file_url = f"/media/user_{request.user.id}/project_{project_id}/diagram_{diagram_id}/{os.path.basename(diagram_path)}"
            return JsonResponse({'filename': file_url})
        else:
            return HttpResponse(status=404)
    except Diagram.DoesNotExist:
        return HttpResponse(status=404)

@api_view(['POST'])
def upload_and_verify_diagram(request):
    try:
        logger.info("Uploading and verifying diagram")

        # Get the uploaded file
        file = request.FILES['file']

        # Create a unique folder for the upload
        upload_folder_path = os.path.join(settings.MEDIA_ROOT, 'uploads', f'user_{request.user.id}')
        if not os.path.exists(upload_folder_path):
            os.makedirs(upload_folder_path)

        # Save the uploaded file
        original_file_path = os.path.join(upload_folder_path, file.name)
        with open(original_file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        logger.info(f"Uploaded file saved at: {original_file_path}")

        # Copy the original file to create a verified version
        verified_file_path = os.path.join(upload_folder_path, 'verified_diagram.bpmn')
        shutil.copyfile(original_file_path, verified_file_path)

        # Perform verification on the copied file
        arts ,artsENG= message(verified_file_path, verified_file_path, os.path.join(settings.MEDIA_ROOT, 'loi3.txt'))
        annotation ,annotationENG= modify_bpmn_file(verified_file_path)
        err_contradiction , erreur_contradictionENG= erreur_contradiction(verified_file_path)
        liste_finale = arts + annotation + err_contradiction
        liste_finaleENG = artsENG+annotationENG+erreur_contradictionENG

        # Generate report
        report_name = 'report.docx'
        report_path = os.path.join(upload_folder_path, report_name)
        report_nameENG = 'report.docx'
        report_pathENG = os.path.join(upload_folder_path, report_nameENG)
        generer_rapport(liste_finale, report_path,file.name)
        generer_rapportENG(liste_finaleENG, report_pathENG,file.name)

        # Save annotations to a file
        with open(os.path.join(upload_folder_path, "diagram_annotations.txt"), 'a') as f:
            for item in annotation:
                f.write(item + "\n")

        report_file_url = f'/media/uploads/user_{request.user.id}/report.docx'        

        logger.info("Diagram verified successfully")

        return JsonResponse({'filename': f'/media/uploads/user_{request.user.id}/verified_diagram.bpmn', 'report_url':report_file_url,'annotations': liste_finale})
    except Exception as e:
        logger.error(f"Error in upload_and_verify_diagram: {e}")
        return HttpResponse(status=500, content="Internal server error")