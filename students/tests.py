from datetime import date

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from students.models import Student


class StudentSecurityTests(TestCase):

    def setUp(self):
        self.director = User.objects.create_user(
            username='test_director',
            email='test_director@example.com',
            password='TestPassword123!',
            role='DIRECTOR',
        )

        self.student_user = User.objects.create_user(
            username='test_student_1',
            email='test_student_1@example.com',
            password='TestPassword123!',
            role='STUDENT',
        )

        self.other_student_user = User.objects.create_user(
            username='test_student_2',
            email='test_student_2@example.com',
            password='TestPassword123!',
            role='STUDENT',
        )

        self.student = Student.objects.create(
            user=self.student_user,
            student_id='TEST-STU-001',
            first_name='Test',
            father_name='Student',
            grandfather_name='One',
            gender='M',
            date_of_birth=date(2008, 1, 1),
            phone='0900000001',
            address='Test Address',
            guardian_name='Test Guardian',
            guardian_phone='0900000011',
            grade=9,
            section='A',
            academic_year='2026/2027',
        )

        self.other_student = Student.objects.create(
            user=self.other_student_user,
            student_id='TEST-STU-002',
            first_name='Other',
            father_name='Student',
            grandfather_name='Two',
            gender='M',
            date_of_birth=date(2008, 2, 2),
            phone='0900000002',
            address='Test Address',
            guardian_name='Other Guardian',
            guardian_phone='0900000022',
            grade=9,
            section='A',
            academic_year='2026/2027',
        )

    def test_student_can_view_own_profile(self):
        self.client.force_login(self.student_user)

        response = self.client.get(
            reverse('student_detail', args=[self.student.pk])
        )

        self.assertEqual(response.status_code, 200)

    def test_student_cannot_view_another_student_profile(self):
        self.client.force_login(self.student_user)

        response = self.client.get(
            reverse('student_detail', args=[self.other_student.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))

    def test_anonymous_user_is_redirected_from_student_profile(self):
        response = self.client.get(
            reverse('student_detail', args=[self.student.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
