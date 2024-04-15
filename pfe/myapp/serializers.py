from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from .models import Project
from rest_framework import serializers


User = get_user_model()

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description']

def get_user_projects(user):
    projects = user.projects.all() 
    serializer = ProjectSerializer(projects, many=True)
    return serializer.data

class CreateUserSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'password']

