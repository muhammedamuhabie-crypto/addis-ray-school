from django import forms
from accounts.models import User
from .models import Student


class StudentForm(forms.ModelForm):

    username = forms.CharField(
        label='Username',
        max_length=150,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'e.g. abebe09'
            }
        )
    )

    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'e.g. student@example.com'
            }
        )
    )

    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Enter a secure password'
            }
        ),
        required=False
    )

    confirm_password = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Re-enter the password'
            }
        ),
        required=False
    )

    class Meta:
        model = Student
        exclude = ['user']

        widgets = {
            'student_id': forms.TextInput(
                attrs={
                    'placeholder': 'e.g. ST001'
                }
            ),

            'first_name': forms.TextInput(
                attrs={
                    'placeholder': 'e.g. Abebe'
                }
            ),

            'father_name': forms.TextInput(
                attrs={
                    'placeholder': 'e.g. Kebede'
                }
            ),

            'grandfather_name': forms.TextInput(
                attrs={
                    'placeholder': 'e.g. Alemu'
                }
            ),

            'date_of_birth': forms.DateInput(
                attrs={
                    'type': 'date'
                }
            ),

            'phone': forms.TextInput(
                attrs={
                    'placeholder': 'e.g. 0912345678'
                }
            ),

            'address': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'e.g. Addis Ababa'
                }
            ),

            'guardian_name': forms.TextInput(
                attrs={
                    'placeholder': 'e.g. Abebe Kebede'
                }
            ),

            'guardian_phone': forms.TextInput(
                attrs={
                    'placeholder': 'e.g. 0912345678'
                }
            ),

            'academic_year': forms.TextInput(
                attrs={
                    'placeholder': 'e.g. 2026/2027'
                }
            ),

            'stream': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'photo': forms.ClearableFileInput(
                attrs={}
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['password'].help_text = (
                'Leave blank to keep the current password.'
            )

            self.fields['confirm_password'].help_text = (
                'Leave blank to keep the current password.'
            )

        else:
            self.fields['password'].required = True
            self.fields['confirm_password'].required = True

        self.fields['stream'].required = False

    def clean_username(self):
        username = self.cleaned_data['username']

        qs = User.objects.filter(
            username=username
        )

        if self.instance.pk:
            qs = qs.exclude(
                pk=self.instance.user_id
            )

        if qs.exists():
            raise forms.ValidationError(
                'This username is already registered.'
            )

        return username

    def clean_email(self):
        email = self.cleaned_data['email']

        qs = User.objects.filter(
            email=email
        )

        if self.instance.pk:
            qs = qs.exclude(
                pk=self.instance.user_id
            )

        if qs.exists():
            raise forms.ValidationError(
                'This email is already registered.'
            )

        return email

    def clean_student_id(self):
        student_id = self.cleaned_data['student_id']

        qs = Student.objects.filter(
            student_id=student_id
        )

        if self.instance.pk:
            qs = qs.exclude(
                pk=self.instance.pk
            )

        if qs.exists():
            raise forms.ValidationError(
                'This student ID is already registered.'
            )

        return student_id

    def clean(self):
        cleaned_data = super().clean()

        grade = cleaned_data.get('grade')
        stream = cleaned_data.get('stream')

        if grade in [11, 12] and not stream:
            self.add_error(
                'stream',
                'Stream is required for Grade 11 and Grade 12.'
            )

        if grade in [9, 10]:
            cleaned_data['stream'] = None

        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if not self.instance.pk:

            if not password:
                self.add_error(
                    'password',
                    'Password is required.'
                )

            if not confirm_password:
                self.add_error(
                    'confirm_password',
                    'Please confirm the password.'
                )

        if password or confirm_password:

            if password != confirm_password:
                self.add_error(
                    'confirm_password',
                    'Passwords do not match.'
                )

        return cleaned_data
