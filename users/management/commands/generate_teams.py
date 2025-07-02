from django.core.management.base import BaseCommand
from users.models import User
from pfa_teams.models import Team, TeamRequest
from pfa_projects.models import Project
from django.db import transaction
import random

class Command(BaseCommand):
    help = 'Génère des équipes avec les étudiants existants'

    def handle(self, *args, **kwargs):
        try:
            with transaction.atomic():
                # Récupérer tous les étudiants
                students = list(User.objects.filter(role='student'))
                
                if not students:
                    self.stdout.write(self.style.ERROR('Aucun étudiant trouvé. Veuillez d\'abord créer des étudiants.'))
                    return

                # Créer quelques projets si nécessaire
                projects_data = [
                    {
                        'title': 'Système de Gestion de Bibliothèque',
                        'description': 'Développement d\'un système complet de gestion de bibliothèque avec suivi des emprunts.',
                        'requirements': 'Python, Django, Base de données',
                    },
                    {
                        'title': 'Application Mobile de Covoiturage',
                        'description': 'Création d\'une application mobile pour faciliter le covoiturage entre étudiants.',
                        'requirements': 'React Native, Node.js, MongoDB',
                    },
                    {
                        'title': 'Plateforme E-learning',
                        'description': 'Développement d\'une plateforme d\'apprentissage en ligne avec des fonctionnalités interactives.',
                        'requirements': 'Vue.js, Django REST, PostgreSQL',
                    },
                    {
                        'title': 'Système de Reconnaissance Faciale',
                        'description': 'Implémentation d\'un système de reconnaissance faciale pour le contrôle d\'accès.',
                        'requirements': 'Python, OpenCV, TensorFlow',
                    }
                ]

                # Créer un professeur si nécessaire
                teacher, created = User.objects.get_or_create(
                    username='prof.ahmed',
                    defaults={
                        'first_name': 'Ahmed',
                        'last_name': 'Bennani',
                        'email': 'prof.ahmed@emi.ac.ma',
                        'role': 'teacher'
                    }
                )
                if created:
                    teacher.set_password('password123')
                    teacher.save()
                    self.stdout.write(self.style.SUCCESS(f'Professeur créé : {teacher.get_full_name()}'))

                # Créer les projets
                projects = []
                for project_data in projects_data:
                    project, created = Project.objects.get_or_create(
                        title=project_data['title'],
                        defaults={
                            'description': project_data['description'],
                            'requirements': project_data['requirements'],
                            'supervisor': teacher,
                            'status': 'available'
                        }
                    )
                    projects.append(project)
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Projet créé : {project.title}'))

                # Créer des équipes
                random.shuffle(students)
                teams_created = 0
                
                # Créer des équipes de 2 étudiants
                for i in range(0, len(students) - 1, 2):
                    student1 = students[i]
                    student2 = students[i + 1]
                    
                    # Vérifier si les étudiants ne sont pas déjà dans une équipe
                    if not Team.objects.filter(members=student1).exists() and not Team.objects.filter(members=student2).exists():
                        # Choisir un projet aléatoire
                        project = random.choice(projects)
                        
                        # Créer l'équipe
                        team_name = f"Team_{student1.username}_{student2.username}"
                        team = Team.objects.create(
                            name=team_name,
                            project=project,
                            status=random.choice(['pending', 'approved'])
                        )
                        team.members.add(student1, student2)
                        
                        # Créer une demande de binôme
                        TeamRequest.objects.create(
                            sender=student1,
                            receiver=student2,
                            project=project,
                            status='accepted',
                            message=f"Demande de formation d'équipe pour le projet {project.title}"
                        )
                        
                        teams_created += 1
                        self.stdout.write(self.style.SUCCESS(
                            f'Équipe créée : {team_name} - Membres : {student1.get_full_name()} et {student2.get_full_name()}'
                        ))

                # Afficher le résumé
                self.stdout.write('\n=== RÉSUMÉ ===')
                self.stdout.write(f'Équipes créées : {teams_created}')
                self.stdout.write(f'Projets disponibles : {len(projects)}')
                self.stdout.write(f'Étudiants sans équipe : {len(students) - teams_created * 2}')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur lors de la création des équipes : {str(e)}')) 