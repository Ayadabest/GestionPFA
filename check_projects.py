import os
import django
import sys

# Configurer l'environnement Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pfa_management.settings')
django.setup()

from pfa_projects.models import Project

def check_projects():
    print("\n=== État des projets dans la base de données ===\n")
    
    # Compter le nombre total de projets
    total_projects = Project.objects.count()
    print(f"Nombre total de projets : {total_projects}")
    
    # Compter les projets par statut
    for status, _ in Project.STATUS_CHOICES:
        count = Project.objects.filter(status=status).count()
        print(f"\nProjets {status} : {count}")
        if count > 0:
            print("Liste :")
            for project in Project.objects.filter(status=status):
                print(f"- {project.title} (Superviseur: {project.supervisor.get_full_name()})")
    
    # Vérifier les projets disponibles
    available_projects = Project.objects.filter(status='available')
    if available_projects.exists():
        print("\nDétails des projets disponibles :")
        for project in available_projects:
            print(f"\nTitre : {project.title}")
            print(f"Superviseur : {project.supervisor.get_full_name()}")
            print(f"Description : {project.description[:100]}...")
    else:
        print("\nAucun projet disponible !")

if __name__ == '__main__':
    check_projects() 