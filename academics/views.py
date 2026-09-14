from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect

from students.models import Student
from .models import GradeRecord, Subject, ClassRoom
from .forms import GradeRecordForm, SubjectForm, ClassRoomForm


def can_grade(u):
    return (
        u.role == 'TEACHER'
        and hasattr(u, 'teacher_profile')
        and u.teacher_profile.can_enter_grades
    )


def can_view_student(u, s):
    return u.role in ['DIRECTOR', 'TEACHER'] or (
        u.role == 'STUDENT' and s.user_id == u.id
    )


def get_final_results(student):
    records = GradeRecord.objects.filter(
        student=student,
        academic_year=student.academic_year
    ).select_related('subject').order_by(
        'subject__name',
        'semester'
    )

    subjects = {}

    for record in records:
        subject_id = record.subject_id

        if subject_id not in subjects:
            subjects[subject_id] = {
                'subject': record.subject,
                'semester_1': None,
                'semester_2': None,
            }

        if record.semester == 'SEMESTER_1':
            subjects[subject_id]['semester_1'] = record.mark

        elif record.semester == 'SEMESTER_2':
            subjects[subject_id]['semester_2'] = record.mark

    results = []

    for item in subjects.values():

        semester_1 = item['semester_1']
        semester_2 = item['semester_2']

        final_mark = None

        if semester_1 is not None and semester_2 is not None:
            final_mark = (
                Decimal(semester_1) + Decimal(semester_2)
            ) / Decimal('2')

        results.append({
            'subject': item['subject'],
            'semester_1': semester_1,
            'semester_2': semester_2,
            'final_mark': final_mark,
        })

    return results


def get_student_final_average(student):
    results = get_final_results(student)

    completed = [
        r for r in results
        if r['final_mark'] is not None
    ]

    if not completed:
        return None

    if len(completed) != len(results):
        return None

    total = sum(
        (r['final_mark'] for r in completed),
        Decimal('0')
    )

    return total / Decimal(len(completed))


@login_required
def load_students(request):
    if request.user.role not in ['DIRECTOR', 'TEACHER']:
        return JsonResponse(
            {'students': []},
            status=403
        )

    grade = request.GET.get('grade')
    section = request.GET.get('section')
    stream = request.GET.get('stream')

    students = Student.objects.none()

    if grade and section:

        students = Student.objects.filter(
            grade=grade,
            section=section
        )

        if grade in ['11', '12']:

            if stream:
                students = students.filter(
                    stream=stream
                )

            else:
                students = Student.objects.none()

    students = students.order_by(
        'student_id'
    )

    data = []

    for student in students:
        data.append({
            'id': student.id,
            'student_id': student.student_id,
            'name': f'{student.first_name} {student.father_name}'
        })

    return JsonResponse({
        'students': data
    })


@login_required
def classes(request):
    if request.user.role not in ['DIRECTOR', 'TEACHER']:
        return redirect('dashboard')

    form = ClassRoomForm(request.POST or None)

    if (
        request.method == 'POST'
        and request.user.role == 'DIRECTOR'
        and form.is_valid()
    ):
        form.save()
        messages.success(
            request,
            'Class created.'
        )
        return redirect('classes')

    return render(
        request,
        'academics/classes.html',
        {
            'classes': ClassRoom.objects.all(),
            'form': form
        }
    )



@login_required
def edit_subject(request, pk):
    if request.user.role != 'DIRECTOR':
        messages.error(
            request,
            'Director permission required.'
        )
        return redirect('subjects')

    subject = get_object_or_404(
        Subject,
        pk=pk
    )

    form = SubjectForm(
        request.POST or None,
        instance=subject
    )

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(
            request,
            'Subject updated.'
        )
        return redirect('subjects')

    return render(
        request,
        'academics/edit_subject.html',
        {
            'form': form,
            'subject': subject
        }
    )


@login_required
def delete_subject(request, pk):
    if request.user.role != 'DIRECTOR':
        messages.error(
            request,
            'Director permission required.'
        )
        return redirect('subjects')

    subject = get_object_or_404(
        Subject,
        pk=pk
    )

    if request.method == 'POST':
        try:
            subject.delete()
            messages.success(
                request,
                'Subject deleted.'
            )
        except Exception:
            messages.error(
                request,
                'This subject cannot be deleted because it is already being used.'
            )

        return redirect('subjects')

    return render(
        request,
        'academics/delete_subject.html',
        {
            'subject': subject
        }
    )


@login_required
def edit_class(request, pk):
    if request.user.role != 'DIRECTOR':
        messages.error(
            request,
            'Director permission required.'
        )
        return redirect('classes')

    classroom = get_object_or_404(
        ClassRoom,
        pk=pk
    )

    form = ClassRoomForm(
        request.POST or None,
        instance=classroom
    )

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(
            request,
            'Class updated.'
        )
        return redirect('classes')

    return render(
        request,
        'academics/edit_class.html',
        {
            'form': form,
            'classroom': classroom
        }
    )


@login_required
def delete_class(request, pk):
    if request.user.role != 'DIRECTOR':
        messages.error(
            request,
            'Director permission required.'
        )
        return redirect('classes')

    classroom = get_object_or_404(
        ClassRoom,
        pk=pk
    )

    if request.method == 'POST':
        classroom.delete()
        messages.success(
            request,
            'Class deleted.'
        )
        return redirect('classes')

    return render(
        request,
        'academics/delete_class.html',
        {
            'classroom': classroom
        }
    )

@login_required
def subjects(request):
    if request.user.role != 'DIRECTOR':
        messages.error(
            request,
            'Director permission required.'
        )
        return redirect('dashboard')

    form = SubjectForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(
            request,
            'Subject added.'
        )
        return redirect('subjects')

    return render(
        request,
        'academics/subjects.html',
        {
            'subjects': Subject.objects.all(),
            'form': form
        }
    )


@login_required
def enter_grade(request):
    if not can_grade(request.user):
        messages.error(
            request,
            'You do not have permission to enter grades.'
        )
        return redirect('dashboard')

    form = GradeRecordForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():

        student = form.cleaned_data['student']

        if student.grade != int(form.cleaned_data['grade']):
            form.add_error(
                'student',
                'Student grade does not match the selected grade.'
            )

        elif student.section != form.cleaned_data['section']:
            form.add_error(
                'student',
                'Student section does not match the selected section.'
            )

        else:

            subject = form.cleaned_data['subject']

            if request.user.role == 'TEACHER':

                teacher_subject = request.user.teacher_profile.subject
                selected_subject = subject

                if teacher_subject != selected_subject:

                    form.add_error(
                        'subject',
                        f'You are a {request.user.teacher_profile.subject.name} teacher. '
                        f'You cannot enter {subject.name} marks.'
                    )

                else:

                    form.save()

                    messages.success(
                        request,
                        'Grade saved successfully.'
                    )

                    return redirect('grade_records')

            else:

                form.save()

                messages.success(
                    request,
                    'Grade saved successfully.'
                )

                return redirect('grade_records')

    return render(
        request,
        'academics/enter_grade.html',
        {
            'form': form
        }
    )


@login_required
def grade_records(request):
    if request.user.role not in ['DIRECTOR', 'TEACHER']:
        return redirect('dashboard')

    records = GradeRecord.objects.select_related(
        'student',
        'subject'
    ).order_by(
        '-academic_year',
        'student__grade',
        'student__section',
        'student__student_id',
        'semester'
    )

    return render(
        request,
        'academics/grade_records.html',
        {
            'records': records
        }
    )


@login_required
def student_results(request, pk=None):

    if pk is None and request.user.role in ['DIRECTOR', 'TEACHER']:
        students = list(
            Student.objects.all().order_by(
                'grade',
                'section',
                'first_name',
                'father_name'
            )
        )

        # Calculate the same class rank used on the
        # individual Academic Results page.
        ranking_groups = {}

        for student in students:
            average = get_student_final_average(student)

            if average is None:
                continue

            if student.grade in [11, 12]:
                group_key = (
                    student.grade,
                    student.section,
                    student.stream
                )
            else:
                group_key = (
                    student.grade,
                    student.section
                )

            ranking_groups.setdefault(
                group_key,
                []
            ).append(
                (student.pk, average)
            )

        # Calculate rank within each Grade/Section,
        # and for Grades 11/12 within Grade/Stream/Section.
        student_ranks = {}

        for group_items in ranking_groups.values():
            group_items.sort(
                key=lambda x: x[1],
                reverse=True
            )

            for position, (student_id, average) in enumerate(
                group_items,
                start=1
            ):
                student_ranks[student_id] = position

        # Attach the calculated rank to each student.
        for student in students:
            student.result_rank = student_ranks.get(
                student.pk
            )

        return render(
            request,
            'academics/student_results_select.html',
            {
                'students': students,
            }
        )

    student = (
        get_object_or_404(
            Student,
            pk=pk
        )
        if pk
        else getattr(
            request.user,
            'student_profile',
            None
        )
    )

    if not student or not can_view_student(
        request.user,
        student
    ):
        messages.error(
            request,
            'You cannot view this result.'
        )
        return redirect('dashboard')

    final_results = get_final_results(student)

    completed_results = [
        r for r in final_results
        if r['final_mark'] is not None
    ]

    average = get_student_final_average(student)

    total = None

    if average is not None:
        total = sum(
            r['final_mark']
            for r in completed_results
        )

    passed = (
        average is not None
        and average >= Decimal('50')
    )

    rank = None

    if average is not None:

        classmates = Student.objects.filter(
            grade=student.grade,
            section=student.section
        )

        if student.grade in [11, 12]:
            classmates = classmates.filter(
                stream=student.stream
            )

        class_results = []

        for classmate in classmates:

            class_average = get_student_final_average(
                classmate
            )

            if class_average is not None:
                class_results.append(
                    (
                        classmate.pk,
                        class_average
                    )
                )

        class_results.sort(
            key=lambda x: x[1],
            reverse=True
        )

        rank = next(
            (
                index + 1
                for index, item in enumerate(class_results)
                if item[0] == student.pk
            ),
            None
        )

    return render(
        request,
        'academics/student_results.html',
        {
            'student': student,
            'final_results': final_results,
            'total': total,
            'average': average,
            'passed': passed,
            'rank': rank,
        }
    )


@login_required
def ranking(request):

    if request.user.role not in [
        'DIRECTOR',
        'TEACHER',
        'STUDENT'
    ]:
        return redirect('dashboard')

    students = Student.objects.all()

    # ---------------------------------
    # 1. SECTION-BASED RANKING
    # ---------------------------------

    section_groups = {}

    for student in students:

        average = get_student_final_average(student)

        if average is None:
            continue

        if student.grade in [11, 12]:
            group = (
                student.grade,
                student.section,
                student.stream
            )
        else:
            group = (
                student.grade,
                student.section,
                None
            )

        section_groups.setdefault(
            group,
            []
        ).append(
            (
                student,
                average
            )
        )

    section_rankings = []

    for group, items in section_groups.items():

        items.sort(
            key=lambda x: x[1],
            reverse=True
        )

        ranking_items = []

        for position, (student, average) in enumerate(
            items,
            1
        ):
            ranking_items.append({
                'student': student,
                'average': average,
                'rank': position
            })

        section_rankings.append({
            'grade': group[0],
            'section': group[1],
            'stream': group[2],
            'students': ranking_items
        })

    section_rankings.sort(
        key=lambda x: (
            x['grade'],
            x['section'],
            x['stream'] or ''
        )
    )

    # ---------------------------------
    # 2. GRADE-BASED TOP 3
    # ---------------------------------

    grade_rankings = []

    for grade in [9, 10, 11, 12]:

        grade_students = []

        for student in students:

            if student.grade != grade:
                continue

            average = get_student_final_average(student)

            if average is None:
                continue

            grade_students.append(
                (
                    student,
                    average
                )
            )

        grade_students.sort(
            key=lambda x: x[1],
            reverse=True
        )

        top_three = []

        for position, (student, average) in enumerate(
            grade_students[:3],
            1
        ):
            top_three.append({
                'student': student,
                'average': average,
                'rank': position
            })

        grade_rankings.append({
            'grade': grade,
            'students': top_three
        })

    # ---------------------------------
    # 3. COMPOUND TOP 3
    # ---------------------------------

    compound_students = []

    for student in students:

        if student.grade not in [9, 10, 11, 12]:
            continue

        average = get_student_final_average(student)

        if average is None:
            continue

        compound_students.append(
            (
                student,
                average
            )
        )

    compound_students.sort(
        key=lambda x: x[1],
        reverse=True
    )

    compound_ranking = []

    for position, (student, average) in enumerate(
        compound_students[:3],
        1
    ):
        compound_ranking.append({
            'student': student,
            'average': average,
            'rank': position
        })

    return render(
        request,
        'academics/ranking.html',
        {
            'section_rankings': section_rankings,
            'grade_rankings': grade_rankings,
            'compound_ranking': compound_ranking
        }
    )

