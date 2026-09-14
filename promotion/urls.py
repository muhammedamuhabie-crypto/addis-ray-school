from django.urls import path
from .views import promote_students,promotion_history
urlpatterns=[path('',promote_students,name='promote_students'),path('history/',promotion_history,name='promotion_history')]
