from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, User, Permission
from django.core.signals import request_finished
from django.contrib.auth.signals import user_logged_in


# @receiver(post_save, sender=User)
def update_group(sender, instance, created, **kwargs):
    from apps.user.models import ADMIN_TYPE

    for groupe_admin in ADMIN_TYPE:
        if instance.admin_type in groupe_admin:
            group = Group.objects.get(name=groupe_admin[1])

    if created:
        instance.groups.add(group)
    else:
        instance.groups.clear()
        instance.groups.add(group)
        
        
def user_admin_logged_in(sender, instance, created, **kwargs):
   pass       


# @receiver(user_logged_in) # Decorator of receiving signal while user going to logged in
# def post_login(sender, user, request, response, **kwargs):
#     response.set_cookie('team', 'india') # This will set cookie
#     return response