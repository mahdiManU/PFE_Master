from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import ProjectListCreateAPIView, ProjectDetailAPIView

#path("upload/",views.upload,name="upload")
urlpatterns = [
    path("",views.home, name="home"),
    path('api/verify-diagram/', views.verify_diagram, name='verify_diagram'),
    path('api/diagram/', views.diagram, name='verify_diagram'),
    path('api/projects/', views.projects_api, name='projects_api'),
    path('api/projects/', ProjectListCreateAPIView.as_view(), name='project-list-create'),
    path('api/projects/<int:pk>/', ProjectDetailAPIView.as_view(), name='project-detail'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
