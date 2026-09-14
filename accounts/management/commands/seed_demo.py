from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import User
from students.models import Student
from teachers.models import TeacherProfile
from academics.models import Subject,ClassRoom,GradeRecord
from attendance.models import Attendance
from datetime import date
class Command(BaseCommand):
    help='Create demo users and sample school data.'
    @transaction.atomic
    def handle(self,*args,**kwargs):
        director,_=User.objects.get_or_create(username='director',defaults={'email':'director@addisray.local','first_name':'School','last_name':'Director','role':'DIRECTOR','is_staff':True,'is_superuser':True}); director.email='director@addisray.local'; director.role='DIRECTOR'; director.set_password('Director123!'); director.is_staff=True; director.is_superuser=True; director.save()
        teacher,_=User.objects.get_or_create(username='teacher',defaults={'email':'teacher@addisray.local','first_name':'Demo','last_name':'Teacher','role':'TEACHER'}); teacher.set_password('Teacher123!'); teacher.email='teacher@addisray.local'; teacher.role='TEACHER'; teacher.save()
        mathematics,_=Subject.objects.get_or_create(code='MATH',defaults={'name':'Mathematics'})
        tp,_=TeacherProfile.objects.get_or_create(user=teacher,defaults={'teacher_id':'T001','first_name':'Demo','father_name':'Teacher','grandfather_name':'User','gender':'M','date_of_birth':date(1990,1,1),'phone':'0900000000','address':'Addis Ababa','qualification':'BSc','subject':mathematics,'grade':9,'section':'A','hire_date':date(2025,9,1),'can_register_students':True,'can_take_attendance':True,'can_enter_grades':True,'can_view_reports':True})
        tp.can_register_students=tp.can_take_attendance=tp.can_enter_grades=tp.can_view_reports=True; tp.save()
        student_user,_=User.objects.get_or_create(username='S001',defaults={'email':'student@addisray.local','first_name':'Demo','last_name':'Student','role':'STUDENT'}); student_user.set_password('Student123!'); student_user.email='student@addisray.local'; student_user.role='STUDENT'; student_user.save()
        student,_=Student.objects.get_or_create(user=student_user,defaults={'student_id':'S001','first_name':'Demo','father_name':'Student','grandfather_name':'User','gender':'M','date_of_birth':date(2010,1,1),'phone':'0911111111','address':'Addis Ababa','guardian_name':'Demo Guardian','guardian_phone':'0922222222','grade':9,'section':'A','academic_year':'2026/27'})
        for name,code,mark in [('Mathematics','MATH',78),('Physics','PHYS',82),('English','ENG',74),('Chemistry','CHEM',80)]:
            sub,_=Subject.objects.get_or_create(code=code,defaults={'name':name}); GradeRecord.objects.update_or_create(student=student,subject=sub,academic_year='2026/27',defaults={'mark':mark})
        ClassRoom.objects.get_or_create(grade=9,section='A',academic_year='2026/27')
        Attendance.objects.update_or_create(student=student,date=date.today(),defaults={'status':'P'})
        self.stdout.write(self.style.SUCCESS('Demo data created successfully.'))

