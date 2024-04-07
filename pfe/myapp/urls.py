from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

#path("upload/",views.upload,name="upload")
urlpatterns = [
    path("",views.home, name="home"),
    path('api/verify-diagram/', views.verify_diagram, name='verify_diagram'),
    path('api/diagram/', views.diagram, name='verify_diagram'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
