from django.shortcuts import render

# Create your views here.
# Create your views here.
def index(request):

    context = {}

    context = {}
    return render(request, "core/index.html", context)