
from django.conf import settings
from django.core.cache import cache
import os
import random
from django.core.mail import send_mail

from django.http import HttpResponse
from project.settings import MEDIA_ROOT


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
    print(settings.EMAIL_HOST_USER,)
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