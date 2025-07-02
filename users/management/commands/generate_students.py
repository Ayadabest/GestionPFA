from django.core.management.base import BaseCommand
from users.models import User, StudentProfile
from django.db import transaction
import random

class Command(BaseCommand):
    help = 'Génère des étudiants avec des noms réalistes'

    def handle(self, *args, **kwargs):
        # Définir les spécialités et niveaux disponibles
        specialties = [
            'Génie Civil',
            'Informatique et Réseaux',
            'Génie Industriel'
        ]
        levels = ['3ème année', '4ème année']

        students_data = [
            ('Ahmed', 'Alami', 'a.alami23@emi.ac.ma'),
            ('Sara', 'Benani', 's.benani22@emi.ac.ma'),
            ('Karim', 'Chraibi', 'k.chraibi23@emi.ac.ma'),
            ('Leila', 'Daoudi', 'l.daoudi22@emi.ac.ma'),
            ('Omar', 'El Fassi', 'o.elfassi23@emi.ac.ma'),
            ('Fatima', 'Ghazali', 'f.ghazali22@emi.ac.ma'),
            ('Hassan', 'Idrissi', 'h.idrissi23@emi.ac.ma'),
            ('Nadia', 'Jalal', 'n.jalal22@emi.ac.ma'),
            ('Mehdi', 'Karimi', 'm.karimi23@emi.ac.ma'),
            ('Amina', 'Lahlou', 'a.lahlou22@emi.ac.ma'),
            ('Youssef', 'Mansouri', 'y.mansouri23@emi.ac.ma'),
            ('Houda', 'Najjar', 'h.najjar22@emi.ac.ma'),
            ('Rachid', 'Ouazzani', 'r.ouazzani23@emi.ac.ma'),
            ('Samira', 'Qabbaj', 's.qabbaj22@emi.ac.ma'),
            ('Tarik', 'Raji', 't.raji23@emi.ac.ma'),
            ('Zineb', 'Saadi', 'z.saadi22@emi.ac.ma'),
            ('Hamza', 'Tazi', 'h.tazi23@emi.ac.ma'),
            ('Malika', 'Wahbi', 'm.wahbi22@emi.ac.ma'),
            ('Jamal', 'Ziani', 'j.ziani23@emi.ac.ma'),
            ('Sofia', 'Bennani', 's.bennani22@emi.ac.ma'),
        ]

        with transaction.atomic():
            for first_name, last_name, email in students_data:
                try:
                    # Choisir aléatoirement une spécialité et un niveau
                    specialty = random.choice(specialties)
                    level = random.choice(levels)
                    
                    # Créer l'utilisateur
                    user = User.objects.create_user(
                        username=email.split('@')[0],
                        email=email,
                        password='password123',  # Mot de passe par défaut
                        first_name=first_name,
                        last_name=last_name,
                        role='student'
                    )

                    # Créer le profil étudiant
                    StudentProfile.objects.create(
                        user=user,
                        student_id=f"STU{user.id:03d}",
                        department=specialty,
                        level=level,
                        phone=f"+212 6{random.randint(10000000, 99999999)}"  # Numéro de téléphone marocain aléatoire
                    )

                    self.stdout.write(self.style.SUCCESS(
                        f'Créé étudiant: {first_name} {last_name} ({specialty} - {level})'
                    ))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'Erreur lors de la création de {first_name} {last_name}: {str(e)}'
                    )) 