from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from .models import Project, Diagram


User = get_user_model()

class CreateUserSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'password']


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

    