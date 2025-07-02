#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pfa_management.settings')
django.setup()

from users.models import User
from pfa_projects.models import Project, Message, Report
from pfa_teams.models import Team
from django.core.files.base import ContentFile

def test_auto_classification():
    """Tester le système de classification automatique des rapports"""
    
    print("🧪 TEST DE CLASSIFICATION AUTOMATIQUE DES RAPPORTS")
    print("=" * 60)
    
    # Récupérer un étudiant et un professeur
    try:
        student = User.objects.filter(role='student').first()
        teacher = User.objects.filter(role='teacher').first()
        project = Project.objects.first()
        
        if not all([student, teacher, project]):
            print("❌ Données de test manquantes")
            return
        
        print(f"👨‍🎓 Étudiant: {student.username}")
        print(f"👨‍🏫 Professeur: {teacher.username}")
        print(f"📋 Projet: {project.title}")
        
        # Vérifier si l'étudiant a une équipe pour ce projet
        try:
            team = Team.objects.get(members=student, project=project)
            print(f"👥 Équipe: {team.name}")
        except Team.DoesNotExist:
            print("❌ L'étudiant n'a pas d'équipe pour ce projet")
            return
        
        # Créer un message avec un fichier PDF simulé
        print("\n📤 Création d'un message avec pièce jointe PDF...")
        
        # Créer un fichier PDF simulé
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test PDF) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF"
        
        message = Message.objects.create(
            sender=student,
            recipient=teacher,
            project=project,
            subject="Rapport TP3 - Classification automatique",
            content="Veuillez trouver ci-joint le rapport du TP3.",
            message_type='student_to_teacher'
        )
        
        # Ajouter le fichier PDF
        message.attachment.save('rapport_tp3.pdf', ContentFile(pdf_content), save=True)
        print(f"✅ Message créé avec ID: {message.id}")
        
        # Tester la classification automatique
        print("\n🔍 Test de classification automatique...")
        auto_report = message.auto_classify_as_report()
        
        if auto_report:
            print(f"✅ Rapport automatiquement classé!")
            print(f"   📄 Titre: {auto_report.title}")
            print(f"   👥 Équipe: {auto_report.team.name}")
            print(f"   📅 Date: {auto_report.submission_date}")
            print(f"   📊 Statut: {auto_report.status}")
            print(f"   💬 Feedback: {auto_report.feedback}")
            
            # Vérifier que le message est marqué comme classé
            message.refresh_from_db()
            if message.auto_classified_as_report:
                print("✅ Message marqué comme classé automatiquement")
            else:
                print("❌ Message non marqué comme classé")
        else:
            print("❌ Aucun rapport créé automatiquement")
        
        # Afficher les rapports du projet
        print(f"\n📋 Rapports du projet '{project.title}':")
        reports = project.reports.all()
        for i, report in enumerate(reports, 1):
            print(f"   {i}. {report.title} - {report.team.name} - {report.status}")
        
        print("\n🎉 Test terminé!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_auto_classification() 