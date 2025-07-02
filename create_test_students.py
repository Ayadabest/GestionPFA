#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pfa_management.settings')
django.setup()

from users.models import User, StudentProfile
from django.contrib.auth.hashers import make_password

def create_test_students():
    """Créer des comptes étudiants de test"""
    
    # Liste des étudiants de test
    test_students = [
        {
            'username': 'student1',
            'email': 'student1@emi.ac.ma',
            'first_name': 'Ahmed',
            'last_name': 'Benali',
            'password': 'password123',
            'department': 'Informatique',
            'level': 'Master 2'
        },
        {
            'username': 'student2',
            'email': 'student2@emi.ac.ma',
            'first_name': 'Fatima',
            'last_name': 'Alaoui',
            'password': 'password123',
            'department': 'Informatique',
            'level': 'Master 2'
        },
        {
            'username': 'student3',
            'email': 'student3@emi.ac.ma',
            'first_name': 'Karim',
            'last_name': 'Tazi',
            'password': 'password123',
            'department': 'Informatique',
            'level': 'Master 2'
        },
        {
            'username': 'student4',
            'email': 'student4@emi.ac.ma',
            'first_name': 'Amina',
            'last_name': 'Bouazza',
            'password': 'password123',
            'department': 'Informatique',
            'level': 'Master 2'
        },
        {
            'username': 'student5',
            'email': 'student5@emi.ac.ma',
            'first_name': 'Youssef',
            'last_name': 'Mansouri',
            'password': 'password123',
            'department': 'Informatique',
            'level': 'Master 2'
        }
    ]
    
    created_count = 0
    
    for student_data in test_students:
        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(username=student_data['username']).exists():
            print(f"L'étudiant {student_data['username']} existe déjà.")
            continue
        
        # Créer l'utilisateur
        user = User.objects.create(
            username=student_data['username'],
            email=student_data['email'],
            first_name=student_data['first_name'],
            last_name=student_data['last_name'],
            password=make_password(student_data['password']),
            role='student',
            is_active=True
        )
        
        # Créer le profil étudiant
        StudentProfile.objects.create(
            user=user,
            student_id=f"STU{user.id:03d}",
            department=student_data['department'],
            level=student_data['level']
        )
        
        print(f"✅ Étudiant créé : {student_data['username']} / {student_data['password']}")
        created_count += 1
    
    print(f"\n🎉 {created_count} étudiants de test ont été créés avec succès !")
    print("\n📋 Identifiants de connexion :")
    print("=" * 50)
    for student_data in test_students:
        print(f"👤 {student_data['username']} / {student_data['password']}")
        print(f"   📧 {student_data['email']}")
        print(f"   👨‍🎓 {student_data['first_name']} {student_data['last_name']}")
        print()

if __name__ == '__main__':
    create_test_students() 