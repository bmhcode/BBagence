import os
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from app.models import Agence, Evenement, Promotion, ArticleBlog

def populate():
    print("Populating data...")

    # Magasins
    m1 = Agence.objects.get_or_create(
        nom="Zara auto", 
        categorie="mode", 
        description="Vêtements tendance pour hommes, femmes et enfants.",
        localisation="Niveau 1, Aile Est",
        est_en_vedette=True
    )[0]

    m2 = Agence.objects.get_or_create(
        nom="Apple Store", 
        categorie="technologie", 
        description="Découvrez les derniers iPhone, Mac et plus encore.",
        localisation="Rez-de-chaussée",
        est_en_vedette=True
    )[0]

    m3 = Agence.objects.get_or_create(
        nom="Sephora", 
        categorie="beaute", 
        description="Parfums, maquillage et soins de grandes marques.",
        localisation="Niveau 1, Centre",
        est_en_vedette=True
    )[0]

    m4 = Agence.objects.get_or_create(
        nom="Starbucks", 
        categorie="restauration", 
        description="Cafés de spécialité et pâtisseries gourmandes.",
        localisation="Niveau 2, Terrasse",
        est_en_vedette=False
    )[0]

    # Promotions
    Promotion.objects.get_or_create(
        titre="Soldes d'Été",
        description="Jusqu'à -50% sur une sélection d'articles d'été.",
        date_debut=timezone.now().date(),
        date_fin=(timezone.now() + timedelta(days=30)).date(),
        agence=m1
    )

    Promotion.objects.get_or_create(
        titre="Offre Étudiante",
        description="Remise de 10% sur les Mac pour les étudiants.",
        date_debut=timezone.now().date(),
        date_fin=(timezone.now() + timedelta(days=365)).date(),
        magasin=m2
    )

    # Evenements
    Evenement.objects.get_or_create(
        titre="Concert de Jazz Live",
        date=timezone.now() + timedelta(days=7),
        description="Venez profiter d'une soirée jazz exceptionnelle sur la place centrale.",
        lieu="Place Centrale"
    )

    Evenement.objects.get_or_create(
        titre="Atelier Maquillage",
        date=timezone.now() + timedelta(days=14),
        description="Apprenez les techniques des pros avec les experts Sephora.",
        lieu="Boutique Sephora"
    )

    # Blog
    ArticleBlog.objects.get_or_create(
        titre="5 Tendances Mode pour le Printemps",
        contenu="Découvrez les couleurs et les styles qui feront fureur cette saison..."
    )

    ArticleBlog.objects.get_or_create(
        titre="L'Ouverture du Nouvel Espace Tech",
        contenu="Nous sommes ravis de vous présenter notre nouvel espace dédié à l'innovation..."
    )

    print("Population successful.")

if __name__ == "__main__":
    populate()
