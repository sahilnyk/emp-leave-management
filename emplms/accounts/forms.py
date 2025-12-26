from django import forms
from django.contrib.auth.models import User

ROLE_CHOICES = (
    ('employee', 'Employee'),
    ('manager', 'Manager'),
)

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Create password"})
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Enter username"}),
            "email": forms.EmailInput(attrs={"placeholder": "Enter email"}),
        }

        help_texts = {
            "username": "",
            "email": "",
            "password": "",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = ""
        self.fields['email'].help_text = ""


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Enter username"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Enter password"})
    )
