from django.db import models


class LoginUser(models.Model):

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('donor', 'Donor'),
        ('needer', 'Needer'),
    ]

    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.name} - {self.role}"


class DonorProfile(models.Model):
    user = models.OneToOneField(LoginUser, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=5)
    location = models.CharField(max_length=100)
    distance_km = models.FloatField(default=0)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.name} - {self.blood_group}"


class BloodRequest(models.Model):
    URGENCY_CHOICES = [
        ('Emergency', 'Emergency'),
        ('Urgent', 'Urgent'),
        ('Normal', 'Normal'),
    ]

    needer = models.ForeignKey(LoginUser, on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=100)
    patient_age = models.PositiveIntegerField()
    blood_group = models.CharField(max_length=5)
    units = models.PositiveIntegerField()
    hospital = models.CharField(max_length=150)
    location = models.CharField(max_length=100)
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES)
    additional_info = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.blood_group} request by {self.needer.name}"