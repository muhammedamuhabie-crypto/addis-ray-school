from django.urls import path

from .views import (
    login_view,
    logout_view,
    forgot_username,
    user_accounts,
    school_settings,
    SchoolPasswordResetView,
    SchoolPasswordResetDoneView,
    SchoolPasswordResetConfirmView,
    SchoolPasswordResetCompleteView,
)


urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path(
        'forgot-password/',
        SchoolPasswordResetView.as_view(),
        name='forgot_password'
    ),

    path(
        'forgot-password/done/',
        SchoolPasswordResetDoneView.as_view(),
        name='password_reset_done'
    ),

    path(
        'reset/<uidb64>/<token>/',
        SchoolPasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),

    path(
        'reset/complete/',
        SchoolPasswordResetCompleteView.as_view(),
        name='password_reset_complete'
    ),

    path(
        'forgot-username/',
        forgot_username,
        name='forgot_username'
    ),

    path('users/', user_accounts, name='user_accounts'),
    path('settings/', school_settings, name='school_settings'),
]
