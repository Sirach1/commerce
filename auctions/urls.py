from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:category_id>", views.index, name="category"),
    path("closed", views.index, name="closed_index"),
    path("categories", views.category, name="categories"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listings/<int:id>", views.auction, name="auction"),
    path("listings/create", views.create, name="create"),
    path("watchlist", views.watchlist, name="watchlists")
]
