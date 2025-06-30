from django.contrib import admin
from django.template.response import TemplateResponse

# админка бд
class DatabaseAdminSite(admin.AdminSite):
   
    def get_app_list(self, request, app_label=None):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        ordering_main = {
        }
        ordering = {
            
            "Товары": 1,
            "Категории товаров": 2,
            "Группы товаров": 3,
            "Единицы измерений поставщиков": 4,
            "Характеристики товаров мотрум": 4,
            
            "Администраторы": 5,
            "Клиенты на сайте": 6,
            "Реквизиты": 6,
            "Расчётные счёта":6,
            "Типы доставок":7,
        
            "Логи": 7,
            "Логи ошибок": 8,
            "Логи добавления товара": 8,
            "Информационные сообщения":8,
            "Логи фоновые по сделкам":8,
            
            "Валюты": 9,
            "Процент умножения валютных цен": 10,
            "НДС": 11,
            "Юридические лица": 19,
            "Базовые изображения для документов": 19,
            
            "Поставщики": 12,
            "Производители": 13,
             "Категории товаров у поставщика": 14,
            "Группы товаров у поставщика": 15,
            "Подгруппы поставщиков": 16,
            "Промо группы":17,
        

            
            "Скидки": 18,
  
            "Администраторы": 20,
        }
        app_dict = self._build_app_dict(request)
      
        app_list = app_dict.values()

        
        app_list = sorted(app_dict.values(), key=lambda x: x["name"].lower())

        for app in app_list:
            app["models"].sort(key=lambda x: ordering[x["name"]])

        return app_list
    
    
    def index(self, request, extra_context=None):
        """
        Display the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """
        app_list = self.get_app_list(request)

        context = {
            **self.each_context(request),
            "title": self.index_title,
            "subtitle": None,
            "app_list": app_list,
            **(extra_context or {}),
        }

        request.current_app = self.name
        
        # УДАЛЕНИЕ КУК С КАРТ И КЛИЕНТ ПРИ ЛОГИНЕ АДМИНА 
        
        current_user = request.user
        if current_user.is_staff:
            cookie = request.COOKIES.get("client_id")
            if cookie:
                response = TemplateResponse(request, self.index_template or "admin/index.html", context)
                # НЕ РАБОТАЕТ работает тут def login_clear
               
                response.set_cookie('client_id', max_age=-1)
                response.set_cookie('cart', max_age=-1)
                response.set_cookie('specificationId', max_age=-1)          
                return response
            else:
                return TemplateResponse(
                request, self.index_template or "admin/index.html", context
            )
        else:
            return TemplateResponse(
                request, self.index_template or "admin/index.html", context
            )
        
# админка сайта
class WebsiteAdminSite(admin.AdminSite):
    def log_addition(self, request, object, message):
        pass  # Disables logging of additions

    def log_change(self, request, object, message):
        pass  # Disables logging of changes

    def log_deletion(self, request, object, object_repr):
        pass  # Disables logging of deletions

website_admin = WebsiteAdminSite(name="website_admin")   