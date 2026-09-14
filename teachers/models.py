from django.db import models
from accounts.models import User
class TeacherProfile(models.Model):
    GENDERS=[('M','Male'),('F','Female')]; SECTIONS=[(x,x) for x in 'ABCDEF']; GRADES=[(9,'Grade 9'),(10,'Grade 10'),(11,'Grade 11'),(12,'Grade 12')]
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='teacher_profile')
    teacher_id=models.CharField(max_length=30,unique=True); first_name=models.CharField(max_length=80); father_name=models.CharField(max_length=80); grandfather_name=models.CharField(max_length=80)
    gender=models.CharField(max_length=1,choices=GENDERS); date_of_birth=models.DateField(); phone=models.CharField(max_length=30); address=models.TextField(); qualification=models.CharField(max_length=150)
    subject=models.ForeignKey('academics.Subject', on_delete=models.PROTECT, related_name='teacher_profiles'); grade=models.PositiveSmallIntegerField(choices=GRADES); section=models.CharField(max_length=1,choices=SECTIONS); hire_date=models.DateField(); photo=models.ImageField(upload_to='teachers/',blank=True,null=True)
    can_register_students=models.BooleanField(default=False); can_take_attendance=models.BooleanField(default=False); can_enter_grades=models.BooleanField(default=False); can_view_reports=models.BooleanField(default=False)
    def __str__(self): return f'{self.teacher_id} - {self.first_name} {self.father_name}'


class TeacherAssignment(models.Model):
    GRADES = [(9,'Grade 9'),(10,'Grade 10'),(11,'Grade 11'),(12,'Grade 12')]
    SECTIONS = [(x,x) for x in 'ABCDEF']

    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    grade = models.PositiveSmallIntegerField(choices=GRADES)
    section = models.CharField(max_length=1, choices=SECTIONS)
    academic_year = models.CharField(max_length=20)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['teacher','grade','section','academic_year'],
                name='unique_teacher_class_assignment'
            )
        ]
        ordering = ['academic_year','grade','section']

    def __str__(self):
        return f'{self.teacher.teacher_id} - Grade {self.grade} Section {self.section} - {self.academic_year}'


