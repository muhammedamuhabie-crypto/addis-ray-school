from django.db import models
from students.models import Student


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f'{self.name} ({self.code})'


class ClassRoom(models.Model):
    GRADES = [
        (9, 'Grade 9'),
        (10, 'Grade 10'),
        (11, 'Grade 11'),
        (12, 'Grade 12'),
    ]

    SECTIONS = [
        (x, x) for x in 'ABCDEF'
    ]

    grade = models.PositiveSmallIntegerField(
        choices=GRADES
    )

    section = models.CharField(
        max_length=1,
        choices=SECTIONS
    )

    academic_year = models.CharField(
        max_length=20
    )

    class Meta:
        unique_together = (
            'grade',
            'section',
            'academic_year'
        )

    def __str__(self):
        return f'Grade {self.grade}-{self.section} ({self.academic_year})'


class GradeRecord(models.Model):

    SEMESTER_CHOICES = [
        ('SEMESTER_1', 'Semester 1'),
        ('SEMESTER_2', 'Semester 2'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='grade_records'
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    academic_year = models.CharField(
        max_length=20
    )

    semester = models.CharField(
        max_length=20,
        choices=SEMESTER_CHOICES,
        default='SEMESTER_1'
    )

    mark = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    class Meta:
        unique_together = (
            'student',
            'subject',
            'academic_year',
            'semester'
        )

    def __str__(self):
        return f'{self.student} - {self.subject} - {self.semester}'
