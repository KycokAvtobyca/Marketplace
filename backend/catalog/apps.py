from django.apps import AppConfig


class CatalogConfig(AppConfig):
    name = "catalog"
    verbose_name = '📦 Каталог'

    # Импорт сигналов
    def ready(self):
        import catalog.signals  # noqa: F401
