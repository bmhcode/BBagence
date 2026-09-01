from django.contrib import admin
from .models import Profile, Agence, Car, CarImages, Brand, Evenement, ContactMessage, ArticleBlog
from django.utils.html import format_html
from django.contrib.auth.models import User

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

@admin.register(Agence)
class AgenceAdmin(admin.ModelAdmin):
    list_display = ('nom', 'manager','ville','est_en_vedette')
    list_filter = ('manager','ville','est_en_vedette')
    search_fields = ('nom', 'description')
    prepopulated_fields = {'slug': ('nom',)}

class CarImageInline(admin.TabularInline):
    model = CarImages
    extra = 3
    fields = ('image', 'caption')
    
@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('agence', 'marque', 'annee','prix_actuel', 'est_en_vedette', 'est_en_promotion')
    list_filter = ('agence', 'marque', 'est_en_promotion')
    search_fields = ('marque','annee')
    # prepopulated_fields = {'slug': ('marque',)}
    inlines = [CarImageInline]
    fieldsets = [
        (None, {
            'fields': ('agence', 'marque', 'modele', 'annee', 'description')
        }),
        ('Caractéristiques', {
            'fields': ('couleur', 'finition', 'moteur', 'kilometrage', 'energie', 'boite_de_vitesse')
        }),
        ('Prix', {
            'fields': ('prix_ancien', 'prix_actuel')
        }),
        ('Promotion', {
            'fields': ('est_en_promotion', 'prix_promo', 'date_debut_promo', 'date_fin_promo', 'date_debut_publication_promo')
        }),
    ]
    list_editable = ['prix_actuel', 'est_en_vedette', 'est_en_promotion',]

    def get_thumbnail(self, obj):
        image = obj.main_image
        if image and image.image:
            return format_html(
                '<img src="{}" style="width:45px;height:45px;object-fit:cover;border-radius:8px;" />',
                image.image.url
            )
        return "-"

    get_thumbnail.short_description = 'Aperçu'


@admin.register(Evenement)
class EvenementAdmin(admin.ModelAdmin):
    list_display = ('titre', 'date_debut', 'date_fin', 'lieu')
    list_filter = ('date_debut','date_fin')
    search_fields = ('titre', 'description')
    prepopulated_fields = {'slug': ('titre',)}

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('nom','image', 'date_debut', 'date_fin')
    search_fields = ('nom',)
    prepopulated_fields = {'slug': ('nom',)}


@admin.register(ArticleBlog)
class ArticleBlogAdmin(admin.ModelAdmin):
    list_display = ('titre', 'date_debut_publication', 'date_fin_publication')
    search_fields = ('titre', 'contenu')
    prepopulated_fields = {'slug': ('titre',)}

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('nom', 'email', 'sujet', 'cree_le')
    readonly_fields = ('cree_le',)
