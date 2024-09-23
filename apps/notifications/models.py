from django.db import models


from apps.client.models import Client, Order

# Create your models here.

TYPE_NOTIFICATION = (
    ("DOCUMENT_SPECIFICATION", "DOCUMENT_SPECIFICATION"),
    ("DOCUMENT_BILL", "DOCUMENT_BILL"),
    ("DOCUMENT_ACT", "DOCUMENT_ACT"),
    ("STATUS_ORDERING", "STATUS_ORDERING"),
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