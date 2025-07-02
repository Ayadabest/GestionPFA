import os
import django
import sys

# Configurer l'environnement Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pfa_management.settings')
django.setup()

from users.models import User
from django.db import transaction

def update_student_emails():
    with transaction.atomic():
        # Mettre à jour les emails des étudiants
        students = User.objects.filter(role='student')
        
        for student in students:
            # Créer un email professionnel basé sur le nom et prénom
            first_name = student.first_name.lower()
            last_name = student.last_name.lower().replace(' ', '')
            
            # Gérer les caractères spéciaux dans les noms
            special_chars = {
                'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
                'à': 'a', 'â': 'a', 'ä': 'a',
                'î': 'i', 'ï': 'i',
                'ô': 'o', 'ö': 'o',
                'ù': 'u', 'û': 'u', 'ü': 'u',
                'ç': 'c'
            }
            
            for char, replacement in special_chars.items():
                first_name = first_name.replace(char, replacement)
                last_name = last_name.replace(char, replacement)
            
            # Créer l'email
            email = f"{first_name}.{last_name}@student.emsi.ma"
            
            # Mettre à jour l'email de l'étudiant
            old_email = student.email
            student.email = email
            student.save()
            
            print(f"Email mis à jour pour {student.get_full_name()}:")
            print(f"  Ancien: {old_email}")
            print(f"  Nouveau: {email}")
            print("-" * 50)

if __name__ == '__main__':
    print("Mise à jour des emails des étudiants...")
    update_student_emails()
    print("Emails mis à jour avec succès !") 