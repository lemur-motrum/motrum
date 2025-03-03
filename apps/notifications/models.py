from django.db import models
from middlewares.middlewares import RequestMiddleware


from apps.client.models import Client, Order
from apps.core.utils_web import send_email_message_html
from django.template import loader
# Create your models here.

TYPE_NOTIFICATION = (
    ("DOCUMENT_SPECIFICATION", "документ спецификации"),
    ("DOCUMENT_BILL", "документ счета"),
    ("DOCUMENT_ACT", "документ акта"),
    ("STATUS_ORDERING", "статус заказа"),
)
class Notification(models.Model):
    client = models.ForeignKey(Client, verbose_name="Клиент", on_delete=models.CASCADE)
    
    order = models.ForeignKey(Order, verbose_name="Заказ", on_delete=models.CASCADE)
    date = models.DateTimeField("Дата и время", auto_now_add=True)
    type_notification = models.CharField(
        max_length=100, choices=TYPE_NOTIFICATION, default="STATUS_ORDERING"
    )
    file = models.CharField(
        max_length=5000, 
        blank=True,
        null=True,
    )
    
    is_viewed = models.BooleanField("Прочитано", default=False)

    class Meta:
        verbose_name = "Уведомление"  
        verbose_name_plural = "Уведомления"
        ordering = ("is_viewed", "-date")    
    
    @staticmethod
    def add_notification(order,type_notification,file):
        request = RequestMiddleware(get_response=None)
        request = request.thread_local.current_request

        order = Order.objects.get(id=order)
        client = order.client
        
        Notification.objects.create(
            order=order,
            client=client,
            file=file,
            type_notification=type_notification,
        )
        name_notification =  None
        link = ""
        for name_notifications in TYPE_NOTIFICATION:
            
            if type_notification in name_notifications:
                print(name_notifications)
                name_notification =  name_notifications[1]
                if name_notifications[0] == "STATUS_ORDERING":
                    link = "/lk/my_orders"
                    # client.is_status_notification_counter = True
                    # client.save() 
                else:
                    link = "/lk/my_documents"    
                    
        url_absolute = request.build_absolute_uri('/').strip("/")
        link = f'{url_absolute}/{link}'        
       
        title_email = f"У вашего заказа {order.name} на сайте Motrum новый {name_notification}"
        text_email = f"У вашего заказа {order.name} на сайте Motrum новый {name_notification}"
        to_client = client.email
        
        
        html_message = loader.render_to_string(
            "core/emails/email_client_status.html",
            {
                "text": text_email,
                "link" : link,
            },
        )
        
        # result = send_email_message_html(
        #     title_email, text_email, to_client, html_message=html_message
        # )
        
        