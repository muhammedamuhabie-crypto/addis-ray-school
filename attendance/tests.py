from datetime import date

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from students.models import Student
from attendance.models import Attendance


class AttendanceSecurityTests(TestCase):

    def setUp(self):
        self.director = User.objects.create_user(
            username='attendance_director',
            email='attendance_director@example.com',
            password='TestPassword123!',
            role='DIRECTOR',
        )

        self.teacher = User.objects.create_user(
            username='attendance_teacher',
            email='attendance_teacher@example.com',
            password='TestPassword123!',
            role='TEACHER',
        )

        self.student_user = User.objects.create_user(
            username='attendance_student_1',
            email='attendance_student_1@example.com',
            password='TestPassword123!',
            role='STUDENT',
        )

        self.other_student_user = User.objects.create_user(
            username='attendance_student_2',
            email='attendance_student_2@example.com',
            password='TestPassword123!',
            role='STUDENT',
        )

        self.student = Student.objects.create(
            user=self.student_user,
            student_id='ATT-STU-001',
            first_name='Attendance',
            father_name='Student',
            grandfather_name='One',
            gender='M',
            date_of_birth=date(2008, 1, 1),
            phone='0900000101',
            address='Test Address',
            guardian_name='Test Guardian',
            guardian_phone='0900000111',
            grade=9,
            section='A',
            academic_year='2026/2027',
        )

        self.other_student = Student.objects.create(
            user=self.other_student_user,
            student_id='ATT-STU-002',
            first_name='Other',
            father_name='Student',
            grandfather_name='Two',
            gender='M',
            date_of_birth=date(2008, 2, 2),
            phone='0900000102',
            address='Test Address',
            guardian_name='Other Guardian',
            guardian_phone='0900000112',
            grade=9,
            section='A',
            academic_year='2026/2027',
        )

        Attendance.objects.create(
            student=self.student,
            date=date(2026, 9, 1),
            status='P',
        )

        Attendance.objects.create(
            student=self.other_student,
            date=date(2026, 9, 1),
            status='A',
        )

    def test_student_can_view_own_attendance(self):
        self.client.force_login(self.student_user)

        response = self.client.get(
            reverse('student_attendance', args=[self.student.pk])
        )

        self.assertEqual(response.status_code, 200)

    def test_student_cannot_view_another_student_attendance(self):
        self.client.force_login(self.student_user)

        response = self.client.get(
            reverse('student_attendance', args=[self.other_student.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))

    def test_student_cannot_view_full_attendance_records(self):
        self.client.force_login(self.student_user)

        response = self.client.get(
            reverse('attendance_records')
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))

    def test_student_cannot_view_attendance_report(self):
        self.client.force_login(self.student_user)

        response = self.client.get(
            reverse('attendance_report')
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))

    def test_teacher_can_view_attendance_records(self):
        self.client.force_login(self.teacher)

        response = self.client.get(
            reverse('attendance_records')
        )

        self.assertEqual(response.status_code, 200)

    def test_teacher_can_view_attendance_report(self):
        self.client.force_login(self.teacher)

        response = self.client.get(
            reverse('attendance_report')
        )

        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_is_redirected_from_attendance_records(self):
        response = self.client.get(
            reverse('attendance_records')
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_anonymous_user_is_redirected_from_student_attendance(self):
        response = self.client.get(
            reverse('student_attendance', args=[self.student.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
