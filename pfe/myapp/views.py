from django.shortcuts import render , HttpResponse
from django.core.files.storage import FileSystemStorage
from rest_framework.decorators import api_view
from rest_framework.response import Response
import re
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
import uuid
import os
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
        serializer.save(project=project)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logging.error(f"Invalid data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
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
   
   

   for i in id_list:
      loi.append(get_annotation2(bpmnfile,i))
   loi.append(get_annotation2(bpmnfile,id))
   loi.append(get_annotation2(bpmnfile,get_lane_id_from_flow_node(bpmnfile,id)))
   return clean_list(loi)
def get_annotation_role(bpmnfile,id):
   finale = []
   tache_liste = get_flow_node_refs_from_lane(bpmnfile,id)
   for i in tache_liste:
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
            message.append("erreur MI"+err+"# il manque le cas de superieur# voire l'article "+get_annotation(bpmn_file_path,i).__str__())
          if("&#60" not in content.__str__() and ("inferieur" not in content.__str__())):
            err += 1 
            message.append("erreur MI"+err+"#: il manque le cas de inferieur# voire l'article "+get_annotation(bpmn_file_path,i).__str__())
          if("=" not in content.__str__() and ("egale" not in content.__str__())):
            err += 1 
            message.append("erreur MI"+err+"#: il manque le cas de egale# voire l'article "+get_annotation(bpmn_file_path,i).__str__())
       if(verif_logique(bpmn_file_path,content.__str__(),i)):
          message.append(verif_logique(bpmn_file_path,content.__str__(),i))
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
                msg.append("missing information : "+re.search(r'<text>(.*?)</text>', lines[lines.index(line2)+1]).group(1))
   return msg
 
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
          message.append("Erreur MI " +str(err)+"# Condition manquante #"+"Condition non preciser dans l'article : "+get_annotation_proxy(bpmn_file_path,id).__str__()+"#Reviser l'article : "+get_annotation_proxy(bpmn_file_path,id).__str__()+" et Ajouter la condition adéquate")  
       else:
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
            for j in lines2:
              if((i in j) and ("<bpmndi:BPMNShape" in j)):
                err +=1
                modified_line =j[:-2]+' bioc:stroke="#6b3c00" bioc:fill="#ffe0b2" color:background-color="#ffe0b2" color:border-color="#6b3c00">\n'
                
                modified_lines.append(modified_line)
                if(get_annotation_role(bpmn_file_path,i).__len__() >0):
                 message.append("Erreur MI " +str(err)+"# Role manquant # Role non précisé dans l'article : "+get_annotation_role(bpmn_file_path,i).__str__()+"#Reviser l'article : "+get_annotation_role(bpmn_file_path,i).__str__()+" Ajouter le rôle adéquat a ces taches :"+get_nom_taches_role(bpmn_file_path,i).__str__())
                else:
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
    message1 = getways_ids2(bpmn_file_path,err)
    return message1 + message 
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
       # print(fs.path('loi.txt'))
        #le fichier avec first a la fin c'est avant verification
        arts = message(fs.path(uploaded_file.name).__str__(),fs.path(myfile+'first.bpmn'),fs.path('loi.txt').__str__())
        
        with open(fs.path(uploaded_file.name+".txt"), 'a') as f:
            for i in arts:
             f.write(i+" \n")
        annotation = modify_bpmn_file(fs.path(uploaded_file.name).__str__())
        liste_finale = arts + annotation
        report_name = uploaded_file.name + '.docx'
        report_name_eng = uploaded_file.name +'ENG'+ '.docx'
        report_path = os.path.join(settings.MEDIA_ROOT, report_name)
        #report_pathENG = os.path.join(settings.MEDIA_ROOT, report_name_eng)
        generer_rapport(liste_finale, report_path)
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

@api_view(['POST'])
def verify_diagram(request):
    if request.method == 'POST' and 'document' in request.FILES:


       # testPDF()
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()
        fs.save(uploaded_file.name,uploaded_file)
        myfile =os.path.splitext(uploaded_file.name)[0]
        fs.save(myfile+'first.bpmn',uploaded_file)
       # print(fs.path('loi.txt'))
        #le fichier avec first a la fin c'est avant verification
        arts = message(fs.path(uploaded_file.name).__str__(),fs.path(myfile+'first.bpmn'),fs.path('loi.txt').__str__())
        
        with open(fs.path(uploaded_file.name+".txt"), 'a') as f:
            for i in arts:
             f.write(i+" \n")
        annotation = modify_bpmn_file(fs.path(uploaded_file.name).__str__())
        liste_finale = arts + annotation
        report_name = uploaded_file.name + '.docx'
        report_name_eng = uploaded_file.name +'ENG'+ '.docx'
        report_path = os.path.join(settings.MEDIA_ROOT, report_name)
        #report_pathENG = os.path.join(settings.MEDIA_ROOT, report_name_eng)
        generer_rapport(liste_finale, report_path)
        #generer_rapportENG(liste_finale,report_pathENG)
        with open(fs.path(uploaded_file.name+".txt"), 'a') as f:
            for i in annotation:
             f.write(i+" \n")
        

       
        return JsonResponse({'filename': uploaded_file.name, 'annotations': annotation})
    else:
        return HttpResponse(status=400)