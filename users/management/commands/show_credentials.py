from django.core.management.base import BaseCommand
from users.models import User
from django.contrib.auth.models import Group
from tabulate import tabulate

class Command(BaseCommand):
    help = 'Affiche les identifiants de tous les utilisateurs'

    def handle(self, *args, **kwargs):
        # Récupérer tous les utilisateurs par rôle
        students = User.objects.filter(role='student').select_related('studentprofile')
        teachers = User.objects.filter(role='teacher')
        admins = User.objects.filter(role='admin')

        # Afficher les étudiants
        self.stdout.write('\n' + self.style.SUCCESS('=== ÉTUDIANTS ==='))
        student_data = []
        for student in students:
            student_data.append([
                student.get_full_name(),
                student.username,
                'password123',
                student.email,
                student.studentprofile.department,
                student.studentprofile.level,
                student.studentprofile.phone or 'Non spécifié'
            ])
        
        if student_data:
            headers = ['Nom complet', 'Nom d\'utilisateur', 'Mot de passe', 'Email', 'Département', 'Niveau', 'Téléphone']
            self.stdout.write(tabulate(student_data, headers=headers, tablefmt='grid'))
        else:
            self.stdout.write(self.style.WARNING('Aucun étudiant trouvé'))

        # Afficher les professeurs
        self.stdout.write('\n' + self.style.SUCCESS('=== PROFESSEURS ==='))
        teacher_data = []
        for teacher in teachers:
            teacher_data.append([
                teacher.get_full_name(),
                teacher.username,
                'password123',
                teacher.email,
                teacher.department
            ])
        
        if teacher_data:
            headers = ['Nom complet', 'Nom d\'utilisateur', 'Mot de passe', 'Email', 'Département']
            self.stdout.write(tabulate(teacher_data, headers=headers, tablefmt='grid'))
        else:
            self.stdout.write(self.style.WARNING('Aucun professeur trouvé'))

        # Afficher les administrateurs
        self.stdout.write('\n' + self.style.SUCCESS('=== ADMINISTRATEURS ==='))
        admin_data = []
        for admin in admins:
            admin_data.append([
                admin.get_full_name(),
                admin.username,
                'password123',
                admin.email
            ])
        
        if admin_data:
            headers = ['Nom complet', 'Nom d\'utilisateur', 'Mot de passe', 'Email']
            self.stdout.write(tabulate(admin_data, headers=headers, tablefmt='grid'))
        else:
            self.stdout.write(self.style.WARNING('Aucun administrateur trouvé'))

        # Afficher un résumé
        self.stdout.write('\n' + self.style.SUCCESS('=== RÉSUMÉ ==='))
        self.stdout.write(f'Total étudiants : {len(students)}')
        self.stdout.write(f'Total professeurs : {len(teachers)}')
        self.stdout.write(f'Total administrateurs : {len(admins)}')
        self.stdout.write('\nMot de passe par défaut pour tous les utilisateurs : password123') 