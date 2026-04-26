from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from datetime import date, datetime
import openpyxl

from .models import Profile, BMIRecord


# ================= REGISTER ================= #
def register(request):
    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')

        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        last_name = request.POST.get('last_name')
        birthdate = request.POST.get('birthdate')
        sex = request.POST.get('sex')
        rank = request.POST.get('rank')
        unit = request.POST.get('unit')
        personnel_type = request.POST.get('personnel_type')

        # ===== FORCE UPPERCASE FOR PCO =====
        if personnel_type == "PCO":
            if first_name:
                first_name = first_name.upper()
            if middle_name:
                middle_name = middle_name.upper()
            if last_name:
                last_name = last_name.upper()

        # ===== VALIDATION =====
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        # ===== CREATE USER =====
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )

        # ===== UPDATE PROFILE =====
        profile = user.profile
        profile.first_name = first_name
        profile.middle_name = middle_name
        profile.last_name = last_name
        profile.birthdate = datetime.strptime(birthdate, "%Y-%m-%d").date()
        profile.sex = sex
        profile.rank = rank
        profile.unit = unit
        profile.personnel_type = personnel_type
        profile.save()

        messages.success(request, "Account created successfully")
        return redirect('login')

    return render(request, 'accounts/signup.html')


# ================= LOGIN ================= #
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('bmi')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'accounts/login.html')


# ================= LOGOUT ================= #
def logout_view(request):
    logout(request)
    return redirect('login')


# ================= BMI ================= #
@login_required
def bmi_view(request):

    if request.method == 'POST':
        weight = float(request.POST.get('weight'))
        height_cm = float(request.POST.get('height'))
        waist = float(request.POST.get('waist') or 0)
        hip = float(request.POST.get('hip') or 0)
        wrist = float(request.POST.get('wrist') or 0)

        height_m = height_cm / 100
        profile = request.user.profile

        # AGE
        today = date.today()
        age = today.year - profile.birthdate.year - (
            (today.month, today.day) < (profile.birthdate.month, profile.birthdate.day)
        )

        # BMI
        bmi = round(weight / (height_m ** 2), 1)

        # WHO
        if bmi < 18.5:
            who = "UNDERWEIGHT"
        elif bmi < 25:
            who = "NORMAL"
        elif bmi < 30:
            who = "OVERWEIGHT"
        elif bmi < 35:
            who = "OBESE CLASS 1"
        elif bmi < 40:
            who = "OBESE CLASS 2"
        else:
            who = "OBESE CLASS 3"

        # PNP
        if bmi <= 18.5:
            pnp = "UNDERWEIGHT"
        elif bmi <= 24.9:
            pnp = "NORMAL"
        elif bmi <= 26:
            pnp = "ACCEPTABLE BMI"
        elif bmi <= 29.9:
            pnp = "OVERWEIGHT"
        elif bmi <= 34.9:
            pnp = "OBESE CLASS 1"
        elif bmi <= 39.9:
            pnp = "OBESE CLASS 2"
        else:
            pnp = "OBESE CLASS 3"

        # AGE-BASED MAX BMI
        if age < 30:
            max_bmi = 24.9
        elif age <= 34:
            max_bmi = 25
        elif age <= 39:
            max_bmi = 25.5
        elif age <= 44:
            max_bmi = 26
        elif age <= 50:
            max_bmi = 26.5
        else:
            max_bmi = 27

        max_weight = round((height_m ** 2) * max_bmi, 1)
        weight_to_lose_val = round(weight - max_weight, 1)

        if weight_to_lose_val < 0:
            weight_to_lose_val = 0.0

        # SAVE
        BMIRecord.objects.create(
            user=request.user,
            profile=profile,
            weight=weight,
            height=height_cm,
            waist=waist,
            hip=hip,
            wrist=wrist,
            bmi=bmi,
            pnp_class=pnp,
            who_class=who,
            weight_to_lose=str(weight_to_lose_val),
            maximum_normal_weight=max_weight
        )

        return render(request, 'accounts/bmi_result.html', {
            'age': age,
            'bmi': bmi,
            'who_class': who,
            'pnp_class': pnp,
            'weight_to_lose': f"{weight_to_lose_val} kg",
            'max_weight': f"{max_weight} kg",
        })

    return render(request, 'accounts/bmi_form.html')


# ================= EXPORT EXCEL ================= #
@login_required
def export_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "BMI Report"

    headers = [
        "UNIT", "RANK", "LAST NAME", "FIRST NAME", "MIDDLE NAME",
        "QLFR", "BIRTHDATE", "AGE", "SEX",
        "WEIGHT (kg)", "HEIGHT (cm)", "WAIST (cm)", "HIP (cm)", "WRIST (cm)",
        "BMI",
        "PNP BMI ACCEPTABLE STANDARD",
        "WHO STANDARD (WHO Classification)",
        "Weight to Lose (Kg)",
        "Normal Weight (Kg)",
        "REMARKS"
    ]

    ws.append(headers)

    records = BMIRecord.objects.select_related('profile').all()
    today = date.today()

    for r in records:
        p = r.profile

        age = today.year - p.birthdate.year - (
            (today.month, today.day) < (p.birthdate.month, p.birthdate.day)
        )

        ws.append([
            p.unit,
            p.rank,
            p.last_name,
            p.first_name,
            p.middle_name or "",
            "",
            p.birthdate.strftime("%Y-%m-%d"),
            age,
            p.sex,
            round(r.weight, 1),
            round(r.height, 1),
            round(r.waist or 0, 1),
            round(r.hip or 0, 1),
            round(r.wrist or 0, 1),
            round(r.bmi, 1),
            r.pnp_class,
            r.who_class,
            round(float(r.weight_to_lose), 1),
            round(r.maximum_normal_weight, 1),
            ""
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=bmi_report.xlsx'

    wb.save(response)
    return response