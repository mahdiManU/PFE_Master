# views.py
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
from .verification.structural import *
from .verification.structural import trouver_article
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework import generics, permissions
from .models import Project,Diagram
from .serializers import ProjectSerializer, DiagramSerializer
import logging
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from .rapport import *
from .verification.contradiction import *
from .rapportEng import *
from .add import *
from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import CreateUserSerializer
from .verification.bpmn_utils import supprimer_doublons, get_lane_id_from_flow_node, color_task, PALETTE_MISSING_INFO
from .verification.missing_info import modify_bpmn_file

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['password'] = User.objects.make_random_password()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['delete'])
    def delete_user(self, request, pk=None):
        user = self.get_object()
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
        arts ,artsENG = message(verified_file_path, verified_file_path, os.path.join(settings.MEDIA_ROOT, 'loi.txt'))
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
        arts ,artsENG= message(verified_file_path, verified_file_path, os.path.join(settings.MEDIA_ROOT, 'loi.txt'))
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