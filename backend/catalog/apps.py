from django.apps import AppConfig


class CatalogConfig(AppConfig):
    name = "catalog"

    # Импорт сигналов
    def ready(self):
        import catalog.signals  # noqa: F401
