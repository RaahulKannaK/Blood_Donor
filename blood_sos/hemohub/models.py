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