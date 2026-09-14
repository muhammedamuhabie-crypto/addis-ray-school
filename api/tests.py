from datetime import date

from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import User
from academics.models import Subject
from students.models import Student
from teachers.models import TeacherProfile


class APIAuthorizationTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.subject = Subject.objects.create(
            name='Mathematics',
            code='MATH-TEST',
        )

        self.director = User.objects.create_user(
            username='api_test_director',
            email='api_test_director@example.com',
            password='TestPassword123!',
            role='DIRECTOR',
        )

        self.teacher = User.objects.create_user(
            username='api_test_teacher',
            email='api_test_teacher@example.com',
            password='TestPassword123!',
            role='TEACHER',
        )

        self.teacher_profile = TeacherProfile.objects.create(
            user=self.teacher,
            teacher_id='T-API-TEST',
            first_name='Test',
            father_name='Teacher',
            grandfather_name='Profile',
            gender='M',
            date_of_birth=date(1990, 1, 1),
            phone='0900000000',
            address='Test Address',
            qualification='Bachelor Degree',
            subject=self.subject,
            grade=9,
            section='A',
            hire_date=date(2020, 1, 1),
        )

        self.student = User.objects.create_user(
            username='api_test_student',
            email='api_test_student@example.com',
            password='TestPassword123!',
            role='STUDENT',
        )

        self.student_profile = Student.objects.create(
            user=self.student,
            student_id='S-API-TEST',
            first_name='Test',
            father_name='Student',
            grandfather_name='Profile',
            gender='M',
            date_of_birth=date(2010, 1, 1),
            phone='0911111111',
            address='Test Address',
            guardian_name='Test Guardian',
            guardian_phone='0922222222',
            grade=9,
            section='A',
            academic_year='2026',
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_director_authorization_allows_director(self):
        self.authenticate(self.director)
        response = self.client.get('/api/authorization/director/')
        self.assertEqual(response.status_code, 200)

    def test_director_authorization_rejects_teacher(self):
        self.authenticate(self.teacher)
        response = self.client.get('/api/authorization/director/')
        self.assertEqual(response.status_code, 403)

    def test_teacher_authorization_allows_teacher(self):
        self.authenticate(self.teacher)
        response = self.client.get('/api/authorization/teacher/')
        self.assertEqual(response.status_code, 200)

    def test_teacher_authorization_rejects_student(self):
        self.authenticate(self.student)
        response = self.client.get('/api/authorization/teacher/')
        self.assertEqual(response.status_code, 403)

    def test_student_authorization_allows_student(self):
        self.authenticate(self.student)
        response = self.client.get('/api/authorization/student/')
        self.assertEqual(response.status_code, 200)

    def test_student_authorization_rejects_teacher(self):
        self.authenticate(self.teacher)
        response = self.client.get('/api/authorization/student/')
        self.assertEqual(response.status_code, 403)

    def test_students_service_allows_teacher(self):
        self.authenticate(self.teacher)
        response = self.client.get('/api/services/students/')
        self.assertEqual(response.status_code, 200)

    def test_students_service_rejects_student(self):
        self.authenticate(self.student)
        response = self.client.get('/api/services/students/')
        self.assertEqual(response.status_code, 403)

    def test_teachers_service_allows_director(self):
        self.authenticate(self.director)
        response = self.client.get('/api/services/teachers/')
        self.assertEqual(response.status_code, 200)

    def test_teachers_service_rejects_teacher(self):
        self.authenticate(self.teacher)
        response = self.client.get('/api/services/teachers/')
        self.assertEqual(response.status_code, 403)

    def test_promotion_service_allows_director(self):
        self.authenticate(self.director)
        response = self.client.get('/api/services/promotion/')
        self.assertEqual(response.status_code, 200)

    def test_promotion_service_rejects_teacher(self):
        self.authenticate(self.teacher)
        response = self.client.get('/api/services/promotion/')
        self.assertEqual(response.status_code, 403)

    def test_settings_service_rejects_student(self):
        self.authenticate(self.student)
        response = self.client.get('/api/services/settings/')
        self.assertEqual(response.status_code, 403)

    def test_student_api_rejects_student(self):
        self.authenticate(self.student)
        response = self.client.get('/api/students/')
        self.assertEqual(response.status_code, 403)

    def test_student_api_allows_teacher(self):
        self.authenticate(self.teacher)
        response = self.client.get('/api/students/')
        self.assertEqual(response.status_code, 200)

    def test_promotion_api_rejects_teacher(self):
        self.authenticate(self.teacher)
        response = self.client.get('/api/promotion/')
        self.assertEqual(response.status_code, 403)

    def test_promotion_api_rejects_student(self):
        self.authenticate(self.student)
        response = self.client.get('/api/promotion/')
        self.assertEqual(response.status_code, 403)

    def test_promotion_api_allows_director(self):
        self.authenticate(self.director)
        response = self.client.get('/api/promotion/')
        self.assertEqual(response.status_code, 200)

    def test_school_performance_rejects_teacher(self):
        self.authenticate(self.teacher)
        response = self.client.get('/api/reports/school/')
        self.assertEqual(response.status_code, 403)

    def test_school_performance_rejects_student(self):
        self.authenticate(self.student)
        response = self.client.get('/api/reports/school/')
        self.assertEqual(response.status_code, 403)

    def test_student_report_rejects_teacher(self):
        self.authenticate(self.teacher)
        response = self.client.get('/api/reports/student/')
        self.assertEqual(response.status_code, 403)

    def test_student_report_allows_student(self):
        self.authenticate(self.student)
        response = self.client.get('/api/reports/student/')
        self.assertEqual(response.status_code, 200)

    def test_class_report_rejects_student(self):
        self.authenticate(self.student)
        response = self.client.get('/api/reports/class/')
        self.assertEqual(response.status_code, 403)

    def test_attendance_report_rejects_student(self):
        self.authenticate(self.student)
        response = self.client.get('/api/reports/attendance/')
        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_cannot_access_current_user(self):
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, 401)

    def test_anonymous_user_cannot_access_students(self):
        response = self.client.get('/api/students/')
        self.assertEqual(response.status_code, 401)
