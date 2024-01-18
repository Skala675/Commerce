from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("publish", views.publish, name="publish"),
    path("itm/<int:id>", views.product, name="product"),
    path("watchlist/<int:id>", views.watchlist, name="watchlist"),
    path("closeAuction/<int:id>", views.closeAuction, name="closeAuction"),
    path("offer/<int:id>", views.offer, name="offer"),
    path("comment/<int:id>", views.comment, name="comment"),
    path("watchlist", views.watchlistPage, name="watchlistPage"),
    path("category/<str:cat>", views.category, name="category")
]
