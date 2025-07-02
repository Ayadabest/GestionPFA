#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pfa_management.settings')
django.setup()

from users.models import User

def show_students():
    """Afficher la liste complète des étudiants"""
    
    students = User.objects.filter(role='student').order_by('username')
    
    print("📋 LISTE COMPLÈTE DES ÉTUDIANTS :")
    print("=" * 60)
    print(f"Total: {students.count()} étudiants")
    print()
    
    for i, student in enumerate(students, 1):
        print(f"{i:2d}. 👤 {student.username} / password123")
        print(f"    📧 {student.email}")
        print(f"    👨‍🎓 {student.first_name} {student.last_name}")
        print()
    
    print("🎯 INSTRUCTIONS DE CONNEXION :")
    print("=" * 40)
    print("1. Allez sur http://127.0.0.1:8000/login/")
    print("2. Utilisez n'importe quel identifiant ci-dessus")
    print("3. Mot de passe: password123")
    print("4. Testez l'envoi de messages !")

if __name__ == '__main__':
    show_students() 