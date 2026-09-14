from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect

from accounts.models import SchoolSettings
from students.models import Student
from academics.views import get_student_final_average

from .models import Promotion


@login_required
def promote_students(request):
    if request.user.role not in ['DIRECTOR', 'TEACHER']:
        messages.error(
            request,
            'You do not have permission to view promotion results.'
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

    year = request.POST.get(
        'academic_year',
        request.GET.get('academic_year', '2026/27')
    )

    settings = SchoolSettings.objects.first()

    if settings is None:
        settings = SchoolSettings.objects.create()

    passing_mark = settings.passing_mark

    students = Student.objects.filter(
        grade=grade,
        section=section
    )

    if grade in [11, 12]:
        if stream:
            students = students.filter(stream=stream)
        else:
            students = Student.objects.none()
    else:
        students = students.filter(stream__isnull=True)

    students = students.order_by('student_id')

    student_results = []

    for student in students:
        average = get_student_final_average(student)

        if average is None:
            status = 'FAIL'
            complete = False
        else:
            status = 'PASS' if average >= passing_mark else 'FAIL'
            complete = True

        student_results.append({
            'student': student,
            'average': average,
            'status': status,
            'complete': complete,
        })

    total_students = len(student_results)

    passed_students = sum(
        1 for item in student_results
        if item['status'] == 'PASS'
    )

    failed_students = sum(
        1 for item in student_results
        if item['status'] == 'FAIL' and item['complete']
    )

    incomplete_students = sum(
        1 for item in student_results
        if not item['complete']
    )

    completed_averages = [
        item['average']
        for item in student_results
        if item['average'] is not None
    ]

    if completed_averages:
        class_average = sum(completed_averages) / len(completed_averages)
        highest_average = max(completed_averages)
        lowest_average = min(completed_averages)
    else:
        class_average = None
        highest_average = None
        lowest_average = None

    if total_students:
        pass_rate = (passed_students / total_students) * 100
    else:
        pass_rate = 0

    promotion_chart = {
        'pass': passed_students,
        'fail': failed_students,
        'incomplete': incomplete_students,
    }

    if request.method == 'POST' and request.user.role == 'DIRECTOR':

        with transaction.atomic():

            for item in student_results:

                student = item['student']
                status = item['status']

                if not item['complete']:
                    continue

                if status == 'PASS':

                    if grade < 12:
                        to_grade = grade + 1
                    else:
                        to_grade = None

                else:
                    to_grade = grade

                Promotion.objects.update_or_create(
                    student=student,
                    from_grade=grade,
                    academic_year=year,
                    defaults={
                        'to_grade': to_grade,
                        'status': status,
                    }
                )

                if status == 'PASS' and to_grade:

                    student.grade = to_grade

                    if to_grade in [9, 10]:
                        student.stream = None

                    student.save(
                        update_fields=[
                            'grade',
                            'stream'
                        ]
                    )

        messages.success(
            request,
            'Automatic PASS/FAIL promotion processing completed.'
        )

        return redirect('promotion_history')

    return render(
        request,
        'promotion/promote_students.html',
        {
            'student_results': student_results,
            'grade': grade,
            'section': section,
            'stream': stream,
            'year': year,
            'passing_mark': passing_mark,
            'total_students': total_students,
            'passed_students': passed_students,
            'failed_students': failed_students,
            'incomplete_students': incomplete_students,
            'pass_rate': pass_rate,
            'class_average': class_average,
            'highest_average': highest_average,
            'lowest_average': lowest_average,
            'promotion_chart': promotion_chart,
        }
    )


@login_required
def promotion_history(request):
    if request.user.role not in ['DIRECTOR', 'TEACHER']:
        messages.error(
            request,
            'You do not have permission to view promotion results.'
        )
        return redirect('dashboard')

    years = list(
        Promotion.objects.values_list(
            'academic_year',
            flat=True
        ).distinct().order_by('-academic_year')
    )

    selected_year = request.GET.get(
        'academic_year',
        years[0] if years else ''
    )

    records = Promotion.objects.select_related(
        'student'
    ).filter(
        academic_year=selected_year
    ).order_by(
        'from_grade',
        'student__first_name',
        'student__father_name',
        'student__grandfather_name'
    )

    records_by_grade = {
        grade: records.filter(from_grade=grade)
        for grade in [9, 10, 11, 12]
    }

    return render(
        request,
        'promotion/promotion_history.html',
        {
            'records': records,
            'records_by_grade': records_by_grade,
            'years': years,
            'selected_year': selected_year,
        }
    )

