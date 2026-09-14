from django.urls import path
from .views import (
    classes,
    subjects,
    enter_grade,
    grade_records,
    student_results,
    ranking,
    load_students,
    edit_subject,
    delete_subject,
    edit_class,
    delete_class
)

urlpatterns = [
    path('classes/<int:pk>/edit/', edit_class, name='edit_class'),
    path('classes/<int:pk>/delete/', delete_class, name='delete_class'),
    path('subjects/<int:pk>/edit/', edit_subject, name='edit_subject'),
    path('subjects/<int:pk>/delete/', delete_subject, name='delete_subject'),
    path(
        'classes/',
        classes,
        name='classes'
    ),

    path(
        'subjects/',
        subjects,
        name='subjects'
    ),

    path(
        'grades/enter/',
        enter_grade,
        name='enter_grade'
    ),

    path(
        'grades/load-students/',
        load_students,
        name='load_students'
    ),

    path(
        'grades/',
        grade_records,
        name='grade_records'
    ),

    path(
        'results/',
        student_results,
        name='my_results'
    ),

    path(
        'results/<int:pk>/',
        student_results,
        name='student_results'
    ),

    path(
        'ranking/',
        ranking,
        name='ranking'
    ),
]


