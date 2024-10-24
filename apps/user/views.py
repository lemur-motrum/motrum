from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.urls import reverse
from apps.user.forms import LoginAdminForm
from apps.user.models import AdminUser


# логин админа
def login_admin(request):
    form = LoginAdminForm()
    next_url = request.POST.get("next")
    id_bitrix = request.GET.get("id_bitrix")

    # если логин через битрикс
    if id_bitrix:
        redirects = login_bitrix(request, next_url, id_bitrix)
        return redirects

    # если вход не через битрикс
    else:
        if request.method == "POST":
            # после войти в форме входа
            redirects = login_clear(request, next_url, form)
            return redirects
        # форма входа
        else:
            context = {
                "error": "",
            }
            return form_login(request, context, form)


# разлогин админа
def logout_admin(request):
    logout(request)
    
    return redirect(reverse("user:login_admin") + "?next=/admin_specification/")


# форма для логина
def form_login(request, context, form):
    return render(request, "user/login_admin.html", {"form": form, "context": context})


def login_clear(request, next_url, form):

    form = LoginAdminForm(request.POST)
    if next_url == None:
        next_url = "/admin_specification/"
    print(next_url)
    if form.is_valid():
        cd = form.cleaned_data
        user = authenticate(username=cd["username"], password=cd["password"])
        # если прошел аутентификация
        if user is not None:
            # если не заблокирова
            if user.is_active:
                login(request, user)
                is_groups_user = user.groups.filter(
                    name__in=["Полный доступ", "Базовый доступ"]
                ).exists()

                # если есть право на просмотр спецификаций
                if is_groups_user == True:
                    cookie = request.COOKIES.get("client_id")
                    response = redirect(next_url)
                    response.set_cookie('client_id', max_age=-1)
                    response.set_cookie('cart', max_age=-1)
                   
                    return response
                    # if cookie:
                    #     response = redirect(next_url) # replace redirect with HttpResponse or render
                    #     response.set_cookie('client_id', cookie, max_age=-1)
                        
                    #     return response
                    # else:
                    #     return response
                        # return HttpResponseRedirect(next_url)

                # нет права на спецификации
                else:
                    request.GET._mutable = True
                    request.GET["next"] = next_url
                    context = {
                        "error": "У вас нет прав доступа ",
                    }
                    return render(
                        request,
                        "user/login_admin.html",
                        {"form": form, "context": context},
                    )

            # заблокирован пользователь
            else:
                request.GET._mutable = True
                request.GET["next"] = next_url
                context = {
                    "error": "Аккаунт заблокирован",
                }
                return render(
                    request,
                    "user/login_admin.html",
                    {"form": form, "context": context},
                )
        # если отказ в аутентификации
        else:
            request.GET._mutable = True
            request.GET["next"] = next_url
            context = {
                "error": " Неверные пароль или логин",
            }
            return render(
                request, "user/login_admin.html", {"form": form, "context": context}
            )


def login_bitrix(request, next_url, id_bitrix):

    next_url = request.GET.get("next")

    if id_bitrix == "2":
        user = AdminUser.objects.get(username="admin")
        login(request, user)
        return HttpResponseRedirect(next_url)
    else:
        form = LoginAdminForm()
        context = {
            "error": "Ошибка доступа из Битрикс. Пожалуйста авторизуйтесь заново",
        }
        return form_login(request, context, form)
