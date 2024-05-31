from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


#path("upload/",views.upload,name="upload")


urlpatterns = [
  path("", views.home, name="home"),
  path('api/csrf-token/', views.get_csrf_token, name='get_csrf_token'),
  path("upload/",views.upload,name="upload"),
    path("api/verify-diagram/", views.verify_diagram, name="verify_diagram"),
    path("api/diagram/", views.diagram, name="verify_diagram"),
    path("api/projects/", views.ProjectListCreateAPIView.as_view(), name="project-list-create"),
    path("api/projects/<int:project_id>/create-diagrams/", views.DiagramListCreateAPIView.as_view(), name='diagram-list-create'),
    path("api/projects/<int:pk>/", views.ProjectDetailAPIView.as_view(), name="project-detail"),
     path("api/projects/<int:project_id>/diagrams/", views.get_project_diagrams, name="get_project_diagrams"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
