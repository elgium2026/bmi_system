from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    SEX_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )

    PERSONNEL_TYPE_CHOICES = (
        ('PCO', 'Police Commissioned Officer (PCO)'),
        ('PNCO', 'Police Non-Commissioned Officer (PNCO)'),
        ('NUP', 'Non-Uniformed Personnel (NUP)'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    birthdate = models.DateField()
    sex = models.CharField(max_length=10, choices=SEX_CHOICES)
    rank = models.CharField(max_length=100)
    unit = models.CharField(max_length=150)
    personnel_type = models.CharField(max_length=10, choices=PERSONNEL_TYPE_CHOICES)

    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            first_name=instance.first_name or '',
            last_name=instance.last_name or '',
            birthdate=timezone.now().date(),
            sex='Male',
            rank='N/A',
            unit='N/A',
            personnel_type='PNCO'
        )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


class BMIRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)

    weight = models.FloatField()
    height = models.FloatField()

    waist = models.FloatField(blank=True, null=True)
    hip = models.FloatField(blank=True, null=True)
    wrist = models.FloatField(blank=True, null=True)

    bmi = models.FloatField()

    pnp_class = models.CharField(max_length=50)
    who_class = models.CharField(max_length=50)

    weight_to_lose = models.CharField(max_length=50)
    maximum_normal_weight = models.FloatField()

    date_computed = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.bmi}"


class LoginAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user} - {self.status} - {self.timestamp}"