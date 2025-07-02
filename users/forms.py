from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, StudentProfile

class StudentRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'cne', 'department', 'password1', 'password2']
        labels = {
            'username': "Nom d'utilisateur",
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'Email',
            'cne': 'CNE',
            'department': 'Département'
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        if commit:
            user.save()
            # Create student profile
            StudentProfile.objects.create(
                user=user,
                student_id=f"STU{user.id:03d}",
                department=user.department
            )
        return user

class TeacherRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'matricule', 'department', 'password1', 'password2']
        labels = {
            'username': "Nom d'utilisateur",
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'Email',
            'matricule': 'Matricule',
            'department': 'Département'
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'teacher'
        if commit:
            user.save()
        return user

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['student_id', 'department', 'level']
        labels = {
            'student_id': 'ID Étudiant',
            'department': 'Département',
            'level': 'Niveau'
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'department']
        labels = {
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'Email',
            'department': 'Département'
        } 