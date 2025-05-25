from django.contrib import admin
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered

# Настройка заголовков админки
admin.site.site_header = "АЗС Администратор"
admin.site.site_title = "АЗС Администрирование"
admin.site.index_title = "Панель управления АЗС"

# Автоматическая регистрация всех моделей из приложения 'fuel'
app_models = apps.get_app_config('fuel').get_models()  

for model in app_models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
