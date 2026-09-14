from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from students.models import Student
from teachers.models import TeacherProfile
from attendance.models import Attendance
from academics.models import GradeRecord
@login_required
def dashboard(request):
    context={'student_count':Student.objects.count(),'teacher_count':TeacherProfile.objects.count(),'attendance_count':Attendance.objects.count(),'result_count':GradeRecord.objects.count()}
    return render(request, f'dashboard/{request.user.role.lower()}_dashboard.html', context)
