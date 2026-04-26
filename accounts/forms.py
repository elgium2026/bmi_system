from django import forms
from django.contrib.auth.models import User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    email = forms.EmailField(required=True)  # ✅ REQUIRED FOR OTP

    PERSONNEL_CHOICES = [
        ('PCO', 'PCO'),
        ('PNCO', 'PNCO'),
        ('NUP', 'NUP'),
    ]

    personnel_type = forms.ChoiceField(choices=PERSONNEL_CHOICES)
    unit = forms.CharField(max_length=100)
    rank = forms.CharField(max_length=50)

    first_name = forms.CharField(max_length=100)
    middle_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100)

    birthdate = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    sex = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female')])

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password != confirm:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data


class BMIForm(forms.Form):
    sex = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female')])
    weight = forms.FloatField(label="Weight (kg)")
    height = forms.FloatField(label="Height (cm)")
    waist = forms.FloatField(label="Waist (cm)")
    hip = forms.FloatField(label="Hip (cm)")
    wrist = forms.FloatField(label="Wrist (cm)")