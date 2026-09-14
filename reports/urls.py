from django.urls import path
from .views import student_report,class_report,school_performance
urlpatterns=[path('student/',student_report,name='student_report'),path('class/',class_report,name='class_report'),path('school/',school_performance,name='school_performance')]
