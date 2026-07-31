from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.urls import reverse

import uuid
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User

from django.conf import settings
from django.utils.html import mark_safe
from django.dispatch import receiver
from django.db.models.signals import post_save


# from .utils import generate_unique_slug

# =========================================
# HELPERS
# =========================================
def generate_unique_slug(model, field_value):
    base_slug = slugify(field_value)
    slug = base_slug
    while model.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{uuid.uuid4().hex[:5]}"
    return slug

# =========================================
# SUBSCRIPTION
# =========================================

class Subscription(models.Model):

    PLAN_CHOICES = (
        ('FREE', 'Free'),
        ('PRO', 'Pro'),
        ('BUSINESS', 'Business'),
    )

    PLAN_LIMITS = {
        'FREE': 3,
        'PRO': 5,
        'BUSINESS': None,  # None = Unlimited
    }
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='FREE')

    def max_products(self):
        return self.PLAN_LIMITS.get(self.plan)

    def __str__(self):
        return f"{self.user.username} - {self.plan}"

# =========================================
# AGENCE
# =========================================

ALGERIA_CITIES = [
    ('Adrar', '01 - Adrar'), ('Chlef', '02 - Chlef'), ('Laghouat', '03 - Laghouat'), ('Oum El Bouaghi', '04 - Oum El Bouaghi'),
    ('Batna', '05 - Batna'), ('Béjaïa', '06 - Béjaïa'), ('Biskra', '07 - Biskra'), ('Béchar', '08 - Béchar'),
    ('Blida', '09 - Blida'), ('Bouira', '10 - Bouira'), ('Tamanrasset', '11 - Tamanrasset'), ('Tébessa', '12 - Tébessa'),
    ('Tlemcen', '13 - Tlemcen'), ('Tiaret', '14 - Tiaret'), ('Tizi Ouzou', '15 - Tizi Ouzou'), ('Alger', '16 - Alger'),
    ('Djelfa', '17 - Djelfa'), ('Jijel', '18 - Jijel'), ('Sétif', '19 - Sétif'), ('Saïda', '20 - Saïda'),
    ('Skikda', '21 - Skikda'), ('Sidi Bel Abbès', '22 - Sidi Bel Abbès'), ('Annaba', '23 - Annaba'), ('Guelma', '24 - Guelma'),
    ('Constantine', '25 - Constantine'), ('Médéa', '26 - Médéa'), ('Mostaganem', '27 - Mostaganem'), ("M'Sila", "28 - M'Sila"),
    ('Mascara', '29 - Mascara'), ('Ouargla', '30 - Ouargla'), ('Oran', '31 - Oran'), ('El Bayadh', '32 - El Bayadh'),
    ('Illizi', '33 - Illizi'), ('Bordj Bou Arreridj', '34 - Bordj Bou Arreridj'), ('Boumerdès', '35 - Boumerdès'), ('El Tarf', '36 - El Tarf'),
    ('Tindouf', '37 - Tindouf'), ('Tissemsilt', '38 - Tissemsilt'), ('El Oued', '39 - El Oued'), ('Khenchela', '40 - Khenchela'),
    ('Souk Ahras', '41 - Souk Ahras'), ('Tipaza', '42 - Tipaza'), ('Mila', '43 - Mila'), ('Aïn Defla', '44 - Aïn Defla'),
    ('Naâma', '45 - Naâma'), ('Aïn Témouchent', '46 - Aïn Témouchent'), ('Ghardaïa', '47 - Ghardaïa'), ('Relizane', '48 - Relizane'),
    ('Timimoun', '49 - Timimoun'), ('Bordj Badji Mokhtar', '50 - Bordj Badji Mokhtar'), ('Ouled Djellal', '51 - Ouled Djellal'),
    ('Béni Abbès', '52 - Béni Abbès'), ('In Salah', '53 - In Salah'), ('In Guezzam', '54 - In Guezzam'), ('Touggourt', '55 - Touggourt'),
    ('Djanet', '56 - Djanet'), ("El M'Ghair", "57 - El M'Ghair"), ('El Meniaa', '58 - El Meniaa')
]

class Agence(models.Model):
    
    nom = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='agences/')

    # ── Relation ──
    manager = models.ForeignKey(User,on_delete=models.CASCADE, related_name='agences')

    # ── Contact ── 
    telephone = models.CharField(max_length=20, blank=True, null=True)
    site_web = models.URLField(blank=True, null=True)
    email    = models.EmailField(blank=True, null=True, verbose_name="Email")
    
    ville = models.CharField(max_length=100, choices=ALGERIA_CITIES, blank=True, null=True, verbose_name=_("Ville"))
    commune = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Commune"))
    adresse = models.CharField(max_length=200, help_text="Ex: Niveau 1, Aile Nord")
    
    # ── Google Map ──
    google_map = models.URLField(max_length=1000, blank=True, verbose_name="Google Map URL")

    est_en_vedette = models.BooleanField(default=False)
    
    # ── Date ──    
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)
    date_ouverture = models.DateField(blank=True, null=True, verbose_name="date d'ouverture (si future)")

    # ── Horaire ──
    heure_ouverture = models.TimeField(null=True, blank=True)
    heure_fermeture = models.TimeField(null=True, blank=True)

    # ── Fermeture ──
    est_ferme = models.BooleanField(default=False, verbose_name="fermée ?")
    observation = models.TextField(blank=True, verbose_name="Observation") # En cas de fermeture ou autre

    class Meta:
        verbose_name = "Agence"
        verbose_name_plural = "Agences"

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        # إذا كان كائن جديد
        if not self.pk:
            self.slug = generate_unique_slug(Agence, self.nom)
        else:
            old = Agence.objects.get(pk=self.pk)
            # إذا تغيّر الاسم → غيّر slug
            if old.nom != self.nom:
                self.slug = generate_unique_slug(Agence, self.nom)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('agence_detail', kwargs={'agence_slug': self.slug})

    @property
    def logoURL(self):
        return self.image.url if self.image else ""

    def main_image(self):
        return self.images.filter(is_main=True).first()

    def main_video(self):
        return self.videos.filter(is_main=True).first()


    @property
    def localisation(self):
        if self.ville and self.commune:
            return f"{self.ville}, {self.commune} - {self.adresse}"
        elif self.ville:
            return f"{self.ville} - {self.adresse}"
        elif self.commune:
            return f"{self.commune} - {self.adresse}"
        return self.adresse or "No location"

    @property
    def est_ouvert_maintenant(self):
        if self.est_ferme:
            return False

        if not self.heure_ouverture or not self.heure_fermeture:
            return False

        now = timezone.localtime().time()

        if self.heure_ouverture < self.heure_fermeture:
            return self.heure_ouverture <= now <= self.heure_fermeture

        return (
            now >= self.heure_ouverture or
            now <= self.heure_fermeture
        )

    def get_ouvert_ferme_display(self):
        if self.est_ferme:
            return "Fermée"

        if not self.heure_ouverture or not self.heure_fermeture:
            return "Horaires inconnus"

        return f"{self.heure_ouverture.strftime('%H:%M')} - {self.heure_fermeture.strftime('%H:%M')}"    
      
class AgenceImages(models.Model):
    agence = models.ForeignKey(Agence, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='agence/images/')
    legende = models.CharField(max_length=200, blank=True)
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.agence.nom}"

class AgenceVideos(models.Model):
    agence = models.ForeignKey(Agence, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='agence/videos/')
    legende = models.CharField(max_length=200, blank=True)
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"Video for {self.agence.nom}"    

class AgenceSocial(models.Model):
    agence = models.OneToOneField(Agence, on_delete=models.CASCADE, related_name='social')
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    tiktok = models.URLField(blank=True)
    whatsapp = models.URLField(blank=True)
    telegram = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
   
class AgenceValidation(models.Model):
    PERIOD_CHOICES = [
        (30, '1 Month'),
        (90, '3 Months'),
        (180, '6 Months'),
        (365, '1 Year'),
    ]
    agence = models.OneToOneField(Agence, on_delete=models.CASCADE, related_name='validation')
    is_validated = models.BooleanField(default=False)
    observation = models.TextField(blank=True, verbose_name="Observation")

    date_debut = models.DateField(null=True, blank=True,verbose_name=_("Start date"))
    periode = models.IntegerField(choices=PERIOD_CHOICES, null=True, blank=True,verbose_name=_("Period"))

    def is_active(self):
        if self.date_debut and self.periode:
            from datetime import timedelta
            return self.date_debut + timedelta(days=self.periode)
        return None    

class AgenceReview(models.Model): # Agence Review 
    agence = models.ForeignKey(Agence, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    note = models.IntegerField(default=5)  # من 1 إلى 5
    commentaire = models.TextField(blank=True, verbose_name="Commentaire")
    cree_le = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('agence', 'user')  # user يقيّم مرة واحدة فقط
 
#============== End Agence ==============

# =========================================
# Car
# =========================================
class Car(models.Model):

    MARQUE_CHOICES = [
        ("Dacia", "Dacia"),
        ("Hyundai", "Hyundai"),
        ("Kia", "Kia"),
        ("Renault", "Renault"),
        ("Peugeot", "Peugeot"),
        ("Citroën", "Citroën"),
        ("Fiat", "Fiat"),
        ("Skoda", "Skoda"),
        ("Toyota", "Toyota"),
        ("Volkswagen", "Volkswagen"),
        ("BMW", "BMW"),
        ("Mercedes-Benz", "Mercedes-Benz"),
        ("Audi", "Audi"),
        ("Ford", "Ford"),
        ("Opel", "Opel"),
        ("Nissan", "Nissan"),
        ("Suzuki", "Suzuki"),
        ("Volkswagen", "Volkswagen"),
        ("Chevrolet", "Chevrolet"),
        ("Lexus", "Lexus"),
        ("Volvo", "Volvo"),
        ("Porsche", "Porsche"),
        ("Ferrari", "Ferrari"),
        ("Lamborghini", "Lamborghini"),
        ("McLaren", "McLaren"),
        ("Aston Martin", "Aston Martin"),
        ("Bentley", "Bentley"),
        ("Rolls-Royce", "Rolls-Royce"),
        ("Jaguar", "Jaguar"),
        ("Land Rover", "Land Rover"),
        ("Maserati", "Maserati"),
        ("Mini", "Mini"),
        ("Smart", "Smart"),
        ("Lada", "Lada"),
        ("Fiat", "Fiat"),
        ("Chery", "Chery"),
        ("Haval", "Haval"),
        ("Geely", "Geely"),
        ("MG", "MG"),
        ("Other", "Other"),
    ]

    CONDITION_CHOICES = [
        ("neuf", "Neuf"),
        ("moins_de_3ans", "Moins de 3 ans"),
        ("occasion", "Occasion"),
    ]

    FUEL_CHOICES = [
        ("essence", "Essence"),
        ("diesel", "Diesel"),
        ("gpl", "GPL"),
        ("hybride", "Hybride"),
        ("electrique", "Électrique"),
    ]

    TRANSMISSION_CHOICES = [
        ("manuelle", "Manuelle"),
        ("automatique", "Automatique"),
        ("semi_automatique", "Semi-automatique"),
    ]

    agence = models.ForeignKey(Agence, on_delete=models.CASCADE, related_name="cars")
      
    etat = models.CharField(max_length=20, choices=CONDITION_CHOICES, default="neuf")

    annee = models.PositiveIntegerField()
    marque = models.CharField(max_length=20, choices=MARQUE_CHOICES, default="")
    modele = models.CharField(max_length=100)
    couleur = models.CharField(max_length=100, default="Black",blank=True, null=True)
    finition = models.CharField(max_length=100, default="Full options",blank=True, null=True)
    moteur = models.CharField(max_length=100, default="1.5 181ch 16v turbo",blank=True, null=True)
    energie = models.CharField(max_length=20, choices=FUEL_CHOICES, default="essence")
    boite_de_vitesse = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, default="automatique")
    kilometrage = models.PositiveIntegerField(default=0, help_text="Kilométrage en km")
    description = models.TextField(blank=True)

    ancien_prix = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    nouveau_prix = models.DecimalField(max_digits=12, decimal_places=2)

    # Promotion
    est_en_promotion = models.BooleanField(default=False)
    prix_promo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    date_debut_promo = models.DateField(null=True, blank=True)
    date_fin_promo = models.DateField(null=True, blank=True)

    est_en_vedette = models.BooleanField(default=False)
    est_disponible = models.BooleanField(default=True)

    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-cree_le"]
        verbose_name = "Car"
        verbose_name_plural = "Cars"

    def __str__(self):
        return f"{self.marque} {self.modele} ({self.annee})"

    def get_absolute_url(self):
        return reverse("car_detail", kwargs={"slug": self.slug})

    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         self.slug = generate_unique_slug(Car, self.titre)

    #     super().save(*args, **kwargs)

    def main_image(self):
        return self.images.filter(is_main=True).first()

    @property
    def is_new(self):
        return timezone.now() - self.cree_le <= timedelta(days=7)

    @property
    def discount_amount(self):
        if self.ancien_prix:
            return self.ancien_prix - self.nouveau_prix
        return Decimal("0.00")

    @property
    def discount_percentage(self):
        if self.ancien_prix and self.ancien_prix > 0:
            return round(
                ((self.ancien_prix - self.nouveau_prix) / self.ancien_prix) * 100,
                1
            )
        return 0

    @property
    def has_discount(self):
        return (
            self.ancien_prix is not None
            and self.ancien_prix > self.nouveau_prix
        )
        
    @property
    def prix_affiche(self):
        """Retourne le prix promo s'il est actif, sinon le prix normal"""
        if self.est_en_promotion and self.prix_promo and self.est_promotion_valide():
            return self.prix_promo
        return self.nouveau_prix

    @property
    def est_en_promotion_valide(self):
        """Vérifie si la promotion est active"""
        return (
            self.est_en_promotion
            and self.prix_promo
            and self.date_debut_promo
            and self.date_fin_promo
            and self.date_debut_promo <= timezone.now().date() <= self.date_fin_promo
        )        

class CarImages(models.Model):
    car = models.ForeignKey(Car, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="cars/gallery/")
    caption = models.CharField(max_length=200, blank=True)
    is_main = models.BooleanField(default=False)
    cree_le = models.DateTimeField(auto_now_add=True)

    # 👇 لترتيب الصور (الأهم أولاً)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-is_main", "id"]

    def __str__(self):
        return f"{self.car.modele} Image"     


#============== End Car ==============

class Evenement(models.Model):
    titre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    date = models.DateTimeField()
    description = models.TextField()
    image = models.ImageField(upload_to='evenements/')
    lieu = models.CharField(max_length=200, default="Place Centrale")
    cree_le = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('evenement_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = "Événement"
        verbose_name_plural = "Événements"

class Promotion(models.Model):
    agence = models.ForeignKey(Agence, on_delete=models.CASCADE, related_name='promotions')
    
    titre = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='promotions/')
    video = models.FileField(upload_to='promotions/videos/', blank=True, null=True, verbose_name="Video")

    date_debut = models.DateField()
    date_fin = models.DateField()

    cree_le = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        from django.core.exceptions import ValidationError
        if self.agence:
            qs = Promotion.objects.filter(agence=self.agence)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError("Cette agence a déjà une promotion active. Une seule promotion est autorisée par agence.")


    def __str__(self):
        return f"{self.titre} - {self.agence.nom}"

    class Meta:
        verbose_name = "Promotion"
        verbose_name_plural = "Promotions"

class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wishlist")
    cars = models.ManyToManyField(Car, blank=True, related_name="wishlists")

    def __str__(self):
        return f"Wishlist de {self.user.username}"

class ContactMessage(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    sujet = models.CharField(max_length=200)
    message = models.TextField()
    cree_le = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message de {self.nom} - {self.sujet}"

class ArticleBlog(models.Model):
    titre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    contenu = models.TextField()
    image = models.ImageField(upload_to='blog/')
    date_publication = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = "Article de Blog"
        verbose_name_plural = "Articles de Blog"


# =========================================
# PROFILE
# =========================================

class Profile(models.Model):
    USER_ROLES = (
        ('customer', 'Customer'),
        ('agence_owner', 'Agence Owner'), 
        ('admin', 'Admin'),
        ('superadmin', 'Super Admin'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=USER_ROLES, default='Customer')
    telephone = models.CharField(max_length=20, blank=True, null=True, default='-')
    ville = models.CharField(max_length=100, choices=ALGERIA_CITIES, blank=True, null=True, verbose_name="Wilaya")
    commune = models.CharField(max_length=100, blank=True, null=True, verbose_name="Commune")
    adresse = models.TextField(blank=True, verbose_name="Adresse")
    image = models.ImageField(upload_to='profiles/', default='profiles/default.png')
    
    cree_le = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + ' : ' + self.role

    @property
    def imageURL(self):
        return self.image.url if self.image else ""

# =========================================
# SIGNAL (AUTO CREATE PROFILE)
# =========================================

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)