from decimal import Decimal

from django.db import transaction
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema, OpenApiResponse

from api.serializers import (
    PromotionListSerializer,
    PromotionCreateSerializer,
    StudentReportSerializer,
    ClassReportSerializer,
    SchoolPerformanceSerializer,
    AttendanceReportSerializer,
)

from students.models import Student
from teachers.models import TeacherProfile
from academics.models import GradeRecord
from attendance.models import Attendance
from promotion.models import Promotion


class PromotionAPIView(APIView):


    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses=PromotionListSerializer
    )
    def get(self, request):
        if request.user.role != 'DIRECTOR':
            raise PermissionDenied(
                'Director access required.'
            )

        records = Promotion.objects.select_related(
            'student'
        ).order_by('-created_at')

        data = []

        for record in records:
            data.append({
                'id': record.id,
                'student_id': record.student.id,
                'student_number': record.student.student_id,
                'student_name': (
                    f'{record.student.first_name} '
                    f'{record.student.father_name}'
                ),
                'from_grade': record.from_grade,
                'to_grade': record.to_grade,
                'academic_year': record.academic_year,
                'status': record.status,
                'created_at': record.created_at,
            })

        return Response({
            'count': len(data),
            'promotions': data,
        })

    @extend_schema(
        request=None,
        responses=PromotionCreateSerializer
    )
    def post(self, request):

        if request.user.role != 'DIRECTOR':
            raise PermissionDenied(
                'Director access required.'
            )

        student_id = request.data.get('student_id')
        action = request.data.get('action')
        academic_year = request.data.get(
            'academic_year',
            '2026/27'
        )

        if not student_id:
            return Response(
                {'detail': 'student_id is required.'},
                status=400
            )

        if action not in [
            'PROMOTED',
            'REPEAT',
            'COMPLETED'
        ]:
            return Response(
                {
                    'detail': (
                        'action must be PROMOTED, '
                        'REPEAT, or COMPLETED.'
                    )
                },
                status=400
            )

        student = Student.objects.filter(
            pk=student_id
        ).first()

        if not student:
            return Response(
                {'detail': 'Student not found.'},
                status=404
            )

        from_grade = student.grade

        if from_grade == 12:

            if action in [
                'PROMOTED',
                'COMPLETED'
            ]:
                to_grade = None
                status = 'COMPLETED'
            else:
                to_grade = 12
                status = 'REPEAT'

        else:

            if action == 'PROMOTED':
                to_grade = from_grade + 1
                status = 'PROMOTED'
            else:
                to_grade = from_grade
                status = 'REPEAT'

        with transaction.atomic():

            promotion = Promotion.objects.create(
                student=student,
                from_grade=from_grade,
                to_grade=to_grade,
                academic_year=academic_year,
                status=status
            )

            if status == 'PROMOTED' and to_grade:

                student.grade = to_grade

                if to_grade in [9, 10]:
                    student.stream = None

                student.save(
                    update_fields=[
                        'grade',
                        'stream'
                    ]
                )

        return Response({
            'id': promotion.id,
            'student_id': student.id,
            'student_number': student.student_id,
            'student_name': (
                f'{student.first_name} '
                f'{student.father_name}'
            ),
            'from_grade': from_grade,
            'to_grade': to_grade,
            'academic_year': academic_year,
            'status': status,
        }, status=201)


class StudentReportAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses=StudentReportSerializer
    )
    def get(self, request):

        if request.user.role != 'STUDENT':
            raise PermissionDenied(
                'Student access required.'
            )

        student = getattr(
            request.user,
            'student_profile',
            None
        )

        if not student:
            raise PermissionDenied(
                'Student profile not found.'
            )

        records = GradeRecord.objects.filter(
            student=student
        ).select_related('subject')

        total = sum(
            (Decimal(record.mark) for record in records),
            Decimal('0')
        )

        count = records.count()

        average = (
            total / Decimal(count)
            if count
            else Decimal('0')
        )

        return Response({
            'student_id': student.id,
            'student_number': student.student_id,
            'student_name': (
                f'{student.first_name} '
                f'{student.father_name}'
            ),
            'grade': student.grade,
            'section': student.section,
            'stream': student.stream,
            'academic_year': student.academic_year,
            'total': total,
            'average': average,
            'passed': average >= Decimal('50'),
            'records': [
                {
                    'id': record.id,
                    'subject_id': record.subject_id,
                    'subject': record.subject.name,
                    'semester': record.semester,
                    'mark': record.mark,
                    'academic_year': record.academic_year,
                }
                for record in records
            ],
        })


class ClassReportAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses=ClassReportSerializer
    )
    def get(self, request):

        if request.user.role not in [
            'DIRECTOR',
            'TEACHER'
        ]:
            raise PermissionDenied(
                'Director or Teacher access required.'
            )

        grade = request.query_params.get(
            'grade'
        )

        section = request.query_params.get(
            'section',
            'ALL'
        )

        if not grade:
            return Response(
                {'detail': 'grade is required.'},
                status=400
            )

        try:
            grade = int(grade)
        except ValueError:
            return Response(
                {'detail': 'grade must be a number.'},
                status=400
            )

        if request.user.role == 'TEACHER':

            teacher = getattr(
                request.user,
                'teacher_profile',
                None
            )

            if not teacher:
                raise PermissionDenied(
                    'Teacher profile not found.'
                )

            if int(teacher.grade) != grade:
                raise PermissionDenied(
                    f'You are assigned to Grade '
                    f'{teacher.grade}.'
                )

            if section != 'ALL':
                if str(teacher.section).strip() != str(
                    section
                ).strip():
                    raise PermissionDenied(
                        f'You are not assigned to '
                        f'Grade {grade} Section {section}.'
                    )

        students = Student.objects.filter(
            grade=grade
        )

        if section != 'ALL':
            students = students.filter(
                section=section
            )

        rows = []

        for student in students:

            records = GradeRecord.objects.filter(
                student=student
            )

            if records.exists():

                total = sum(
                    (
                        Decimal(record.mark)
                        for record in records
                    ),
                    Decimal('0')
                )

                average = (
                    total /
                    Decimal(records.count())
                )

            else:
                average = Decimal('0')

            rows.append({
                'student_id': student.id,
                'student_number': student.student_id,
                'student_name': (
                    f'{student.first_name} '
                    f'{student.father_name}'
                ),
                'grade': student.grade,
                'section': student.section,
                'stream': student.stream,
                'average': average,
                'passed': average >= Decimal('50'),
            })

        rows.sort(
            key=lambda item: item['average'],
            reverse=True
        )

        for position, row in enumerate(
            rows,
            start=1
        ):
            row['rank'] = position

        total_students = len(rows)

        passed_students = sum(
            1 for row in rows
            if row['passed']
        )

        failed_students = (
            total_students - passed_students
        )

        pass_percentage = (
            (passed_students / total_students) * 100
            if total_students
            else 0
        )

        fail_percentage = (
            (failed_students / total_students) * 100
            if total_students
            else 0
        )

        return Response({
            'grade': grade,
            'section': section,
            'total_students': total_students,
            'passed_students': passed_students,
            'failed_students': failed_students,
            'pass_percentage': pass_percentage,
            'fail_percentage': fail_percentage,
            'students': rows,
        })


class SchoolPerformanceAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses=SchoolPerformanceSerializer
    )
    def get(self, request):

        if request.user.role != 'DIRECTOR':
            raise PermissionDenied(
                'Director access required.'
            )

        students = Student.objects.all()

        passed = 0
        failed = 0

        for student in students:

            records = GradeRecord.objects.filter(
                student=student
            )

            if not records.exists():
                continue

            total = sum(
                (
                    Decimal(record.mark)
                    for record in records
                ),
                Decimal('0')
            )

            average = (
                total /
                Decimal(records.count())
            )

            if average >= Decimal('50'):
                passed += 1
            else:
                failed += 1

        return Response({
            'students': students.count(),
            'teachers': TeacherProfile.objects.count(),
            'passed': passed,
            'failed': failed,
            'attendance_records': Attendance.objects.count(),
        })


class AttendanceReportAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses=AttendanceReportSerializer
    )
    def get(self, request):

        if request.user.role not in [
            'DIRECTOR',
            'TEACHER'
        ]:
            raise PermissionDenied(
                'Director or Teacher access required.'
            )

        records = Attendance.objects.select_related(
            'student'
        ).all()

        if request.user.role == 'TEACHER':

            teacher = getattr(
                request.user,
                'teacher_profile',
                None
            )

            if not teacher:
                raise PermissionDenied(
                    'Teacher profile not found.'
                )

            records = records.filter(
                student__grade=teacher.grade
            )

            if getattr(teacher, 'section', None):
                records = records.filter(
                    student__section=teacher.section
                )

        total = records.count()

        present = records.filter(
            status='PRESENT'
        ).count()

        absent = records.filter(
            status='ABSENT'
        ).count()

        late = records.filter(
            status='LATE'
        ).count()

        percentage = (
            (present / total) * 100
            if total
            else 0
        )

        return Response({
            'total_records': total,
            'present': present,
            'absent': absent,
            'late': late,
            'attendance_percentage': percentage,
        })
