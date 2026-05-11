from django.contrib import admin

from .models import SiteConfiguration


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ("id", "max_discount_percentage")

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return not SiteConfiguration.objects.exists()
