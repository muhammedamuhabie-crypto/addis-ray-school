from django import forms
from accounts.models import User
from .models import TeacherProfile
from academics.models import Subject


class TeacherForm(forms.ModelForm):

    username = forms.CharField(
        label='Username',
        max_length=150,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'e.g. teacher001'
            }
        )
    )

    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'e.g. teacher@example.com'
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
        model = TeacherProfile
        exclude = [
            'user',
            'can_register_students',
            'can_take_attendance',
            'can_enter_grades',
            'can_view_reports'
        ]

        widgets = {
            'teacher_id': forms.TextInput(
                attrs={
                    'placeholder': 'e.g. T001'
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

            'subject': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),

            'hire_date': forms.DateInput(
                attrs={
                    'type': 'date'
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['subject'].queryset = Subject.objects.all().order_by('name')
        self.fields['subject'].empty_label = 'Select a subject'

        for name, field in self.fields.items():
            field.required = name != 'photo'

        if self.instance and self.instance.pk:
            self.fields['password'].help_text = (
                'Leave blank to keep the current password.'
            )

            self.fields['confirm_password'].help_text = (
                'Leave blank to keep the current password.'
            )

            if self.instance.user:
                self.fields['username'].initial = self.instance.user.username

        else:
            self.fields['password'].required = True
            self.fields['confirm_password'].required = True

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

    def clean_teacher_id(self):
        teacher_id = self.cleaned_data['teacher_id']

        qs = TeacherProfile.objects.filter(
            teacher_id=teacher_id
        )

        if self.instance.pk:
            qs = qs.exclude(
                pk=self.instance.pk
            )

        if qs.exists():
            raise forms.ValidationError(
                'This teacher ID is already registered.'
            )

        return teacher_id

    def clean(self):
        cleaned_data = super().clean()

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


class PermissionForm(forms.ModelForm):

    class Meta:
        model = TeacherProfile
        fields = [
            'can_register_students',
            'can_take_attendance',
            'can_enter_grades',
            'can_view_reports'
        ]



