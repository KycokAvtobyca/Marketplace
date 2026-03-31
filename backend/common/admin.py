from django.contrib import admin

from .models import SiteConfiguration


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    # Запрещаем удалять настройки, чтобы сайт не упал
    def has_delete_permission(self, request, obj=None):
        return False

    # Запрещаем добавлять новые, если одна уже есть
    def has_add_permission(self, request):
        return not SiteConfiguration.objects.exists()
