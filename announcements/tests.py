from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Announcement


User = get_user_model()


class AnnouncementAuthorizationTests(TestCase):

    def setUp(self):
        self.director = User.objects.create_user(
            username="announcement_director",
            email="announcement_director@test.local",
            password="TestPassword123!",
            role="DIRECTOR",
        )

        self.teacher = User.objects.create_user(
            username="announcement_teacher",
            email="announcement_teacher@test.local",
            password="TestPassword123!",
            role="TEACHER",
        )

        self.student = User.objects.create_user(
            username="announcement_student",
            email="announcement_student@test.local",
            password="TestPassword123!",
            role="STUDENT",
        )

    def test_director_can_create_announcement(self):
        self.client.force_login(self.director)

        response = self.client.post(
            reverse("announcement_create"),
            {
                "title": "Director Notice",
                "message": "Important school message.",
                "priority": "IMPORTANT",
                "audience": "Fake Audience",
            },
        )

        self.assertRedirects(response, reverse("announcement_list"))

        announcement = Announcement.objects.get(title="Director Notice")

        self.assertEqual(announcement.posted_by, self.director)
        self.assertEqual(announcement.audience, "All Teachers & Students")

    def test_teacher_can_create_announcement(self):
        self.client.force_login(self.teacher)

        response = self.client.post(
            reverse("announcement_create"),
            {
                "title": "Teacher Notice",
                "message": "Important class message.",
                "priority": "NORMAL",
                "audience": "Fake Audience",
            },
        )

        self.assertRedirects(response, reverse("announcement_list"))

        announcement = Announcement.objects.get(title="Teacher Notice")

        self.assertEqual(announcement.posted_by, self.teacher)
        self.assertEqual(announcement.audience, "All Students")

    def test_student_cannot_create_announcement(self):
        self.client.force_login(self.student)

        response = self.client.post(
            reverse("announcement_create"),
            {
                "title": "Student Notice",
                "message": "Unauthorized message.",
                "priority": "NORMAL",
                "audience": "All Teachers & Students",
            },
        )

        self.assertRedirects(response, reverse("announcement_list"))
        self.assertFalse(
            Announcement.objects.filter(title="Student Notice").exists()
        )

    def test_student_can_view_announcements(self):
        Announcement.objects.create(
            title="School Notice",
            audience="All Teachers & Students",
            message="School message.",
            posted_by=self.director,
        )

        Announcement.objects.create(
            title="Student Notice",
            audience="All Students",
            message="Student message.",
            posted_by=self.teacher,
        )

        self.client.force_login(self.student)

        response = self.client.get(reverse("announcement_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "School Notice")
        self.assertContains(response, "Student Notice")

    def test_teacher_can_view_both_audiences(self):
        Announcement.objects.create(
            title="Director Notice",
            audience="All Teachers & Students",
            message="Director message.",
            posted_by=self.director,
        )

        Announcement.objects.create(
            title="Teacher Notice",
            audience="All Students",
            message="Teacher message.",
            posted_by=self.teacher,
        )

        self.client.force_login(self.teacher)

        response = self.client.get(reverse("announcement_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Director Notice")
        self.assertContains(response, "Teacher Notice")

    def test_user_cannot_edit_another_users_announcement(self):
        announcement = Announcement.objects.create(
            title="Director Notice",
            audience="All Teachers & Students",
            message="Original message.",
            posted_by=self.director,
        )

        self.client.force_login(self.teacher)

        response = self.client.post(
            reverse("announcement_edit", args=[announcement.pk]),
            {
                "title": "Changed Notice",
                "message": "Changed message.",
                "priority": "URGENT",
            },
        )

        self.assertRedirects(response, reverse("announcement_list"))

        announcement.refresh_from_db()

        self.assertEqual(announcement.title, "Director Notice")
        self.assertEqual(announcement.message, "Original message.")
        self.assertEqual(announcement.posted_by, self.director)

    def test_user_cannot_delete_another_users_announcement(self):
        announcement = Announcement.objects.create(
            title="Director Notice",
            audience="All Teachers & Students",
            message="Original message.",
            posted_by=self.director,
        )

        self.client.force_login(self.teacher)

        response = self.client.post(
            reverse("announcement_delete", args=[announcement.pk])
        )

        self.assertRedirects(response, reverse("announcement_list"))
        self.assertTrue(
            Announcement.objects.filter(pk=announcement.pk).exists()
        )
