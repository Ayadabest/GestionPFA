import os
from pathlib import Path

# Configuration pour l'envoi d'emails
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'votre_email@gmail.com'  # À remplacer par votre email
EMAIL_HOST_PASSWORD = 'votre_mot_de_passe'  # À remplacer par votre mot de passe d'application

# URL de base du site
BASE_URL = 'http://localhost:8000'  # À adapter selon votre configuration

# Media files (Uploaded files)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Ensure the media directory exists
MEDIA_DIRS = ['media/reports', 'media/messages']
for dir_path in MEDIA_DIRS:
    os.makedirs(os.path.join(BASE_DIR, dir_path), exist_ok=True) 