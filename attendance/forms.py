from django import forms
from .models import Attendance
class AttendanceForm(forms.ModelForm):
    class Meta: model=Attendance; fields=['date','status']; widgets={'date':forms.DateInput(attrs={'type':'date'})}
