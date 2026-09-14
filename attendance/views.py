from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render,redirect
from students.models import Student
from .models import Attendance

def can_attend(u): return u.role=='DIRECTOR' or (u.role=='TEACHER' and hasattr(u,'teacher_profile') and u.teacher_profile.can_take_attendance)
@login_required
def take_attendance(request):
    if not can_attend(request.user):
        messages.error(
            request,
            'You do not have permission to take attendance.'
        )
        return redirect('dashboard')

    grade = int(
        request.POST.get(
            'grade',
            request.GET.get('grade', 9)
        )
    )

    section = request.POST.get(
        'section',
        request.GET.get('section', 'A')
    )

    stream = request.POST.get(
        'stream',
        request.GET.get('stream', '')
    )

    day = request.POST.get(
        'date',
        request.GET.get('date', str(date.today()))
    )

    students = Student.objects.filter(
        grade=grade,
        section=section
    )

    if grade in [11, 12] and stream in ['NATURAL', 'SOCIAL']:
        students = students.filter(stream=stream)

    students = students.order_by(
        'first_name',
        'father_name',
        'grandfather_name'
    )

    if request.method == 'POST':
        with transaction.atomic():
            for s in students:
                status = request.POST.get(
                    f'status_{s.pk}'
                )

                if status in ['P', 'A', 'L']:
                    Attendance.objects.update_or_create(
                        student=s,
                        date=day,
                        defaults={
                            'status': status
                        }
                    )

        messages.success(
            request,
            'Attendance saved.'
        )

        redirect_url = (
            f'/attendance/take/?grade={grade}'
            f'&section={section}'
            f'&date={day}'
        )

        if grade in [11, 12] and stream in ['NATURAL', 'SOCIAL']:
            redirect_url += f'&stream={stream}'

        return redirect(redirect_url)

    existing = {
        a.student_id: a.status
        for a in Attendance.objects.filter(
            student__in=students,
            date=day
        )
    }

    return render(
        request,
        'attendance/take_attendance.html',
        {
            'students': students,
            'existing': existing,
            'grade': grade,
            'section': section,
            'stream': stream,
            'day': day,
        }
    )


@login_required
def attendance_records(request):
    if request.user.role not in ['DIRECTOR', 'TEACHER']:
        messages.error(
            request,
            'You do not have permission to view attendance records.'
        )
        return redirect('dashboard')

    records = Attendance.objects.select_related('student').all().order_by(
        'student__grade',
        'student__stream',
        'student__section',
        '-date',
        'student__first_name'
    )

    selected_date = request.GET.get('date', '')
    selected_grade = request.GET.get('grade', '')
    selected_section = request.GET.get('section', '')
    selected_status = request.GET.get('status', '')

    if selected_date:
        records = records.filter(date=selected_date)

    if selected_grade:
        records = records.filter(student__grade=selected_grade)

    if selected_section:
        records = records.filter(student__section=selected_section)

    if selected_status in ['P', 'A', 'L']:
        records = records.filter(status=selected_status)

    total = records.count()
    present = records.filter(status='P').count()
    late = records.filter(status='L').count()
    absent = records.filter(status='A').count()

    attendance_percentage = (
        ((present + late) / total * 100)
        if total else 0
    )

    grouped_records = []

    current_grade = None
    current_stream = None
    current_section = None
    current_group = None

    for record in records:
        grade = record.student.grade
        stream = getattr(record.student, 'stream', None)
        section = record.student.section

        if (
            grade != current_grade
            or stream != current_stream
            or section != current_section
        ):
            current_grade = grade
            current_stream = stream
            current_section = section

            current_group = {
                'grade': grade,
                'stream': stream,
                'section': section,
                'records': [],
            }

            grouped_records.append(current_group)

        current_group['records'].append(record)

    return render(request, 'attendance/attendance_records.html', {
        'records': records,
        'grouped_records': grouped_records,
        'total': total,
        'present': present,
        'late': late,
        'absent': absent,
        'attendance_percentage': attendance_percentage,
        'selected_date': selected_date,
        'selected_grade': selected_grade,
        'selected_section': selected_section,
        'selected_status': selected_status,
    })

@login_required
def student_attendance(request,pk=None):
    if request.user.role == 'STUDENT':
        student = getattr(request.user, 'student_profile', None)

        if student is None:
            messages.error(
                request,
                'Student profile not found.'
            )
            return redirect('dashboard')

        if pk is not None and int(pk) != student.pk:
            messages.error(
                request,
                'You can only view your own attendance.'
            )
            return redirect('dashboard')

    elif request.user.role in ['DIRECTOR', 'TEACHER']:
        if pk is None:
            student = getattr(request.user, 'student_profile', None)
        else:
            student = get_object_or_404(Student, pk=pk)
    else:
        messages.error(
            request,
            'You do not have permission to view attendance.'
        )
        return redirect('dashboard')

    if student is None:
        messages.error(
            request,
            'Student profile not found.'
        )
        return redirect('dashboard')

    records=Attendance.objects.filter(student=student).order_by('-date')

    total=records.count()
    present=records.filter(status='P').count()
    late=records.filter(status='L').count()
    absent=records.filter(status='A').count()

    percentage=((present+late)/total*100) if total else 0

    return render(request,'attendance/student_attendance.html',{
        'student':student,
        'records':records,
        'total':total,
        'present':present,
        'late':late,
        'absent':absent,
        'percentage':percentage
    })

@login_required
def attendance_report(request):
    if request.user.role not in ['DIRECTOR', 'TEACHER']:
        messages.error(
            request,
            'You do not have permission to view the attendance report.'
        )
        return redirect('dashboard')

    records = Attendance.objects.select_related('student').all()

    selected_date = request.GET.get('date', '')
    selected_grade = request.GET.get('grade', '')
    selected_section = request.GET.get('section', '')

    if selected_date:
        records = records.filter(date=selected_date)

    if selected_grade:
        records = records.filter(student__grade=selected_grade)

    if selected_section:
        records = records.filter(student__section=selected_section)

    total = records.count()
    present = records.filter(status='P').count()
    late = records.filter(status='L').count()
    absent = records.filter(status='A').count()

    attendance_percentage = (
        ((present + late) / total * 100)
        if total else 0
    )

    student_stats = []

    students = Student.objects.all().order_by(
        'grade',
        'stream',
        'section',
        'first_name',
        'father_name'
    )

    if selected_grade:
        students = students.filter(grade=selected_grade)

    if selected_section:
        students = students.filter(section=selected_section)

    for student in students:
        student_records = records.filter(student=student)

        student_total = student_records.count()
        student_present = student_records.filter(status='P').count()
        student_late = student_records.filter(status='L').count()
        student_absent = student_records.filter(status='A').count()

        student_percentage = (
            ((student_present + student_late) / student_total * 100)
            if student_total else 0
        )

        if student_total:
            student_stats.append({
                'student': student,
                'total': student_total,
                'present': student_present,
                'late': student_late,
                'absent': student_absent,
                'percentage': student_percentage,
            })

    grouped_stats = []

    current_grade = None
    current_stream = None
    current_section = None
    current_group = None

    for item in student_stats:

        grade = item['student'].grade
        stream = getattr(item['student'], 'stream', None)
        section = item['student'].section

        if (
            grade != current_grade
            or stream != current_stream
            or section != current_section
        ):
            current_grade = grade
            current_stream = stream
            current_section = section

            current_group = {
                'grade': grade,
                'stream': stream,
                'section': section,
                'students': [],
            }

            grouped_stats.append(current_group)

        current_group['students'].append(item)

    return render(request, 'attendance/attendance_report.html', {
        'total': total,
        'present': present,
        'late': late,
        'absent': absent,
        'attendance_percentage': attendance_percentage,
        'student_stats': student_stats,
        'grouped_stats': grouped_stats,
        'selected_date': selected_date,
        'selected_grade': selected_grade,
        'selected_section': selected_section,
    })


