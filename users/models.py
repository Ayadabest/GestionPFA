from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Étudiant'),
        ('teacher', 'Professeur'),
        ('admin', 'Administrateur'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    cne = models.CharField(max_length=20, blank=True, help_text="Code National de l'Étudiant")
    matricule = models.CharField(max_length=20, blank=True, help_text="Matricule du professeur")
    department = models.CharField(max_length=100, default='Informatique')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    skills = models.TextField(blank=True, help_text="Compétences séparées par des virgules")
    availability = models.CharField(max_length=100, blank=True, help_text="Disponibilité pour les réunions")
    
    class Meta:
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    def is_student(self):
        return self.role == 'student'

    def is_teacher(self):
        return self.role == 'teacher'

    def is_admin_user(self):
        return self.role == 'admin'

    def get_profile_data(self):
        data = {
            'full_name': self.get_full_name(),
            'email': self.email,
            'role': self.get_role_display(),
            'department': self.department,
            'profile_picture': self.profile_picture.url if self.profile_picture else None,
            'skills': self.skills,
            'availability': self.availability
        }
        if self.is_student():
            data['cne'] = self.cne
        elif self.is_teacher():
            data['matricule'] = self.matricule
        return data
class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    supervisor = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={'role': 'teacher'},  # Seuls les professeurs peuvent être superviseurs
        related_name='supervised_teams'
    )
    members = models.ManyToManyField(
        User, 
        related_name='teams',
        limit_choices_to={'role': 'student'}  # Seuls les étudiants peuvent être membres
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
        
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=10, unique=True)
    department = models.CharField(max_length=50)
    level = models.CharField(max_length=20)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.student_id}"
