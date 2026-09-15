from django.db import models


# =========================================================
# LOGIN USER
# =========================================================

class LoginUser(models.Model):

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('donor', 'Donor'),
        ('needer', 'Needer'),
    ]

    name = models.CharField(max_length=100)

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

    # Admin verification / blocking
    is_verified = models.BooleanField(
        default=False
    )

    is_blocked = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.name} - {self.role}"


# =========================================================
# DONOR PROFILE
# =========================================================

class DonorProfile(models.Model):

    user = models.OneToOneField(
        LoginUser,
        on_delete=models.CASCADE
    )

    blood_group = models.CharField(
        max_length=5,
        blank=True
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


# =========================================================
# HOSPITAL
# =========================================================

class Hospital(models.Model):

    name = models.CharField(
        max_length=150
    )

    location = models.CharField(
        max_length=100
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    is_verified = models.BooleanField(
        default=False
    )

    is_blocked = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.name} - {self.location}"


# =========================================================
# BLOOD REQUEST
# =========================================================

class BloodRequest(models.Model):

    URGENCY_CHOICES = [
        ('Emergency', 'Emergency'),
        ('Urgent', 'Urgent'),
        ('Normal', 'Normal'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Fulfilled', 'Fulfilled'),
        ('Cancelled', 'Cancelled'),
    ]

    STAGE_CHOICES = [
        ('Stage 1', 'Stage 1'),
        ('Stage 2', 'Stage 2'),
        ('Stage 3', 'Stage 3'),
        ('Admin Escalation', 'Admin Escalation'),
        ('Completed', 'Completed'),
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

    # Units already received
    received_units = models.PositiveIntegerField(
        default=0
    )

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
        choices=STATUS_CHOICES,
        default='Active'
    )

    # SOS escalation
    current_stage = models.CharField(
        max_length=30,
        choices=STAGE_CHOICES,
        default='Stage 1'
    )

    progress = models.PositiveIntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def update_progress(self):

        if self.units > 0:

            self.progress = int(
                (self.received_units / self.units) * 100
            )

        else:

            self.progress = 0

        if self.progress >= 100:

            self.progress = 100
            self.status = 'Fulfilled'
            self.current_stage = 'Completed'

        elif self.received_units >= 1:

            self.current_stage = 'Stage 1'

        else:

            self.current_stage = 'Stage 1'

        self.save()

    def __str__(self):
        return (
            f"{self.blood_group} request "
            f"by {self.needer.name}"
        )


# =========================================================
# DONOR RESPONSE
# =========================================================

class DonorResponse(models.Model):

    STATUS_CHOICES = [
        ('Responded', 'Responded'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

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
        choices=STATUS_CHOICES,
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


# =========================================================
# DONATION HISTORY
# =========================================================

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