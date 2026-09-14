from django.urls import path

from . import views


urlpatterns = [
    path("", views.announcement_list, name="announcement_list"),
    path("create/", views.announcement_create, name="announcement_create"),
    path("edit/<int:pk>/", views.announcement_edit, name="announcement_edit"),
    path("delete/<int:pk>/", views.announcement_delete, name="announcement_delete"),
]
