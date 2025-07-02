import os
import django
import sys

# Configurer l'environnement Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pfa_management.settings')
django.setup()

from pfa_projects.models import Project
from users.models import User

def create_test_project():
    try:
        # Récupérer un superviseur (professeur)
        supervisor = User.objects.filter(role='teacher').first()
        if not supervisor:
            print("Erreur : Aucun professeur trouvé dans la base de données")
            return
        
        # Créer un nouveau projet
        project = Project.objects.create(
            title="Projet Test - Application Mobile",
            description="Un projet de test pour vérifier la fonctionnalité de sélection de projet",
            supervisor=supervisor,
            status='available',
            requirements="Python, Django, React Native",
            max_students=2
        )
        
        print(f"\nProjet créé avec succès :")
        print(f"ID : {project.id}")
        print(f"Titre : {project.title}")
        print(f"Superviseur : {project.supervisor.get_full_name()}")
        print(f"Statut : {project.status}")
        
        # Vérifier tous les projets disponibles
        print("\nListe de tous les projets disponibles :")
        available_projects = Project.objects.filter(status='available')
        for p in available_projects:
            print(f"- {p.title} (ID: {p.id}, Superviseur: {p.supervisor.get_full_name()})")
            
    except Exception as e:
        print(f"Erreur lors de la création du projet : {str(e)}")

if __name__ == '__main__':
    create_test_project() 