from datetime import date

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from academics.models import Subject
from teachers.models import TeacherProfile


class TeacherSecurityTests(TestCase):

    def setUp(self):
        self.director = User.objects.create_user(
            username='teacher_test_director',
            email='teacher_test_director@example.com',
            password='TestPassword123!',
            role='DIRECTOR',
        )

        self.teacher_user = User.objects.create_user(
            username='teacher_test_user',
            email='teacher_test_user@example.com',
            password='TestPassword123!',
            role='TEACHER',
        )

        self.subject = Subject.objects.create(
            name='Test Mathematics',
        )

        self.teacher = TeacherProfile.objects.create(
            user=self.teacher_user,
            teacher_id='TEST-TEACHER-001',
            first_name='Test',
            father_name='Teacher',
            grandfather_name='One',
            gender='M',
            date_of_birth=date(1985, 1, 1),
            phone='0900000201',
            address='Test Address',
            qualification='Bachelor Degree',
            subject=self.subject,
            grade=9,
            section='A',
            hire_date=date(2020, 1, 1),
        )

    def test_teacher_cannot_edit_teacher_profile(self):
        self.client.force_login(self.teacher_user)

        response = self.client.get(
            reverse('edit_teacher', args=[self.teacher.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))

    def test_director_can_edit_teacher_profile(self):
        self.client.force_login(self.director)

        response = self.client.get(
            reverse('edit_teacher', args=[self.teacher.pk])
        )

        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_is_redirected_from_teacher_edit(self):
        response = self.client.get(
            reverse('edit_teacher', args=[self.teacher.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
