from django.shortcuts import render

# Create your views here.
def index(request):
    print(12313)
    context = {
        
    }
    return render(request, "core/index.html", context)