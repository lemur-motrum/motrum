import os
from django.conf import settings
from regex import F
from rest_framework import routers, serializers, viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.cache import cache
from django.contrib.auth import authenticate, login

from apps.client.api.serializers import (
    AccountRequisitesSerializer,
    AllAccountRequisitesSerializer,
    ClientRequisitesSerializer,
    ClientSerializer,
    RequisitesSerializer,
)
from apps.client.models import AccountRequisites, Client, Requisites
from apps.core.utils_web import _get_pin, _verify_pin, send_email_message, send_pin


class ApiClient(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    http_method_names = ["get", "post", "put", "update"]

    # def to_representation(self, instance):
    #     rep = super().to_representation(instance)
    #     rep["client"] = ClientSerializer(instance.client).data
    #     requisites_all = 11
    #     requisites = RequisitesSerializer(instance.purchased_by).data

    #     return rep

    # РЕГИСТРАЦИЯ ИЛИ АВТОРИЗАЦИЯ
    @action(detail=False, methods=["post"], url_path=r"login")
    def create_or_login_users(self, request, *args, **kwargs):
        data = request.data
        phone = data["phone"].replace(" ", "")
        pin_user = data["pin"]
        data["is_active"] = True
        data["username"] = phone
        # pin = _get_pin(4)
        pin = 1111
        cache.set(phone, pin, 120)
        # email ="a@ashvechkova.ru"
        # send_code = send_email_message(
        #     "Вход в личный кабинет на сайте Motrum",
        #     "Код для входа: " + str(pin),
        #     email
        # )

        # первый шаг отправка пин
        if pin_user == "":
            # cache.set(phone, pin, 120)
            # send_pin(pin, phone)
            return Response(pin, status=status.HTTP_200_OK)

        # сравнение пин и логин
        else:
            verify_pin = _verify_pin(phone, int(pin_user))
            # коды совпадают
            if verify_pin:
                serializer = self.serializer_class(data=data, many=False)
                # новый юзер
                if serializer.is_valid():
                    client = serializer.save()
                    client.add_manager()
                    
                    
                # старый юзер логин
                else:
                    client = Client.objects.get(username=phone)
                    serializer = ClientSerializer(client, many=False)

                if client.is_active:
                    if client.last_login:
                        login(request, client)
                        
                        # client.add_manager()
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    else:
                        login(request, client)
                        # client.add_manager()
                        return Response(serializer.data, status=status.HTTP_201_CREATED)

                else:
                    return Response(serializer.data, status=status.HTTP_403_FORBIDDEN)

            # коды не совпадают
            else:
                return Response(pin, status=status.HTTP_400_BAD_REQUEST)


class ApiClientRequisitesAccount(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientRequisitesSerializer
    http_method_names = ["get", "post", "update"]


class ApiRequisites(viewsets.ModelViewSet):
    queryset = Requisites.objects.all()
    serializer_class = RequisitesSerializer
    http_method_names = ["get", "post", "update"]

    def get_serializer(self, *args, **kwargs):
        # add many=True if the data is of type list
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(ApiRequisites, self).get_serializer(*args, **kwargs)

    @action(detail=False, methods=["post"], url_path=r"add")
    def add_all_requisites(self, request, *args, **kwargs):
        data = request.data
        i = -1
        valid_all = True
        serializer_data_new = []
        for data_item in data:
            i += 1
            requisites = data_item.get("requisites")

            account_requisites_data = data_item.get("account_requisites")

            serializer = self.serializer_class(data=requisites, many=False)
            
            if serializer.is_valid():

                requisites_item = serializer.save()
                serializer_data_new.append(serializer.data)
                
                for account_requisites_item in account_requisites_data:
                    account_requisites_item["requisites"] = requisites_item.id
               
                
                serializer_class_new = AccountRequisitesSerializer
                serializer = serializer_class_new(
                    data=account_requisites_data, many=True
                )
                if serializer.is_valid():
                    account_requisites_item = serializer.save()
                    serializer_data_new[i]["account_requisites"] = serializer.data
           
                else:
                    valid_all = False
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                valid_all = False
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if valid_all:
            return Response(serializer_data_new, status=status.HTTP_200_OK)

        
    @action(detail=True, methods=["update"], url_path=r"update")
    def update_requisites(self, request, pk=None, *args, **kwargs):
      
        queryset = Requisites.objects.get(pk=pk)
        data = request.data
        serializer_data_new = []
        valid_all = True
        
        for data_item in data:
            requisites = data_item.get("requisites")
            account_requisites_data = data_item.get("account_requisites")
            
            serializer =  self.serializer_class(queryset, data=requisites, partial=True)
            if serializer.is_valid():
                serializer.save()
                serializer_data_new.append(serializer.data)
                account_requisites = []

                for account_requisites_data_item in account_requisites_data:
                  
                    serializer_class_new = AccountRequisitesSerializer
                    queryset = AccountRequisites.objects.get(pk=account_requisites_data_item['id'])
                    serializer = serializer_class_new(
                        queryset, data=account_requisites_data_item, partial=True,
                    )
                    if serializer.is_valid():
                        account_requisites_item = serializer.save()
                        account_requisites.append(serializer.data)
                    
                    else:
                        valid_all = False
                        return Response(
                            serializer.errors, status=status.HTTP_400_BAD_REQUEST
                        )
            else:
                valid_all = False
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        

        if valid_all:
            serializer_data_new[0]["account_requisites"] = account_requisites
            return Response(serializer_data_new, status=status.HTTP_200_OK)
        
        
        
        
class ApiAccountRequisites(viewsets.ModelViewSet):
    queryset = AccountRequisites.objects.all()
    serializer_class = AccountRequisitesSerializer

    http_method_names = ["get", "post", "put", "update"]


# class ApiAllClientRequisites(viewsets.ModelViewSet):
#     queryset = Requisites.objects.all()
#     serializer_class = AllAccountRequisitesSerializer

#     http_method_names = ["get", "post", "put", "update"]

#     @action(detail=True, methods=["get"], url_path=r"requisites")
#     def get_all_requisites(self, request, pk=None, *args, **kwargs):
#         queryset = Requisites.objects.filter(client=pk)
#         serializer_class = AllAccountRequisitesSerializer
#         serializer = self.serializer_class(queryset, many=True)
#         return Response(serializer.data,status=status.HTTP_200_OK)


#     # def get_serializer(self, methods=["post"], *args, **kwargs):
#     #     print(11111)

#     #     # add many=True if the data is of type list
#     #     if isinstance(kwargs.get("data", {}), list):
#     #         kwargs["many"] = True

#     @action(detail=True, methods=["post"], url_path=r"add")
#     def save_new_requisites(self, request,pk=None, *args, **kwargs):
#         data = request.data
#         i = -1
#         # for data_item in data:
#         #     i+=1
#         #     requisites = data_item.get('requisites')

#         #     account_requisites_data = data_item.get('account_requisites')

#         #     serializer = self.serializer_class(data=requisites, many=False)
#         #     serializer_data = []
#         #     if serializer.is_valid():

#         #         requisites_item = serializer.save()
#         #         serializer_data.append(serializer.data)
#         #         account_requisites = {}
#         #         serializer_data[i]["account_requisites"] =  []
#         #         print(serializer_data[i])
#         #         for account_requisites_item in account_requisites_data:
#         #             account_requisites_item["requisites"] = requisites_item.id

#         #         serializer_class_new = AccountRequisitesSerializer
#         #         serializer = serializer_class_new(data=account_requisites_data, many=True)
#         #         if serializer.is_valid():

#         #             account_requisites_item = serializer.save()
#         #             serializer_data[i]["account_requisites"].append(serializer.data)
#         #             return Response(serializer_data,status=status.HTTP_200_OK)
#         #         else:
#         #             return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

#         #     else:

#         #         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


#         return Response(data,status=status.HTTP_200_OK)
