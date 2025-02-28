import os
import django
import sys
import subprocess

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from django.contrib.auth import get_user_model


def run_command(command):
    """Run shell commands and handle errors"""
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")


def install_requirements():
    """Install dependencies"""
    print("\n📦 Installing dependencies...\n")
    run_command("pip install -r requirements.txt")


def apply_migrations():
    """Run makemigrations and migrate"""
    print("\n🔄 Applying migrations...\n")
    run_command("python manage.py makemigrations")
    run_command("python manage.py migrate")


def create_superuser():
    """Create a superuser if it doesn’t exist"""
    print("\n👤 Creating superuser...\n")
    User = get_user_model()
    if not User.objects.filter(email="admin@yopmail.com").exists():
        User.objects.create_superuser(email="admin@yopmail.com", password="admin")
        print("✅ Superuser created successfully!")
    else:
        print("⚠️ Superuser already exists!")


if __name__ == "__main__":
    install_requirements()
    apply_migrations()
    create_superuser()
    print("\n🚀 Setup completed successfully!\n")
