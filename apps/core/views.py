from django.shortcuts import render

# Create your views here.
def index(request):
   
    context = {  
    }
    return render(request, "core/index.html", context)

def okt(request):
   
    context = {  
    }
    return render(request, "core/okt.html", context)

def web(request):
   
    context = {  
    }
    return render(request, "core/web.html", context)



