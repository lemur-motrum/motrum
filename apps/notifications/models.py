from django.db import models


from apps.client.models import Client, Order
from apps.core.utils_web import send_email_message_html

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
    
    is_viewed = models.BooleanField("Прочитано", default=False)

    class Meta:
        verbose_name = "Уведомление"  
        verbose_name_plural = "Уведомления"
        ordering = ("is_viewed", "-date")    
    
    @staticmethod
    def add_notification(order,type_notification):
        order = Order.objects.get(id=order)
        client = order.client
        
        Notification.objects.create(
            order=order,
            client=client,
            type_notification=type_notification,
        )
        name_notification =  None
        for name_notifications in TYPE_NOTIFICATION:
            if type_notification in name_notifications:
                name_notification =  name_notifications
                
        print(name_notification)
        title_email = f"У вашего заказа {order.name} новый "
        text_email = f"Клиент: {client.contact_name}Телефон: {client.phone}Сообщение{text_message}"
        
        send_email_message_html(
            title_email, text_email, to_manager, html_message=html_message
        )
        