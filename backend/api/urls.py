from django.urls import include, path

urlpatterns = [
    path("catalog/", include("catalog.urls")),
    path("users/", include("users.urls")),
    path("cart/", include("carts.urls")),
    path("favorites/", include("favorites.urls")),
]
