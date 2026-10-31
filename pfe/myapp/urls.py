from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


#path("upload/",views.upload,name="upload")


urlpatterns = [
  path("upload/",views.upload,name="upload"),
  path("", views.home, name="home"),
  path('api/upload/verify/', views.upload_and_verify_diagram, name="upload_and_verify_diagram"),
  path("api/projects/<int:project_id>/diagrams/<int:diagram_id>/verify/", views.verify_diagram, name="verify_diagram"),
    path("api/diagram/", views.diagram, name="diagram_upload"),
    path("api/projects/", views.ProjectListCreateAPIView.as_view(), name="project-list-create"),
    path("api/projects/<int:project_id>/create-diagrams/", views.DiagramListCreateAPIView.as_view(), name='diagram-list-create'),
    path("api/projects/<int:project_id>/diagrams/<int:id>/", views.DiagramDetailAPIView.as_view(), name="diagram-detail"),
    path('api/projects/<int:project_id>/diagrams/<int:diagram_id>/info/', views.get_diagram, name='get_diagram'),
    path("api/projects/<int:pk>/", views.ProjectDetailAPIView.as_view(), name="project-detail"),
     path("api/projects/<int:project_id>/diagrams/", views.get_project_diagrams, name="get_project_diagrams"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
