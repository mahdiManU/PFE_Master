from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from .models import Project, Diagram


User = get_user_model()

class CreateUserSerializer(UserCreateSerializer):
    num_projects = serializers.SerializerMethodField()
    num_completed_projects = serializers.SerializerMethodField()
    
    

    def get_num_projects(self, obj):
        return Project.objects.filter(owner=obj).count()

    def get_num_completed_projects(self, obj):
        projects = Project.objects.filter(owner=obj)
        completed_projects = 0
        for project in projects:
            if all(diagram.verified for diagram in project.diagrams.all()):
                completed_projects += 1
        return completed_projects
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'password', 'is_active', 'num_projects', 'num_completed_projects']

class ProjectSerializer(serializers.ModelSerializer):
    num_diagrams = serializers.SerializerMethodField()

    def get_num_diagrams(self, obj):
        return obj.diagrams.count()

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'owner', 'created_at', 'updated_at', 'num_diagrams']
        

class DiagramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagram
        fields = ['id', 'name', 'description', 'file', 'verified']  # Exclude 'project_id'
        read_only_fields = ['project']

    