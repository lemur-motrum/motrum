
from django.conf import settings
from django.core.cache import cache
import os
import random
from django.core.mail import send_mail
from django.core.mail import EmailMessage

from django.http import HttpResponse


from project.settings import MEDIA_ROOT

# загрузка катринок для разделов каталога 
def get_file_path_catalog_web(instance, filename):
    from apps.product.models import CategoryProduct
    from apps.product.models import GroupProduct

    base_dir = "website/catalog"
    type_dir = instance._meta.object_name
    filenames = instance.slug
    images_last_list = filename.split(".")
    type_file = "." + images_last_list[-1]
    filename = f"{filenames}{type_file}"
    check_media_directory_exist_web(base_dir, type_dir)
    return "{0}/{1}/{2}".format(
        base_dir,
        type_dir,
        filename,
    )
    
# загрузка катринок для проектов
def get_file_path_project_web(instance, filename):
    from apps.projects_web.models import Project,ProjectImage,CategoryProject,ClientCategoryProject
    if isinstance(instance, Project):
        base_dir = "website/project"
        filenames = F"{instance.slug}_main"
        type_dir = F"{instance.slug}"
      
    elif isinstance(instance, ProjectImage):
        base_dir = "website/project"
        project = Project.objects.get(id=instance.project.id)
        # number_project = int(project.id)
        project_img = ProjectImage.objects.filter(project=project).count()
        number_image= int(project_img) + 1
        
        type_dir = F"{instance.project.slug}"
        filenames = F"{instance.project.slug}__{number_image}"
        print(filenames)
    elif isinstance(instance, CategoryProject) or isinstance(instance, ClientCategoryProject):
        base_dir = "website/project/categories"
        type_dir = F"{instance.slug}"
        filenames = F"{instance.slug}"
 
    images_last_list = filename.split(".")
    type_file = "." + images_last_list[-1]
    filename = f"{filenames}{type_file}"
    print(type_file)
    print(filename)
    
    check_media_directory_exist_web(base_dir, type_dir)
    return "{0}/{1}/{2}".format(
        base_dir,
        type_dir,
        filename,
    )   
    
# загрузка катринок для слайдера
def get_file_path_slider_web(instance, filename): 
    print(instance.slug)       
    base_dir = "website/slider"
    filenames = F"{instance.slug}"
    type_dir = F"{instance.slug}"
    
    images_last_list = filename.split(".")
    type_file = "." + images_last_list[-1]
    filename = f"{filenames}{type_file}"
    
    check_media_directory_exist_web(base_dir, type_dir)
    return "{0}/{1}/{2}".format(
        base_dir,
        type_dir,
        filename,
    )   


# проверка есть ли путь и папка
def check_media_directory_exist_web(base_dir, type_dir):
    new_dir = "{0}/{1}/{2}".format(
        MEDIA_ROOT,
        base_dir,
        type_dir,
    )
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

def _get_pin(length=5):
    # Возвращает числовой PIN-код длиной в цифрах или базово 5 
    return random.sample(range(10**(length-1), 10**length), 1)[0]

def  _verify_pin ( mobile_number ,  pin ): 
    """ Проверяет правильность PIN-кода """ 
    return  pin  ==  cache . get ( mobile_number ) 

def send_pin( pin,mobile_number):
    """ Sends SMS PIN to the specified number """
    # mobile_number = request.POST.get('mobile_number', "")
    # if not mobile_number:
    #     return HttpResponse("No mobile number", mimetype='text/plain', status=403)

    # store the PIN in the cache for later verification.
    cache.set(mobile_number, pin, 120) 
    
    # client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    # message = client.messages.create(
    #                     body="%s" % pin,
    #                     to=mobile_number,
    #                     from_=settings.TWILIO_FROM_NUMBER,
    #                 )
    # return HttpResponse("Message %s sent" % 123123, mimetype='text/plain', status=200)
    return "пин отправлен"

def send_email_message(subject, message, to_email):

    send_result = send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [to_email],
        fail_silently=False,
    )
    

    if send_result == 1:
        return True
    else:
        return False
    
def send_email_message_and_file(subject, message, to_email, file):

    email = EmailMessage(
    subject, 
    message, 
    settings.EMAIL_HOST_USER, 
    [to_email])
    email.attach_file(file)
    email.send()
 
    return email    

def send_email_message_html(subject, message, to_email,html_message):

    send_result = send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [to_email],
        fail_silently=True,
        html_message=html_message,
    )
    

    if send_result == 1:
        return True
    else:
        return False
    
def promote_product_slider(product):
    from apps.core.models import SliderMain
    if product.promote:
        name = f"Товар {product.name}"
        try:
            slider = SliderMain.objects.get(product_promote=product,type_slider="PROMOTE")
            if slider.active == False:
                slider.active == True
                slider.save()
        except SliderMain.DoesNotExist:
            slider = SliderMain(active=True,name= name,type_slider="PROMOTE",product_promote=product)
            slider.save()
        #     SliderMain.objects.update_or_create( product_promote=product,type_slider="PROMOTE",
        #     defaults={'active': True,"name": name},
        # )
    else:
        pass
    
# def email_callback():
#     pass    
