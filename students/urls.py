from django.urls import path
from .views import (
    student_list,
    register_student,
    student_detail,
    edit_student,
    delete_student,
    filter_students
)

urlpatterns = [
    path('', student_list, name='student_list'),
    path('register/', register_student, name='register_student'),
    path('filter/', filter_students, name='filter_students'),
    path('<int:pk>/', student_detail, name='student_detail'),
    path('<int:pk>/edit/', edit_student, name='edit_student'),
    path('<int:pk>/delete/', delete_student, name='delete_student'),
]
