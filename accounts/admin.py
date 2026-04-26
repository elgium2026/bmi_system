from django.contrib import admin
from datetime import date
from .models import Profile, BMIRecord, LoginAttempt


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'full_name',
        'rank',
        'unit',
        'personnel_type',
        'birthdate',
        'age',
        'sex',
    )

    def full_name(self, obj):
        return f"{obj.last_name}, {obj.first_name} {obj.middle_name or ''}"

    def age(self, obj):
        today = date.today()
        return today.year - obj.birthdate.year - (
            (today.month, today.day) < (obj.birthdate.month, obj.birthdate.day)
        )


@admin.register(BMIRecord)
class BMIRecordAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'full_name',
        'unit',
        'rank',
        'age',
        'sex',
        'weight',
        'height',
        'waist',
        'hip',
        'wrist',
        'bmi',
        'pnp_class',
        'who_class',
        'weight_to_lose',
        'maximum_normal_weight',
        'date_computed',
    )

    def full_name(self, obj):
        return f"{obj.profile.last_name}, {obj.profile.first_name}"

    def unit(self, obj):
        return obj.profile.unit

    def rank(self, obj):
        return obj.profile.rank

    def sex(self, obj):
        return obj.profile.sex

    def age(self, obj):
        today = date.today()
        b = obj.profile.birthdate
        return today.year - b.year - ((today.month, today.day) < (b.month, b.day))


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'timestamp')