import os
import django
import sys

# Configurer l'environnement Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pfa_management.settings')
django.setup()

from pfa_projects.models import Project
from pfa_teams.models import Team

def reset_project_status():
    print("\n=== Réinitialisation du statut des projets ===\n")
    
    # Récupérer tous les projets
    projects = Project.objects.all()
    
    for project in projects:
        # Vérifier si le projet est réellement attribué à une équipe
        team_exists = Team.objects.filter(project=project).exists()
        
        if not team_exists and project.status != 'available':
            old_status = project.status
            project.status = 'available'
            project.save()
            print(f"Projet '{project.title}' réinitialisé : {old_status} -> available")
        else:
            print(f"Projet '{project.title}' - Statut inchangé : {project.status}")
    
    print("\nStatut final des projets :")
    for status, _ in Project.STATUS_CHOICES:
        count = Project.objects.filter(status=status).count()
        print(f"- {status}: {count} projets")

if __name__ == '__main__':
    reset_project_status() 