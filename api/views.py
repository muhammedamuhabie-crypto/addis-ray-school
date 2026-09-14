from decimal import Decimal

from rest_framework import permissions, viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from students.models import Student
from academics.models import Subject, ClassRoom, GradeRecord
from teachers.models import TeacherProfile, TeacherAssignment

from .serializers import (
    StudentSerializer,
    CurrentUserSerializer,
    AuthorizationResponseSerializer,
    ServiceAuthorizationSerializer,
    SubjectSerializer,
    ClassRoomSerializer,
    GradeRecordSerializer,
    TeacherSerializer,
    TeacherCreateSerializer,
    AttendanceSerializer,
    StudentResultsSerializer,
    StudentAverageSerializer,
    RankingSerializer,
)

from .permissions import (
    IsDirector,
    IsTeacher,
    IsStudent,
    IsDirectorOrTeacher,
)


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsDirectorOrTeacher]

    def _teacher_profile(self):
        if self.request.user.role == 'TEACHER':
            return TeacherProfile.objects.get(user=self.request.user)
        return None

    def get_queryset(self):
        qs = Student.objects.all()

        if self.request.user.role == 'TEACHER':
            teacher = self._teacher_profile()
            return qs.filter(
                grade=teacher.grade,
                section=teacher.section
            )

        return qs

    def perform_create(self, serializer):
        if self.request.user.role == 'TEACHER':
            teacher = self._teacher_profile()

            if not teacher.can_register_students:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(
                    'You are not authorized to register students.'
                )

            student_grade = serializer.validated_data.get('grade')
            student_section = serializer.validated_data.get('section')

            if student_grade != teacher.grade:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(
                    f'You are assigned to Grade {teacher.grade}. '
                    f'You cannot register students for Grade {student_grade}.'
                )

            if student_section != teacher.section:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(
                    f'You are assigned to Section {teacher.section}. '
                    f'You cannot register students for Section {student_section}.'
                )

        serializer.save()

    def perform_update(self, serializer):
        if self.request.user.role == 'TEACHER':
            teacher = self._teacher_profile()

            if not teacher.can_register_students:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(
                    'You are not authorized to edit students.'
                )

            student = self.get_object()

            if student.grade != teacher.grade:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(
                    f'You are assigned to Grade {teacher.grade}. '
                    f'You cannot edit a student from Grade {student.grade}.'
                )

            if student.section != teacher.section:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(
                    f'You are assigned to Section {teacher.section}. '
                    f'You cannot edit a student from Section {student.section}.'
                )

            new_grade = serializer.validated_data.get('grade', student.grade)
            new_section = serializer.validated_data.get('section', student.section)

            if new_grade != teacher.grade:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(
                    f'You are assigned to Grade {teacher.grade}. '
                    f'You cannot move a student to Grade {new_grade}.'
                )

        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.role == 'TEACHER':
            teacher = self._teacher_profile()

            if not teacher.can_register_students:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(
                    'You are not authorized to delete students.'
                )

            if instance.grade != teacher.grade:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(
                    f'You are assigned to Grade {teacher.grade}. '
                    f'You cannot delete a student from Grade {instance.grade}.'
                )

            if instance.section != teacher.section:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(
                    f'You are assigned to Section {teacher.section}. '
                    f'You cannot delete a student from Section {instance.section}.'
                )

        instance.delete()


class CurrentUserView(GenericAPIView):
    serializer_class = CurrentUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
        })


class DirectorAuthorizationView(GenericAPIView):
    serializer_class = AuthorizationResponseSerializer
    permission_classes = [IsDirector]

    def get(self, request):
        return Response({
            'authorized': True,
            'role': request.user.role,
            'message': 'Director authorization successful.'
        })


class TeacherAuthorizationView(GenericAPIView):
    serializer_class = AuthorizationResponseSerializer
    permission_classes = [IsTeacher]

    def get(self, request):
        return Response({
            'authorized': True,
            'role': request.user.role,
            'message': 'Teacher authorization successful.'
        })


class StudentAuthorizationView(GenericAPIView):
    serializer_class = AuthorizationResponseSerializer
    permission_classes = [IsStudent]

    def get(self, request):
        return Response({
            'authorized': True,
            'role': request.user.role,
            'message': 'Student authorization successful.'
        })


class StudentsServiceAuthorizationView(GenericAPIView):
    serializer_class = ServiceAuthorizationSerializer
    permission_classes = [IsDirectorOrTeacher]

    def get(self, request):
        return Response({
            'authorized': True,
            'role': request.user.role,
            'service': 'Students',
            'message': 'Students service authorization successful.'
        })


class TeachersServiceAuthorizationView(GenericAPIView):
    serializer_class = ServiceAuthorizationSerializer
    permission_classes = [IsDirector]

    def get(self, request):
        return Response({
            'authorized': True,
            'role': request.user.role,
            'service': 'Teachers',
            'message': 'Teachers service authorization successful.'
        })


class AcademicsServiceAuthorizationView(GenericAPIView):
    serializer_class = ServiceAuthorizationSerializer
    permission_classes = [IsDirectorOrTeacher]

    def get(self, request):
        return Response({
            'authorized': True,
            'role': request.user.role,
            'service': 'Academics',
            'message': 'Academics service authorization successful.'
        })


class AttendanceServiceAuthorizationView(GenericAPIView):
    serializer_class = ServiceAuthorizationSerializer
    permission_classes = [IsDirectorOrTeacher]

    def get(self, request):
        return Response({
            'authorized': True,
            'role': request.user.role,
            'service': 'Attendance',
            'message': 'Attendance service authorization successful.'
        })


class PromotionServiceAuthorizationView(GenericAPIView):
    serializer_class = ServiceAuthorizationSerializer
    permission_classes = [IsDirector]

    def get(self, request):
        return Response({
            'authorized': True,
            'role': request.user.role,
            'service': 'Promotion',
            'message': 'Promotion service authorization successful.'
        })


class ReportsServiceAuthorizationView(GenericAPIView):
    serializer_class = ServiceAuthorizationSerializer
    permission_classes = [IsDirectorOrTeacher]

    def get(self, request):
        return Response({
            'authorized': True,
            'role': request.user.role,
            'service': 'Reports',
            'message': 'Reports service authorization successful.'
        })


class SettingsServiceAuthorizationView(GenericAPIView):
    serializer_class = ServiceAuthorizationSerializer
    permission_classes = [IsDirector]

    def get(self, request):
        return Response({
            'authorized': True,
            'role': request.user.role,
            'service': 'Settings',
            'message': 'Settings service authorization successful.'
        })


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all().order_by('name')
    serializer_class = SubjectSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsDirectorOrTeacher]
        else:
            permission_classes = [IsDirector]

        return [permission() for permission in permission_classes]


class ClassRoomViewSet(viewsets.ModelViewSet):
    queryset = ClassRoom.objects.all().order_by(
        'grade',
        'section',
        'academic_year'
    )
    serializer_class = ClassRoomSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsDirectorOrTeacher]
        else:
            permission_classes = [IsDirector]

        return [permission() for permission in permission_classes]


class GradeRecordViewSet(viewsets.ModelViewSet):
    queryset = GradeRecord.objects.select_related(
        'student',
        'subject'
    ).all().order_by(
        '-academic_year',
        'student__student_id',
        'subject__name',
        'semester'
    )

    serializer_class = GradeRecordSerializer
    permission_classes = [IsDirectorOrTeacher]

    def get_queryset(self):
        user = self.request.user

        queryset = GradeRecord.objects.select_related(
            'student',
            'subject'
        ).all().order_by(
            '-academic_year',
            'student__student_id',
            'subject__name',
            'semester'
        )

        if user.role == 'TEACHER':
            if not hasattr(user, 'teacher_profile'):
                return queryset.none()

            teacher = user.teacher_profile

            if not teacher.can_enter_grades:
                return queryset.none()

            teacher_subject = teacher.subject

            assignments = TeacherAssignment.objects.filter(
                teacher=teacher,
                academic_year__in=queryset.values_list('academic_year', flat=True)
            ).values_list('grade', 'section', 'academic_year')

            from django.db.models import Q

            assignment_filter = Q()

            for grade, section, academic_year in assignments:
                assignment_filter |= Q(
                    student__grade=grade,
                    student__section=section,
                    academic_year=academic_year
                )

            queryset = queryset.filter(
                subject=teacher_subject
            ).filter(assignment_filter)

        return queryset

    def perform_create(self, serializer):

        user = self.request.user

        if user.role == 'TEACHER':

            if not hasattr(user, 'teacher_profile'):
                raise PermissionDenied(
                    'Teacher profile not found.'
                )

            if not user.teacher_profile.can_enter_grades:
                raise PermissionDenied(
                    'You do not have permission to enter grades.'
                )

            teacher_subject = user.teacher_profile.subject

            selected_subject = serializer.validated_data['subject']

            if teacher_subject != selected_subject:
                raise PermissionDenied(
                    f'You are a {teacher_subject.name} teacher. '
                    f'You cannot enter {selected_subject.name} marks.'
                )

            student = serializer.validated_data['student']

            assignment_exists = TeacherAssignment.objects.filter(
                teacher=user.teacher_profile,
                grade=student.grade,
                section=student.section,
                academic_year=student.academic_year
            ).exists()

            if not assignment_exists:
                raise PermissionDenied(
                    f'You are not assigned to Grade {student.grade} '
                    f'Section {student.section} for {student.academic_year}.'
                )

        serializer.save()

    def perform_update(self, serializer):

        user = self.request.user

        if user.role == 'TEACHER':

            if not hasattr(user, 'teacher_profile'):
                raise PermissionDenied(
                    'Teacher profile not found.'
                )

            if not user.teacher_profile.can_enter_grades:
                raise PermissionDenied(
                    'You do not have permission to edit grades.'
                )

            subject = serializer.validated_data.get(
                'subject',
                serializer.instance.subject
            )

            student = serializer.validated_data.get(
                'student',
                serializer.instance.student
            )

            teacher_subject = user.teacher_profile.subject

            selected_subject = subject

            if teacher_subject != selected_subject:
                raise PermissionDenied(
                    f'You are a {user.teacher_profile.subject.name} teacher. '
                    f'You cannot edit {subject.name} marks.'
                )

            assignment_exists = TeacherAssignment.objects.filter(
                teacher=user.teacher_profile,
                grade=student.grade,
                section=student.section,
                academic_year=student.academic_year
            ).exists()

            if not assignment_exists:
                raise PermissionDenied(
                    f'You are not assigned to Grade {student.grade} '
                    f'Section {student.section} for {student.academic_year}.'
                )

        serializer.save()


def get_final_results(student):

    records = GradeRecord.objects.filter(
        student=student,
        academic_year=student.academic_year
    ).select_related(
        'subject'
    ).order_by(
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
                Decimal(semester_1) +
                Decimal(semester_2)
            ) / Decimal('2')

        results.append({
            'subject_id': item['subject'].id,
            'subject': item['subject'].name,
            'code': item['subject'].code,
            'semester_1': semester_1,
            'semester_2': semester_2,
            'final_mark': final_mark,
        })

    return results


def get_student_final_average(student):

    results = get_final_results(student)

    completed = []

    for result in results:

        if result['final_mark'] is not None:
            completed.append(
                Decimal(result['final_mark'])
            )

        elif result['semester_1'] is not None:
            completed.append(
                Decimal(result['semester_1'])
            )

        elif result['semester_2'] is not None:
            completed.append(
                Decimal(result['semester_2'])
            )

    if not completed:
        return None

    total = sum(
        completed,
        Decimal('0')
    )

    return total / Decimal(len(completed))


class StudentResultsAPIView(GenericAPIView):

    serializer_class = StudentResultsSerializer

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, student_id):

        student = Student.objects.filter(
            pk=student_id
        ).first()

        if not student:
            return Response(
                {'detail': 'Student not found.'},
                status=404
            )

        if request.user.role == 'STUDENT':

            if not hasattr(request.user, 'student_profile'):
                raise PermissionDenied(
                    'Student profile not found.'
                )

            if request.user.student_profile.pk != student.pk:
                raise PermissionDenied(
                    'You can only view your own results.'
                )

        elif request.user.role == 'TEACHER':

            if not hasattr(request.user, 'teacher_profile'):
                raise PermissionDenied(
                    'Teacher profile not found.'
                )

            teacher = request.user.teacher_profile

            teacher_grade = str(
                teacher.grade
            ).strip()

            student_grade = str(
                student.grade
            ).strip()

            if teacher_grade != student_grade:
                raise PermissionDenied(
                    f'You are assigned to Grade {teacher.grade}. '
                    f'You cannot view results for Grade {student.grade}.'
                )

        results = get_final_results(student)

        average = get_student_final_average(student)

        passed = (
            average is not None
            and average >= Decimal('50')
        )

        completed = [
            result
            for result in results
            if result['final_mark'] is not None
        ]

        total = None

        if completed:
            total = sum(
                (
                    result['final_mark']
                    for result in completed
                ),
                Decimal('0')
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
            'results': results,
            'total': total,
            'average': average,
            'passed': passed,
        })


class StudentAverageAPIView(GenericAPIView):

    serializer_class = StudentAverageSerializer

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, student_id):

        student = Student.objects.filter(
            pk=student_id
        ).first()

        if not student:
            return Response(
                {'detail': 'Student not found.'},
                status=404
            )

        if request.user.role == 'STUDENT':

            if not hasattr(request.user, 'student_profile'):
                raise PermissionDenied(
                    'Student profile not found.'
                )

            if request.user.student_profile.pk != student.pk:
                raise PermissionDenied(
                    'You can only view your own average.'
                )

        elif request.user.role == 'TEACHER':

            if not hasattr(request.user, 'teacher_profile'):
                raise PermissionDenied(
                    'Teacher profile not found.'
                )

            teacher = request.user.teacher_profile

            assignment_exists = TeacherAssignment.objects.filter(
                teacher=teacher,
                grade=student.grade,
                section=student.section,
                academic_year=student.academic_year
            ).exists()

            if not assignment_exists:
                raise PermissionDenied(
                    f'You are not assigned to Grade {student.grade} '
                    f'Section {student.section} for {student.academic_year}.'
                )

        average = get_student_final_average(student)

        return Response({
            'student_id': student.id,
            'student_number': student.student_id,
            'student_name': (
                f'{student.first_name} '
                f'{student.father_name}'
            ),
            'average': average,
        })


class RankingAPIView(GenericAPIView):

    serializer_class = RankingSerializer

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        students = Student.objects.all()

        if request.user.role == 'TEACHER':

            if not hasattr(request.user, 'teacher_profile'):
                raise PermissionDenied(
                    'Teacher profile not found.'
                )

            teacher = request.user.teacher_profile

            students = students.filter(
                grade=teacher.grade
            )

        elif request.user.role == 'STUDENT':

            if not hasattr(request.user, 'student_profile'):
                raise PermissionDenied(
                    'Student profile not found.'
                )

            student_profile = request.user.student_profile

            students = students.filter(
                grade=student_profile.grade,
                section=student_profile.section
            )

            if student_profile.grade in [11, 12]:
                students = students.filter(
                    stream=student_profile.stream
                )

        rankings = []

        for student in students:

            average = get_student_final_average(student)

            if average is None:
                continue

            rankings.append({
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
            })

        rankings.sort(
            key=lambda item: item['average'],
            reverse=True
        )

        for position, item in enumerate(rankings, 1):
            item['rank'] = position

        return Response({
            'count': len(rankings),
            'rankings': rankings,
        })

class TeacherViewSet(viewsets.ModelViewSet):

    queryset = TeacherProfile.objects.select_related(
        'user'
    ).all().order_by(
        'teacher_id'
    )

    permission_classes = [IsDirector]

    def get_serializer_class(self):
        if self.action == 'create':
            return TeacherCreateSerializer
        return TeacherSerializer



from attendance.models import Attendance


class AttendanceViewSet(viewsets.ModelViewSet):

    queryset = Attendance.objects.select_related(
        'student'
    ).all().order_by(
        '-date',
        'student__first_name'
    )

    permission_classes = [IsDirectorOrTeacher]

    def get_serializer_class(self):
        return AttendanceSerializer

    def _teacher_profile(self):
        if self.request.user.role == 'TEACHER':
            return TeacherProfile.objects.get(user=self.request.user)
        return None

    def get_queryset(self):
        qs = super().get_queryset()

        if self.request.user.role == 'TEACHER':
            teacher = self._teacher_profile()

            return qs.filter(
                student__grade=teacher.grade
            )

        return qs

    def _check_teacher_permission(self):
        if self.request.user.role != 'TEACHER':
            return None

        teacher = self._teacher_profile()

        if not teacher.can_take_attendance:
            raise PermissionDenied(
                'You do not have permission to manage attendance.'
            )

        return teacher

    def _check_student_class(self, student, teacher):
        teacher_grade = str(teacher.grade).strip()
        student_grade = str(student.grade).strip()

        if teacher_grade != student_grade:
            raise PermissionDenied(
                f'You are assigned to Grade {teacher.grade}. '
                f'You cannot manage attendance for Grade {student.grade}.'
            )

    def perform_create(self, serializer):
        teacher = self._check_teacher_permission()

        if teacher is not None:
            if teacher_subject != selected_subject:
                raise PermissionDenied(
                    f'You are a {teacher_subject.name} teacher. '
                    f'You cannot enter {selected_subject.name} marks.'
                )

            student = serializer.validated_data['student']
            self._check_student_class(student, teacher)

        serializer.save()

    def perform_update(self, serializer):
        teacher = self._check_teacher_permission()

        if teacher is not None:
            student = serializer.validated_data.get(
                'student',
                serializer.instance.student
            )

            self._check_student_class(student, teacher)

        serializer.save()

    def perform_destroy(self, instance):
        teacher = self._check_teacher_permission()

        if teacher is not None:
            self._check_student_class(instance.student, teacher)

        instance.delete()



