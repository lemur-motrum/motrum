from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.logs.models import LogsAddProduct
from apps.product.models import Product

@receiver(post_save, sender=Product)
def add_logs_created(sender, instance, created, **kwargs):
     if created:
        log = LogsAddProduct.objects.create(product=instance.pk)
        print(f'New deal with pk: {instance.pk} was created.')