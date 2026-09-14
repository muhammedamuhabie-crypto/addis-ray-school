from django.db import models
from students.models import Student


class Promotion(models.Model):
    STATUS = [
        ('PASS', 'PASS'),
        ('FAIL', 'FAIL'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='promotions'
    )

    from_grade = models.PositiveSmallIntegerField()

    to_grade = models.PositiveSmallIntegerField(
        null=True,
        blank=True
    )

    academic_year = models.CharField(
        max_length=20
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
