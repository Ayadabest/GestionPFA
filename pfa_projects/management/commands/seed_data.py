from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = 'Charge les données initiales pour les projets et les étudiants'

    def handle(self, *args, **kwargs):
        try:
            # Charger les fixtures
            call_command('loaddata', 'initial_data.json')
            
            self.stdout.write(
                self.style.SUCCESS('Les données ont été chargées avec succès!')
            )
            
            # Afficher un résumé des données chargées
            self.stdout.write("\nDonnées chargées :")
            self.stdout.write("- 1 enseignant")
            self.stdout.write("- 3 étudiants")
            self.stdout.write("- 3 projets disponibles")
            
            self.stdout.write("\nVous pouvez maintenant vous connecter avec les comptes suivants :")
            self.stdout.write("Enseignant :")
            self.stdout.write("  - Username : prof1")
            self.stdout.write("  - Password : password123")
            self.stdout.write("\nÉtudiants :")
            self.stdout.write("  - Username : etudiant1, etudiant2, etudiant3")
            self.stdout.write("  - Password : password123")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erreur lors du chargement des données : {str(e)}')
            ) 