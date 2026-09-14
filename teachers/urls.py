from django.urls import path
from .views import teacher_list, register_teacher, teacher_self_register, teacher_detail, edit_teacher, permissions, delete_teacher

urlpatterns = [
    path('', teacher_list, name='teacher_list'),
    path('register/', register_teacher, name='register_teacher'),
    path('self-register/', teacher_self_register, name='teacher_self_register'),
    path('<int:pk>/', teacher_detail, name='teacher_detail'),
    path('<int:pk>/edit/', edit_teacher, name='edit_teacher'),
    path('<int:pk>/permissions/', permissions, name='teacher_permissions'),
    path('<int:pk>/delete/', delete_teacher, name='delete_teacher'),
]
