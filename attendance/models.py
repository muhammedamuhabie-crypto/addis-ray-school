from django.db import models
from students.models import Student
class Attendance(models.Model):
    STATUS=[('P','Present'),('A','Absent'),('L','Late')]
    student=models.ForeignKey(Student,on_delete=models.CASCADE,related_name='attendance_records'); date=models.DateField(); status=models.CharField(max_length=1,choices=STATUS)
    class Meta: unique_together=('student','date'); ordering=['-date','student__first_name']
    def __str__(self): return f'{self.student} - {self.date} - {self.get_status_display()}'
