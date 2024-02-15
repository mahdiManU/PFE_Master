from django.shortcuts import render , HttpResponse
from django.core.files.storage import FileSystemStorage
# Create your views here.
def home(request):
    return render(request ,"home.html")
def upload(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()
        fs.save(uploaded_file.name,uploaded_file)
        return render(request, 'upload_success.html',{'file_name': uploaded_file.name})
    return render(request ,"upload.html")

