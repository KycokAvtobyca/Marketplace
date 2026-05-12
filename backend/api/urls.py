from django.urls import include, path
from . import views

urlpatterns = [
    path("catalog/", include("catalog.urls")),
    path("users/", include("users.urls")),
    path("cart/", include("carts.urls")),
    path("favorites/", include("favorites.urls")),
    path("orders/", include("orders.urls")),
    # Admin integration
    path("admin-redirect/", views.admin_redirect, name="admin_redirect"),
    path("check-admin-access/", views.check_admin_access, name="check_admin_access"),
]

