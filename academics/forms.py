from django import forms

from .models import GradeRecord, Subject, ClassRoom
from students.models import Student


class GradeRecordForm(forms.ModelForm):

    grade = forms.ChoiceField(
        choices=[
            ('', 'Select grade')
        ] + [
            (str(value), label)
            for value, label in Student.GRADES
        ],
        widget=forms.Select(
            attrs={
                'class': 'form-select',
                'id': 'id_grade'
            }
        )
    )

    section = forms.ChoiceField(
        choices=[
            ('', 'Select section')
        ] + [
            (value, label)
            for value, label in Student.SECTIONS
        ],
        widget=forms.Select(
            attrs={
                'class': 'form-select',
                'id': 'id_section'
            }
        )
    )

    stream = forms.ChoiceField(
        choices=[
            ('', 'Select stream')
        ] + [
            (value, label)
            for value, label in Student.STREAMS
        ],
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-select',
                'id': 'id_stream'
            }
        )
    )

    class Meta:
        model = GradeRecord

        fields = [
            'grade',
            'section',
            'stream',
            'student',
            'subject',
            'academic_year',
            'semester',
            'mark',
        ]

        widgets = {

            'student': forms.Select(
                attrs={
                    'class': 'form-select',
                    'id': 'id_student'
                }
            ),

            'subject': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'academic_year': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Example: 2026/27'
                }
            ),

            'semester': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'mark': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter mark (0-100)',
                    'min': 0,
                    'max': 100,
                    'step': '0.01'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['student'].queryset = Student.objects.none()

        grade = self.data.get('grade') or self.initial.get('grade')
        section = self.data.get('section') or self.initial.get('section')
        stream = self.data.get('stream') or self.initial.get('stream')

        if grade and section:

            students = Student.objects.filter(
                grade=grade,
                section=section
            )

            if str(grade) in ['11', '12'] and stream:
                students = students.filter(
                    stream=stream
                )

            self.fields['student'].queryset = students.order_by(
                'student_id'
            )

    def clean(self):

        cleaned_data = super().clean()

        grade = cleaned_data.get('grade')
        section = cleaned_data.get('section')
        stream = cleaned_data.get('stream')
        student = cleaned_data.get('student')
        mark = cleaned_data.get('mark')

        if grade and section and student:

            if (
                student.grade != int(grade)
                or student.section != section
            ):
                raise forms.ValidationError(
                    'The selected student does not belong to the selected grade and section.'
                )

            if int(grade) in [11, 12]:

                if not stream:
                    self.add_error(
                        'stream',
                        'Stream is required for Grade 11 and Grade 12.'
                    )

                elif student.stream != stream:
                    self.add_error(
                        'student',
                        'The selected student does not belong to the selected stream.'
                    )

            else:

                if stream:
                    self.add_error(
                        'stream',
                        'Stream is only used for Grade 11 and Grade 12.'
                    )

        if mark is not None:

            if mark < 0 or mark > 100:
                self.add_error(
                    'mark',
                    'Mark must be between 0 and 100.'
                )

        return cleaned_data


class SubjectForm(forms.ModelForm):

    class Meta:
        model = Subject
        fields = ['name', 'code']


class ClassRoomForm(forms.ModelForm):

    class Meta:
        model = ClassRoom
        fields = ['grade', 'section', 'academic_year']
