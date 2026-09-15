
from django.db import models


# ---------------------------------------------------------
# LOGIN USER
# ---------------------------------------------------------

class LoginUser(models.Model):

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('donor', 'Donor'),
        ('needer', 'Needer'),
    ]

    name = models.CharField(
        max_length=100
    )

    age = models.PositiveIntegerField()

    username = models.CharField(
        max_length=100,
        unique=True
    )

    password = models.CharField(
        max_length=255
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    # -----------------------------------------------------
    # ADMIN USER MANAGEMENT
    # -----------------------------------------------------

    is_verified = models.BooleanField(
        default=False
    )

    is_blocked = models.BooleanField(
        default=False
    )

    def __str__(self):

        return f"{self.name} - {self.role}"


# ---------------------------------------------------------
# DONOR PROFILE
# ---------------------------------------------------------

class DonorProfile(models.Model):

    user = models.OneToOneField(
        LoginUser,
        on_delete=models.CASCADE
    )

    blood_group = models.CharField(
        max_length=5
    )

    location = models.CharField(
        max_length=100,
        blank=True
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    last_donation_date = models.DateField(
        null=True,
        blank=True
    )

    distance_km = models.FloatField(
        default=0
    )

    is_available = models.BooleanField(
        default=True
    )

    def __str__(self):

        return f"{self.user.name} - {self.blood_group}"


# ---------------------------------------------------------
# BLOOD REQUEST
# ---------------------------------------------------------

class BloodRequest(models.Model):

    URGENCY_CHOICES = [
        ('Emergency', 'Emergency'),
        ('Urgent', 'Urgent'),
        ('Normal', 'Normal'),
    ]

    needer = models.ForeignKey(
        LoginUser,
        on_delete=models.CASCADE
    )

    patient_name = models.CharField(
        max_length=100
    )

    patient_age = models.PositiveIntegerField()

    blood_group = models.CharField(
        max_length=5
    )

    units = models.PositiveIntegerField()

    hospital = models.CharField(
        max_length=150
    )

    location = models.CharField(
        max_length=100
    )

    urgency = models.CharField(
        max_length=20,
        choices=URGENCY_CHOICES
    )

    additional_info = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        default='Active'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.blood_group} request by {self.needer.name}"


# ---------------------------------------------------------
# SUSPICIOUS REQUEST
# ---------------------------------------------------------

class SuspiciousRequest(models.Model):

    blood_request = models.ForeignKey(
        BloodRequest,
        on_delete=models.CASCADE,
        related_name="suspicious_alerts"
    )

    title = models.CharField(
        max_length=150
    )

    description = models.TextField()

    severity = models.CharField(
        max_length=20,
        default="High"
    )

    is_reviewed = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.title} - {self.severity}"


# ---------------------------------------------------------
# DONOR RESPONSE
# ---------------------------------------------------------

class DonorResponse(models.Model):

    donor = models.ForeignKey(
        DonorProfile,
        on_delete=models.CASCADE
    )

    blood_request = models.ForeignKey(
        BloodRequest,
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=20,
        default='Responded'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.donor.user.name} - "
            f"{self.blood_request.blood_group}"
        )


# ---------------------------------------------------------
# DONATION HISTORY
# ---------------------------------------------------------

class DonationHistory(models.Model):

    donor = models.ForeignKey(
        DonorProfile,
        on_delete=models.CASCADE
    )

    blood_group = models.CharField(
        max_length=5
    )

    hospital = models.CharField(
        max_length=150
    )

    location = models.CharField(
        max_length=100
    )

    donation_date = models.DateField()

    status = models.CharField(
        max_length=20,
        default='Completed'
    )

    def __str__(self):

        return (
            f"{self.donor.user.name} - "
            f"{self.donation_date}"
        )


# ---------------------------------------------------------
# ADMIN ACTION LOG
# ---------------------------------------------------------

class AdminActionLog(models.Model):

    admin = models.ForeignKey(
        LoginUser,
        on_delete=models.CASCADE,
        related_name="admin_actions"
    )

    action = models.CharField(
        max_length=100
    )

    target_user = models.ForeignKey(
        LoginUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="admin_action_targets"
    )

    description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.admin.name} - "
            f"{self.action}"
        )

