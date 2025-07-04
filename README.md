# Système de Gestion des Binômes PFA

Ce projet est un système de gestion des binômes pour les Projets de Fin d'Année (PFA), développé avec Django.

## Fonctionnalités

- Gestion des comptes utilisateurs (étudiants, enseignants, administrateurs)
- Formation et gestion des binômes
- Gestion des projets PFA
- Système de messagerie intégré
- Suivi de l'avancement des projets
- Gestion des soumissions de documents

## Installation

1. Cloner le dépôt :
```bash
git clone [url-du-depot]
cd pfa-management
```

2. Créer un environnement virtuel et l'activer :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Effectuer les migrations :
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Créer un super utilisateur :
```bash
python manage.py createsuperuser
```

6. Lancer le serveur de développement :
```bash
python manage.py runserver
```

## Structure du Projet

- `accounts/` : Gestion des utilisateurs et authentification
- `projects/` : Gestion des projets PFA
- `teams/` : Gestion des binômes et de la communication

## Utilisation

1. Accéder à l'interface d'administration : `http://localhost:8000/admin/`
2. Créer des comptes utilisateurs (étudiants, enseignants)
3. Les étudiants peuvent :
   - Former des binômes
   - Choisir des projets
   - Soumettre des documents
4. Les enseignants peuvent :
   - Créer des projets
   - Suivre l'avancement
   - Évaluer les soumissions

## Auteur

Elouajjite Aya
Contact : Aya.Ouajjite@emsi-edu.ma #   G e s t i o n P F A  
 