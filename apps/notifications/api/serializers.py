from rest_framework import serializers

from apps.notifications.models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Notification
        fields = "__all__"
        
class NotificationOrderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Notification
        fields = "__all__" 
    def to_representation(self, instance):
        representation = super(NotificationOrderSerializer, self).to_representation(instance)
        
        
        representation = representation.filter(type_notification="STATUS_ORDERING")
        return representation           