from django.contrib import admin


class WebsiteAdminSite(admin.AdminSite):
   
    def get_app_list(self, request, app_label=None):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        ordering = {
            
            "Товары": 1,
            "Категории товаров": 2,
            "Группы товаров": 3,
            "Единицы измерений поставщиков": 4,
            
            "Администраторы": 5,
            "Клиенты": 6,
            "Логи": 7,
            "Логи ошибок": 8,
            "Валюты": 9,
            "Процент умножения валютных цен": 10,
            "НДС": 11,
            
            "Поставщики": 12,
            "Производители": 13,
             "Категории товаров у поставщика": 14,
            "Группы товаров у поставщика": 15,
            "Подгруппы поставщиков": 16,
            "Скидки": 17,
           
            
            
            "Скидки": 18,
            "Спецификации": 19,
            "Администраторы": 20,
        }
        app_dict = self._build_app_dict(request)
        # a.sort(key=lambda x: b.index(x[0]))
        # Sort the apps alphabetically.
        app_list = sorted(app_dict.values(), key=lambda x: x["name"].lower())

        # Sort the models alphabetically within each app.
        for app in app_list:
            app["models"].sort(key=lambda x: ordering[x["name"]])

        return app_list
