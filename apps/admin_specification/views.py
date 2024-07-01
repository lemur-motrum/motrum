from django.shortcuts import render

# Create your views here.

def specifications(request):
    title = "Услуги"
    responsets = [1221]
    context = {
        "title": title,
        "responsets": responsets,
    }
    return render(request, "admin_specification/test_admin_specification.html", context)
