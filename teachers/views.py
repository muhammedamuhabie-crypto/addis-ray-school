import secrets,string
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404,render,redirect
from accounts.models import User
from .models import TeacherProfile
from .forms import TeacherForm,PermissionForm

def pwd(): return ''.join(secrets.choice(string.ascii_letters+string.digits) for _ in range(10))

def director_required(request):
    return request.user.role=='DIRECTOR'

@login_required
def teacher_list(request):
    return render(request,'teachers/teacher_list.html',{'teachers':TeacherProfile.objects.all().order_by('first_name')})

@login_required
@login_required
def register_teacher(request):
    if not director_required(request):
        messages.error(request, 'Director permission required.')
        return redirect('teacher_list')

    form = TeacherForm(
        request.POST or None,
        request.FILES or None
    )

    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data

        with transaction.atomic():
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['father_name'],
                role='TEACHER'
            )

            teacher = form.save(commit=False)
            teacher.user = user
            teacher.save()

        messages.success(
            request,
            f'Teacher account created successfully for {user.username}.'
        )

        return redirect(
            'teacher_detail',
            teacher.pk
        )

    return render(
        request,
        'teachers/register_teacher.html',
        {'form': form}
    )


def teacher_self_register(request):
    if (
        request.user.is_authenticated
        and request.user.role in ['DIRECTOR', 'TEACHER']
    ):
        messages.error(
            request,
            'You already have a school account.'
        )
        return redirect('dashboard')

    form = TeacherForm(
        request.POST or None,
        request.FILES or None
    )

    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data

        with transaction.atomic():
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['father_name'],
                role='TEACHER'
            )

            teacher = form.save(commit=False)
            teacher.user = user
            teacher.save()

        messages.success(
            request,
            'Teacher account created successfully. '
            'You can now log in using your username and password.'
        )

        return redirect('login')

    return render(
        request,
        'teachers/teacher_self_register.html',
        {'form': form}
    )


@login_required
def teacher_detail(request,pk):
    return render(
        request,
        'teachers/teacher_detail.html',
        {'teacher':get_object_or_404(TeacherProfile,pk=pk)}
    )


@login_required
def edit_teacher(request,pk):
    if not director_required(request):
        messages.error(
            request,
            'Director permission required.'
        )
        return redirect('dashboard')

    teacher=get_object_or_404(TeacherProfile,pk=pk)
    form=TeacherForm(
        request.POST or None,
        request.FILES or None,
        instance=teacher
    )
    form.fields['email'].initial=teacher.user.email

    if request.method=='POST' and form.is_valid():
        teacher=form.save()
        teacher.user.email=form.cleaned_data['email']
        teacher.user.save()
        messages.success(request,'Teacher updated.')
        return redirect('teacher_detail',pk)

    return render(
        request,
        'teachers/edit_teacher.html',
        {'form':form,'teacher':teacher}
    )


@login_required
def permissions(request,pk):
    if not director_required(request):
        messages.error(request,'Director permission required.')
        return redirect('dashboard')

    teacher=get_object_or_404(TeacherProfile,pk=pk)
    form=PermissionForm(request.POST or None,instance=teacher)

    if request.method=='POST' and form.is_valid():
        form.save()
        messages.success(request,'Teacher permissions updated.')
        return redirect('teacher_detail',pk)

    return render(
        request,
        'teachers/permissions.html',
        {'form':form,'teacher':teacher}
    )



@login_required
def delete_teacher(request, pk):
    if request.user.role != "DIRECTOR":
        return HttpResponseForbidden("Only the Director can delete teachers.")

    if request.method != "POST":
        return redirect("teacher_detail", pk=pk)

    teacher = get_object_or_404(TeacherProfile, pk=pk)
    user = teacher.user
    teacher.delete()
    if user:
        user.delete()

    return redirect("teacher_list")