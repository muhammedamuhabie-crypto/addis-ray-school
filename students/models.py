from django.db import models
from accounts.models import User


class Student(models.Model):
    GENDERS = [
        ('M', 'Male'),
        ('F', 'Female')
    ]

    GRADES = [
        (9, 'Grade 9'),
        (10, 'Grade 10'),
        (11, 'Grade 11'),
        (12, 'Grade 12')
    ]

    SECTIONS = [
        (x, x) for x in 'ABCDEF'
    ]

    STREAMS = [
        ('NATURAL', 'Natural'),
        ('SOCIAL', 'Social')
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )

    student_id = models.CharField(
        max_length=30,
        unique=True
    )

    first_name = models.CharField(max_length=80)
    father_name = models.CharField(max_length=80)
    grandfather_name = models.CharField(max_length=80)

    gender = models.CharField(
        max_length=1,
        choices=GENDERS
    )

    date_of_birth = models.DateField()

    phone = models.CharField(max_length=30)
    address = models.TextField()

    guardian_name = models.CharField(max_length=150)
    guardian_phone = models.CharField(max_length=30)

    grade = models.PositiveSmallIntegerField(
        choices=GRADES
    )

    section = models.CharField(
        max_length=1,
        choices=SECTIONS
    )

    stream = models.CharField(
        max_length=10,
        choices=STREAMS,
        blank=True,
        null=True
    )

    academic_year = models.CharField(
        max_length=20
    )

    photo = models.ImageField(
        upload_to='students/',
        blank=True,
        null=True
    )

    def __str__(self):
        return f'{self.student_id} - {self.first_name} {self.father_name}'
