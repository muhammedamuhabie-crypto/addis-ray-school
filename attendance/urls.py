from django.urls import path
from .views import take_attendance, attendance_records, student_attendance, attendance_report

urlpatterns = [
    path('take/', take_attendance, name='take_attendance'),
    path('records/', attendance_records, name='attendance_records'),
    path('report/', attendance_report, name='attendance_report'),
    path('student/', student_attendance, name='my_attendance'),
    path('student/<int:pk>/', student_attendance, name='student_attendance'),
]
