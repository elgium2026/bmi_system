from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile


@login_required
def home(request):
    return render(request, 'accounts/home.html')


@login_required
def bmi_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        try:
            weight = float(request.POST.get('weight'))
            height_cm = float(request.POST.get('height'))
            height_m = height_cm / 100

            bmi = weight / (height_m ** 2)

            if bmi < 18.5:
                category = "Underweight"
            elif bmi < 25:
                category = "Normal"
            elif bmi < 30:
                category = "Overweight"
            else:
                category = "Obese"

            return render(request, 'accounts/bmi_result.html', {
                'bmi': round(bmi, 2),
                'category': category
            })

        except (TypeError, ValueError):
            return render(request, 'accounts/bmi_form.html', {
                'error': 'Invalid input'
            })

    return render(request, 'accounts/bmi_form.html')