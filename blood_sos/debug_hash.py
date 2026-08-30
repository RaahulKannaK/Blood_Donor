import os
import django

# Tell Django where settings.py is
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blood_sos.settings")

# Start Django
django.setup()

from django.contrib.auth.hashers import check_password


password_hash = input("Enter Django password hash: ")
password = input("Enter password to check: ")

if check_password(password, password_hash):
    print("\n✅ PASSWORD MATCHES")
else:
    print("\n❌ PASSWORD DOES NOT MATCH")