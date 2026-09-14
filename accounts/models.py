from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [('DIRECTOR','Director'),('TEACHER','Teacher'),('STUDENT','Student')]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STUDENT')
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    REQUIRED_FIELDS = ['email']
    def __str__(self): return self.get_full_name() or self.email

class SchoolSettings(models.Model):
    school_name = models.CharField(
        max_length=200,
        default='Addis Ray Secondary School'
    )
    school_address = models.TextField(blank=True)
    school_phone = models.CharField(max_length=30, blank=True)
    school_email = models.EmailField(blank=True)
    school_logo = models.ImageField(
        upload_to='school/',
        blank=True,
        null=True
    )
    academic_year = models.CharField(
        max_length=20,
        default='2026/2027'
    )

    SEMESTER_CHOICES = [
        ('SEMESTER_1', 'Semester 1'),
        ('SEMESTER_2', 'Semester 2'),
    ]

    current_semester = models.CharField(
        max_length=12,
        choices=SEMESTER_CHOICES,
        default='SEMESTER_1'
    )
    passing_mark = models.PositiveSmallIntegerField(default=50)
    attendance_daily = models.BooleanField(default=True)
    ranking_enabled = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.school_name
