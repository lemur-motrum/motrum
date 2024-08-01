from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.urls import reverse
from apps.user.forms import LoginAdminForm


# логин админа
def login_admin(request):
    form = LoginAdminForm()
    next_url = request.POST.get("next")
    print(next_url)
    if request.method == "POST":
        form = LoginAdminForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd["username"], password=cd["password"])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    is_groups_user = user.groups.filter(
                        name__in=["Полный доступ", "Базовый доступ"]
                    ).exists()
                    print(is_groups_user)
                    if is_groups_user == True:
                        return HttpResponseRedirect(next_url)
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
            else:
                request.GET._mutable = True
                request.GET["next"] = next_url
                context = {
                    "error": " Неверные пароль или логин",
                }
                return render(
                    request, "user/login_admin.html", {"form": form, "context": context}
                )
    else:
        context = {
            "error": "",
        }
    return render(request, "user/login_admin.html", {"form": form, "context": context})

# разлогин админа
def logout_admin(request):
    logout(request)
    return redirect(reverse("user:login_admin") + "?next=/admin_specification/")
