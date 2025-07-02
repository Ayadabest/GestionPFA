from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import StudentProfile
from pfa_teams.models import Team
from pfa_projects.models import Project
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # Nettoyage des données existantes
        self.stdout.write('Suppression des données existantes...')
        Team.objects.all().delete()
        Project.objects.all().delete()
        StudentProfile.objects.all().delete()
        User.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Données existantes supprimées avec succès'))

        # Création de l'administrateur
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@pfa.com',
            password='admin123',
            role='admin'
        )
        self.stdout.write(self.style.SUCCESS('Admin créé avec succès'))

        # Création des professeurs
        professors = [
            {
                'username': 'prof1',
                'email': 'prof1@pfa.com',
                'password': 'prof123',
                'first_name': 'Ahmed',
                'last_name': 'El Idrissi',
                'skills': 'Intelligence Artificielle, Machine Learning',
            },
            {
                'username': 'prof2',
                'email': 'prof2@pfa.com',
                'password': 'prof123',
                'first_name': 'Youssef',
                'last_name': 'El Mansouri',
                'skills': 'Web Development, Cloud Computing',
            }
        ]

        for prof_data in professors:
            prof = User.objects.create_user(
                username=prof_data['username'],
                email=prof_data['email'],
                password=prof_data['password'],
                first_name=prof_data['first_name'],
                last_name=prof_data['last_name'],
                role='teacher',
                skills=prof_data['skills']
            )
            self.stdout.write(self.style.SUCCESS(f'Professeur {prof.username} créé avec succès'))

        # Création des étudiants
        students = [
            {
                'username': 'etud1',
                'email': 'etud1@pfa.com',
                'password': 'etud123',
                'first_name': 'Aya',
                'last_name': 'Elouajjite',
                'department': 'Informatique',
                'level': 'Master 2',
                'skills': 'Python, Java, Web'
            },
            {
                'username': 'etud2',
                'email': 'etud2@pfa.com',
                'password': 'etud123',
                'first_name': 'Anas',
                'last_name': 'Atmani',
                'department': 'Informatique',
                'level': 'Master 2',
                'skills': 'JavaScript, React, Node.js'
            },
            {
                'username': 'etud3',
                'email': 'etud3@pfa.com',
                'password': 'etud123',
                'first_name': 'Yassine',
                'last_name': 'Bensouda',
                'department': 'Informatique',
                'level': 'Master 2',
                'skills': 'DevOps, Docker, AWS'
            },
            {
                'username': 'etud4',
                'email': 'etud4@pfa.com',
                'password': 'etud123',
                'first_name': 'Fatima',
                'last_name': 'Tazi',
                'department': 'Informatique',
                'level': 'Master 2',
                'skills': 'Data Science, Python, R'
            }
        ]

        created_students = []
        for student_data in students:
            student = User.objects.create_user(
                username=student_data['username'],
                email=student_data['email'],
                password=student_data['password'],
                first_name=student_data['first_name'],
                last_name=student_data['last_name'],
                role='student',
                skills=student_data['skills']
            )
            
            profile = StudentProfile.objects.create(
                user=student,
                student_id=f"STU{len(created_students)+1:03d}",
                department=student_data['department'],
                level=student_data['level']
            )
            created_students.append(student)
            self.stdout.write(self.style.SUCCESS(f'Étudiant {student.username} créé avec succès'))

        # Création des projets
        projects = [
            {
                'title': 'Système de Gestion des PFA',
                'description': 'Développement d\'une plateforme web pour la gestion des projets de fin d\'année',
                'requirements': 'Django, Python, JavaScript, Bootstrap',
                'supervisor': User.objects.get(username='prof1'),
                'status': 'available',
                'deadline': timezone.now().date() + timedelta(days=90)
            },
            {
                'title': 'Application de Covoiturage',
                'description': 'Développement d\'une application mobile de covoiturage pour les étudiants',
                'requirements': 'React Native, Node.js, MongoDB',
                'supervisor': User.objects.get(username='prof2'),
                'status': 'available',
                'deadline': timezone.now().date() + timedelta(days=90)
            },
            {
                'title': 'Système de Reconnaissance Faciale',
                'description': 'Développement d\'un système de reconnaissance faciale pour le contrôle d\'accès',
                'requirements': 'Python, OpenCV, TensorFlow',
                'supervisor': User.objects.get(username='prof1'),
                'status': 'available',
                'deadline': timezone.now().date() + timedelta(days=90)
            }
        ]

        for project_data in projects:
            project = Project.objects.create(**project_data)
            self.stdout.write(self.style.SUCCESS(f'Projet {project.title} créé avec succès'))

        # Création des équipes
        teams = [
            {
                'name': 'Team Alpha',
                'project': Project.objects.get(title='Système de Gestion des PFA'),
                'members': [created_students[0], created_students[1]],
                'status': 'pending'
            },
            {
                'name': 'Team Beta',
                'project': Project.objects.get(title='Application de Covoiturage'),
                'members': [created_students[2], created_students[3]],
                'status': 'pending'
            }
        ]

        for team_data in teams:
            team = Team.objects.create(
                name=team_data['name'],
                project=team_data['project'],
                status=team_data['status']
            )
            team.members.set(team_data['members'])
            self.stdout.write(self.style.SUCCESS(f'Équipe {team.name} créée avec succès')) 