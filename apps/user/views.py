from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login

from apps.user.forms import LoginAdminForm

# Create your views here.
def login_admin(request):
    next_url = request.POST.get('next')
    if request.method == 'POST':
        form = LoginAdminForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    
                    return HttpResponseRedirect(next_url) 
                    
                else:
                    return HttpResponse('Аккаунт заблокирован')
            else:
                return HttpResponse('Неверные пароль или логин')
    else:
        form = LoginAdminForm()
    return render(request, 'user/login_admin.html', {'form': form})