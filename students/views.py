import secrets
import string

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect

from accounts.models import User
from teachers.models import TeacherProfile
from .models import Student
from .forms import StudentForm


def allowed(request):
    return request.user.role == 'DIRECTOR' or (
        request.user.role == 'TEACHER'
        and hasattr(request.user, 'teacher_profile')
        and request.user.teacher_profile.can_register_students
    )


def random_password():
    return ''.join(
        secrets.choice(string.ascii_letters + string.digits)
        for _ in range(10)
    )


@login_required
def student_list(request):
    q = request.GET.get('q', '')
    students = Student.objects.all().order_by(
        'grade',
        'section',
        'first_name',
        'father_name'
    )

    if q:
        students = students.filter(
            Q(student_id__icontains=q)
            | Q(first_name__icontains=q)
            | Q(father_name__icontains=q)
            | Q(user__email__icontains=q)
        )

    return render(
        request,
        'students/student_list.html',
        {
            'students': students,
            'q': q
        }
    )


@login_required
def register_student(request):
    if not allowed(request):
        messages.error(
            request,
            'You do not have permission to register students.'
        )
        return redirect('student_list')

    form = StudentForm(
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
                role='STUDENT'
            )

            student = form.save(commit=False)
            student.user = user
            student.save()

        messages.success(
            request,
            'Student and User Account created successfully.'
        )

        return redirect(
            'student_detail',
            student.pk
        )

    return render(
        request,
        'students/register_student.html',
        {'form': form}
    )


@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.user.role == 'STUDENT' and student.user_id != request.user.id:
        messages.error(
            request,
            'You can only view your own student profile.'
        )
        return redirect('dashboard')

    if request.user.role not in ['DIRECTOR', 'TEACHER', 'STUDENT']:
        messages.error(
            request,
            'You do not have permission to view student details.'
        )
        return redirect('dashboard')

    return render(
        request,
        'students/student_detail.html',
        {
            'student': student
        }
    )


@login_required
def edit_student(request, pk):
    student = get_object_or_404(
        Student,
        pk=pk
    )

    if not allowed(request):
        messages.error(
            request,
            'You do not have permission to edit students.'
        )
        return redirect(
            'student_detail',
            pk
        )

    form = StudentForm(
        request.POST or None,
        request.FILES or None,
        instance=student
    )

    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data

        with transaction.atomic():
            student = form.save()

            student.user.username = data['username']
            student.user.email = data['email']

            if data.get('password'):
                student.user.set_password(data['password'])

            student.user.save()

        messages.success(
            request,
            'Student updated successfully.'
        )

        return redirect(
            'student_detail',
            pk
        )

    form.fields['username'].initial = student.user.username
    form.fields['email'].initial = student.user.email

    return render(
        request,
        'students/edit_student.html',
        {
            'form': form,
            'student': student
        }
    )


@login_required
def delete_student(request, pk):
    student = get_object_or_404(
        Student,
        pk=pk
    )

    if not allowed(request):
        messages.error(
            request,
            'You do not have permission to delete students.'
        )
        return redirect('student_list')

    if request.method == 'POST':
        student.user.delete()

        messages.success(
            request,
            'Student deleted.'
        )

    return redirect('student_list')

@login_required
def filter_students(request):
    grade = request.GET.get('grade')
    section = request.GET.get('section')
    stream = request.GET.get('stream')

    students = Student.objects.all()

    if grade:
        students = students.filter(grade=grade)

    if section:
        students = students.filter(section=section)

    if grade in ['11', '12']:
        if stream:
            students = students.filter(stream=stream)
        else:
            students = students.none()
    else:
        students = students.filter(stream__isnull=True)

    students = students.order_by(
        'student_id'
    )

    data = []

    for student in students:
        data.append({
            'id': student.id,
            'student_id': student.student_id,
            'name': (
                student.first_name
                + ' '
                + student.father_name
                + ' '
                + student.grandfather_name
            ),
        })

    from django.http import JsonResponse

    return JsonResponse({
        'students': data
    })
