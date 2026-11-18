from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
import os

# Create your models here.

class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(_("First Name"), max_length=100)
    last_name = models.CharField(_("Last Name"), max_length=100)
    email = models.EmailField(_("Email Address"), max_length=254, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined =  models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

def diagram_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<user_id>/project_<project_id>/diagram_<diagram_id>/<filename>
    return f'user_{instance.project.owner.id}/project_{instance.project.id}/diagram_{instance.id}/{filename}'

class Diagram(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    verified = models.BooleanField(default=False)
    file = models.FileField(upload_to=diagram_directory_path)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='diagrams')  # Use `project` here

    def __str__(self):
        return self.name

@receiver(post_save, sender=User)
def create_user_directory(sender, instance, created, **kwargs):
    if created:
        user_directory = os.path.join(settings.MEDIA_ROOT, f'user_{instance.id}')
        os.makedirs(user_directory, exist_ok=True)

@receiver(post_save, sender=Project)
def create_project_directory(sender, instance, created, **kwargs):
    if created:
        user_directory = os.path.join(settings.MEDIA_ROOT, f'user_{instance.owner.id}')
        project_directory = os.path.join(user_directory, f'project_{instance.id}')
        os.makedirs(project_directory, exist_ok=True)

@receiver(post_save, sender=Diagram)
def create_diagram_directory(sender, instance, created, **kwargs):
    """
    After the first save the diagram id is known, so move the uploaded file from
    user_X/project_Y/diagram_None/ to user_X/project_Y/diagram_<id>/.
    The database must store a path RELATIVE to MEDIA_ROOT (never C:\\...),
    otherwise the project breaks as soon as it is copied to another machine.
    """
    if not created or not instance.file:
        return

    project_dir = os.path.join(
        settings.MEDIA_ROOT, f'user_{instance.project.owner.id}', f'project_{instance.project.id}')
    diagram_dir = os.path.join(project_dir, f'diagram_{instance.id}')
    os.makedirs(diagram_dir, exist_ok=True)

    old_path = instance.file.path
    filename = os.path.basename(old_path)
    new_path = os.path.join(diagram_dir, filename)
    if os.path.abspath(old_path) != os.path.abspath(new_path):
        os.replace(old_path, new_path)  # also overwrites on Windows

    new_name = f'user_{instance.project.owner.id}/project_{instance.project.id}/diagram_{instance.id}/{filename}'
    Diagram.objects.filter(pk=instance.pk).update(file=new_name)
    instance.file.name = new_name

    none_dir = os.path.join(project_dir, 'diagram_None')
    if os.path.isdir(none_dir) and not os.listdir(none_dir):
        os.rmdir(none_dir)





