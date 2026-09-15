from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, SchoolSettings


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Email or username',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Email or username'
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Password'
            }
        )
    )


class UsernameRecoveryForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Your registered email'
            }
        )
    )


class CreateUserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Password'
            }
        )
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'password',
        ]

        widgets = {
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Username'
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Email'
                }
            ),
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'First name'
                }
            ),
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Last name'
                }
            ),
            'role': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

        return user


class SchoolSettingsForm(forms.ModelForm):

    remove_school_logo = forms.BooleanField(
        required=False,
        label='Remove current logo'
    )

    class Meta:
        model = SchoolSettings

        fields = [
            'school_name',
            'school_address',
            'school_phone',
            'school_email',
            'school_logo',
            'academic_year',
            'current_semester',
            'passing_mark',
            'attendance_daily',
            'ranking_enabled',
        ]

        widgets = {
            'school_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'School name'
                }
            ),

            'school_address': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'School address',
                    'rows': 3
                }
            ),

            'school_phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'School phone number'
                }
            ),

            'school_email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'School email address'
                }
            ),

            'school_logo': forms.FileInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'academic_year': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Example: 2026/2027'
                }
            ),

            'current_semester': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'passing_mark': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Example: 50',
                    'min': 0,
                    'max': 100
                }
            ),

            'attendance_daily': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'
                }
            ),

            'ranking_enabled': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'
                }
            ),
        }


