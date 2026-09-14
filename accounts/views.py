from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.db.models import Q
from django.urls import reverse_lazy

from .forms import (
    LoginForm,
    UsernameRecoveryForm,
    CreateUserForm,
    SchoolSettingsForm,
)
from .models import User
from students.models import Student


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('dashboard')

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


class SchoolPasswordResetView(PasswordResetView):
    template_name = 'accounts/forgot_password.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')


class SchoolPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class SchoolPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class SchoolPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'


def forgot_username(request):
    form = UsernameRecoveryForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']

        user = User.objects.filter(email=email).first()

        if user:
            send_mail(
                'Addis Ray username recovery',
                (
                    f'Hello {user.get_full_name() or user.username},\n\n'
                    f'Your Addis Ray Secondary School username is: '
                    f'{user.username}\n\n'
                    'If you did not request this information, '
                    'please contact the school administration.'
                ),
                'noreply@addisray.local',
                [user.email],
                fail_silently=True,
            )

        messages.success(
            request,
            'If an account exists with that email, '
            'the username has been sent to the registered email address.'
        )

        return redirect('login')

    return render(
        request,
        'accounts/forgot_username.html',
        {'form': form}
    )


@login_required
def user_accounts(request):
    if request.user.role != 'DIRECTOR':
        messages.error(
            request,
            'Director permission required.'
        )
        return redirect('dashboard')

    form = CreateUserForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()

        messages.success(
            request,
            'User account created successfully.'
        )

        return redirect('user_accounts')

    users = User.objects.all().order_by(
        'role',
        'email'
    )

    student_search = request.GET.get(
        'student_search',
        ''
    ).strip()

    student_accounts = Student.objects.select_related(
        'user'
    ).all().order_by(
        'first_name',
        'father_name',
        'grandfather_name'
    )

    if student_search:
        student_accounts = student_accounts.filter(
            Q(first_name__icontains=student_search) |
            Q(father_name__icontains=student_search) |
            Q(grandfather_name__icontains=student_search) |
            Q(student_id__icontains=student_search)
        )

    return render(
        request,
        'accounts/user_accounts.html',
        {
            'users': users,
            'form': form,
            'student_accounts': student_accounts,
            'student_search': student_search,
        }
    )


@login_required
def school_settings(request):
    if request.user.role != 'DIRECTOR':
        messages.error(
            request,
            'Director permission required.'
        )
        return redirect('dashboard')

    from .models import SchoolSettings

    settings = SchoolSettings.objects.first()

    if settings is None:
        settings = SchoolSettings.objects.create()

    form = SchoolSettingsForm(
        request.POST or None,
        request.FILES or None,
        instance=settings
    )

    if request.method == 'POST' and form.is_valid():
        form.save()

        messages.success(
            request,
            'School settings updated successfully.'
        )

        return redirect('school_settings')

    return render(
        request,
        'accounts/settings.html',
        {
            'form': form,
            'settings': settings,
        }
    )

