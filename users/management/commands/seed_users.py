from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import StudentProfile
from pfa_projects.models import Project
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with initial users and projects'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding users...')

        # Create admin user
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Administrateur',
            last_name='Système',
            role='admin',
            department='Administration'
        )
        self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin.username}'))

        # Create teachers
        teachers_data = [
            {
                'username': 'prof1',
                'password': 'prof123',
                'email': 'prof1@example.com',
                'first_name': 'Mohammed',
                'last_name': 'El Alaoui',
                'matricule': 'TCH001',
                'department': 'Informatique',
                'role': 'teacher',
                'skills': 'Intelligence Artificielle, Big Data, Python',
                'availability': 'Lundi-Vendredi, 14h-18h'
            },
            {
                'username': 'prof2',
                'password': 'prof123',
                'email': 'prof2@example.com',
                'first_name': 'Fatima',
                'last_name': 'Bennis',
                'matricule': 'TCH002',
                'department': 'Informatique',
                'role': 'teacher',
                'skills': 'Développement Web, Cloud Computing, DevOps',
                'availability': 'Lundi-Jeudi, 9h-12h'
            },
            {
                'username': 'prof3',
                'password': 'prof123',
                'email': 'prof3@example.com',
                'first_name': 'Ahmed',
                'last_name': 'Tazi',
                'matricule': 'TCH003',
                'department': 'Informatique',
                'role': 'teacher',
                'skills': 'Sécurité Informatique, Réseaux, Java',
                'availability': 'Mardi-Vendredi, 10h-16h'
            }
        ]

        teachers = []
        for teacher_data in teachers_data:
            teacher = User.objects.create_user(**teacher_data)
            teachers.append(teacher)
            self.stdout.write(self.style.SUCCESS(f'Created teacher: {teacher.username}'))

        # Create students
        students_data = [
            {
                'username': 'student1',
                'password': 'student123',
                'email': 'student1@example.com',
                'first_name': 'Youssef',
                'last_name': 'El Amrani',
                'cne': 'STU001',
                'department': 'Informatique',
                'role': 'student',
                'skills': 'Python, JavaScript, React',
                'availability': 'Flexible'
            },
            {
                'username': 'student2',
                'password': 'student123',
                'email': 'student2@example.com',
                'first_name': 'Meryem',
                'last_name': 'Idrissi',
                'cne': 'STU002',
                'department': 'Informatique',
                'role': 'student',
                'skills': 'Java, Spring Boot, Angular',
                'availability': 'Après-midi'
            },
            {
                'username': 'student3',
                'password': 'student123',
                'email': 'student3@example.com',
                'first_name': 'Omar',
                'last_name': 'Benjelloun',
                'cne': 'STU003',
                'department': 'Informatique',
                'role': 'student',
                'skills': 'DevOps, Docker, AWS',
                'availability': 'Matin'
            },
            {
                'username': 'student4',
                'password': 'student123',
                'email': 'student4@example.com',
                'first_name': 'Safae',
                'last_name': 'Fassi',
                'cne': 'STU004',
                'department': 'Informatique',
                'role': 'student',
                'skills': 'Data Science, Machine Learning',
                'availability': 'Week-end'
            },
            {
                'username': 'student5',
                'password': 'student123',
                'email': 'student5@example.com',
                'first_name': 'Karim',
                'last_name': 'Bennani',
                'cne': 'STU005',
                'department': 'Informatique',
                'role': 'student',
                'skills': 'Mobile Dev, Flutter, Firebase',
                'availability': 'Soir'
            }
        ]

        for student_data in students_data:
            student = User.objects.create_user(**student_data)
            StudentProfile.objects.create(
                user=student,
                student_id=f"STU{student.id:03d}",
                department=student.department,
                level='Master 2'
            )
            self.stdout.write(self.style.SUCCESS(f'Created student: {student.username}'))

        # Create projects
        projects_data = [
            {
                'title': 'Système de Gestion de Bibliothèque Numérique',
                'description': 'Développement d\'un système de gestion de bibliothèque numérique avec interface utilisateur avancée et base de données',
                'requirements': 'Python, Django, React',
                'supervisor': teachers[0],
                'max_students': 2,
                'status': 'available'
            },
            {
                'title': 'Application d\'IA pour la Prévision Météorologique',
                'description': 'Développement d\'un modèle de prévision météorologique utilisant des techniques d\'apprentissage automatique',
                'requirements': 'Python, TensorFlow, Data Analysis',
                'supervisor': teachers[1],
                'max_students': 2,
                'status': 'available'
            },
            {
                'title': 'Plateforme d\'Apprentissage en Ligne',
                'description': 'Développement d\'une plateforme éducative interactive avec support pour les cours en direct et les examens',
                'requirements': 'Django, Vue.js, WebRTC',
                'supervisor': teachers[2],
                'max_students': 3,
                'status': 'available'
            },
            {
                'title': 'Système de Gestion des Projets Étudiants',
                'description': 'Développement d\'un système pour gérer et suivre les projets étudiants avec tableau de bord pour les professeurs',
                'requirements': 'Laravel, MySQL, Bootstrap',
                'supervisor': teachers[0],
                'max_students': 2,
                'status': 'available'
            },
            {
                'title': 'Application de Chat Intelligent',
                'description': 'Développement d\'un chatbot intelligent utilisant le traitement du langage naturel',
                'requirements': 'Python, NLTK, Machine Learning',
                'supervisor': teachers[1],
                'max_students': 2,
                'status': 'available'
            }
        ]

        for project_data in projects_data:
            project = Project.objects.create(
                title=project_data['title'],
                description=project_data['description'],
                requirements=project_data['requirements'],
                supervisor=project_data['supervisor'],
                max_students=project_data['max_students'],
                status=project_data['status'],
                created_at=timezone.now()
            )
            self.stdout.write(self.style.SUCCESS(f'Created project: {project.title}')) 