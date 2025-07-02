#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pfa_management.settings')
django.setup()

from users.models import User

def show_teachers():
    """Afficher la liste des professeurs"""
    
    teachers = User.objects.filter(role='teacher').order_by('username')
    
    print("📋 LISTE DES PROFESSEURS :")
    print("=" * 50)
    print(f"Total: {teachers.count()} professeurs")
    print()
    
    for i, teacher in enumerate(teachers, 1):
        print(f"{i}. 👨‍🏫 {teacher.username} / password123")
        print(f"   📧 {teacher.email}")
        print(f"   👨‍🎓 {teacher.first_name} {teacher.last_name}")
        print()
    
    print("🎯 INSTRUCTIONS DE CONNEXION :")
    print("=" * 40)
    print("1. Allez sur http://127.0.0.1:8000/login/")
    print("2. Utilisez n'importe quel identifiant ci-dessus")
    print("3. Mot de passe: password123")
    print("4. Testez l'envoi de messages aux étudiants !")

if __name__ == '__main__':
    show_teachers() 