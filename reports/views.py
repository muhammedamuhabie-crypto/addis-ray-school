from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render,redirect,get_object_or_404
from students.models import Student
from teachers.models import TeacherProfile
from attendance.models import Attendance
from academics.models import GradeRecord

@login_required
def student_report(request):
    student=getattr(request.user,'student_profile',None)
    if not student:
        messages.error(request,'Student account required.')
        return redirect('dashboard')

    records=GradeRecord.objects.filter(student=student)
    total=sum(float(x.mark) for x in records)
    avg=total/records.count() if records.exists() else 0

    return render(request,'reports/student_report.html',{
        'student':student,
        'records':records,
        'total':total,
        'average':avg,
        'passed':avg>=50
    })


@login_required
def class_report(request):
    if request.user.role not in ['DIRECTOR', 'TEACHER']:
        messages.error(request, 'Permission required.')
        return redirect('dashboard')

    grade = int(request.GET.get('grade', 9))
    section = request.GET.get('section', 'A')
    stream = request.GET.get('stream', '')

    students = Student.objects.filter(grade=grade)

    if section != 'ALL':
        students = students.filter(section=section)

    if grade in [11, 12] and stream:
        students = students.filter(stream=stream)

    students = students.order_by(
        'stream',
        'section',
        'first_name',
        'father_name'
    )

    rows = []

    for s in students:
        records = GradeRecord.objects.filter(student=s)

        if records.exists():
            average = sum(float(x.mark) for x in records) / records.count()
        else:
            average = 0

        rows.append({
            'student': s,
            'average': average,
            'passed': average >= 50
        })

    rows.sort(key=lambda x: x['average'], reverse=True)

    for number, row in enumerate(rows, start=1):
        row['rank'] = number

    total_students = len(rows)
    passed_students = sum(1 for row in rows if row['passed'])
    failed_students = sum(1 for row in rows if not row['passed'])

    if total_students:
        pass_percentage = (passed_students / total_students) * 100
        fail_percentage = (failed_students / total_students) * 100
    else:
        pass_percentage = 0
        fail_percentage = 0

    return render(request, 'reports/class_report.html', {
        'rows': rows,
        'grade': grade,
        'section': section,
        'stream': stream,
        'total_students': total_students,
        'passed_students': passed_students,
        'failed_students': failed_students,
        'pass_percentage': pass_percentage,
        'fail_percentage': fail_percentage
    })

@login_required
@login_required
def school_performance(request):
    if request.user.role != 'DIRECTOR':
        messages.error(request, 'Director permission required.')
        return redirect('dashboard')

    from decimal import Decimal
    from collections import defaultdict

    students = Student.objects.all()
    total_students = students.count()

    yearly_data = defaultdict(lambda: {
        'passed': 0,
        'failed': 0,
        'incomplete': 0,
        'total': 0,
    })

    records = GradeRecord.objects.select_related(
        'student',
        'subject'
    ).order_by(
        'academic_year',
        'student_id',
        'subject_id',
        'semester'
    )

    student_year_subjects = defaultdict(dict)

    for record in records:
        key = (record.academic_year, record.student_id)

        subject_data = student_year_subjects[key].setdefault(
            record.subject_id,
            {
                'semester_1': None,
                'semester_2': None,
            }
        )

        if record.semester == 'SEMESTER_1':
            subject_data['semester_1'] = record.mark
        elif record.semester == 'SEMESTER_2':
            subject_data['semester_2'] = record.mark

    for (academic_year, student_id), subjects in student_year_subjects.items():
        yearly_data[academic_year]['total'] += 1

        final_marks = []
        incomplete = False

        for subject_data in subjects.values():
            semester_1 = subject_data['semester_1']
            semester_2 = subject_data['semester_2']

            if semester_1 is None or semester_2 is None:
                incomplete = True
                continue

            final_mark = (
                Decimal(semester_1) + Decimal(semester_2)
            ) / Decimal('2')

            final_marks.append(final_mark)

        if incomplete or not final_marks:
            status = 'incomplete'
        else:
            average = sum(
                final_marks,
                Decimal('0')
            ) / Decimal(len(final_marks))

            status = 'passed' if average >= Decimal('50') else 'failed'

        yearly_data[academic_year][status] += 1

    current_year = (
        students.values_list(
            'academic_year',
            flat=True
        )
        .distinct()
        .order_by('-academic_year')
        .first()
    )

    current_year_students = yearly_data.get(
        current_year,
        {
            'passed': 0,
            'failed': 0,
            'incomplete': 0,
            'total': 0,
        }
    )

    current_total = current_year_students['total']

    if current_total:
        passed_percent = round(
            current_year_students['passed'] * 100 / current_total,
            1
        )
        failed_percent = round(
            current_year_students['failed'] * 100 / current_total,
            1
        )
        incomplete_percent = round(
            current_year_students['incomplete'] * 100 / current_total,
            1
        )
    else:
        passed_percent = 0
        failed_percent = 0
        incomplete_percent = 0

    yearly_performance = []

    for year in sorted(yearly_data.keys()):
        data = yearly_data[year]
        total = data['total']

        if total:
            yearly_performance.append({
                'year': year,
                'passed': data['passed'],
                'failed': data['failed'],
                'incomplete': data['incomplete'],
                'passed_percent': round(
                    data['passed'] * 100 / total,
                    1
                ),
                'failed_percent': round(
                    data['failed'] * 100 / total,
                    1
                ),
                'incomplete_percent': round(
                    data['incomplete'] * 100 / total,
                    1
                ),
            })

    # Calculate graph coordinates in Python.
    # This keeps the three lines inside the SVG plotting area.
    graph_width = 900
    graph_height = 220
    graph_left = 50
    graph_top = 12

    point_count = len(yearly_performance)

    passed_points = []
    failed_points = []
    incomplete_points = []

    for index, item in enumerate(yearly_performance):

        if point_count == 1:
            x = 500
        else:
            x = graph_left + (
                index * graph_width / (point_count - 1)
            )

        passed_y = graph_top + (
            (100 - item['passed_percent']) * graph_height / 100
        )

        failed_y = graph_top + (
            (100 - item['failed_percent']) * graph_height / 100
        )

        incomplete_y = graph_top + (
            (100 - item['incomplete_percent']) * graph_height / 100
        )

        passed_points.append(
            f'{x:.1f},{passed_y:.1f}'
        )

        failed_points.append(
            f'{x:.1f},{failed_y:.1f}'
        )

        incomplete_points.append(
            f'{x:.1f},{incomplete_y:.1f}'
        )

    return render(
        request,
        'reports/school_performance.html',
        {
            'students': total_students,
            'teachers': TeacherProfile.objects.count(),
            'attendance': Attendance.objects.count(),

            'current_year': current_year,
            'current_total': current_total,

            'passed': current_year_students['passed'],
            'failed': current_year_students['failed'],
            'incomplete': current_year_students['incomplete'],

            'passed_percent': passed_percent,
            'failed_percent': failed_percent,
            'incomplete_percent': incomplete_percent,

            'yearly_performance': yearly_performance,

            'passed_points': ' '.join(passed_points),
            'failed_points': ' '.join(failed_points),
            'incomplete_points': ' '.join(incomplete_points),
        }
    )