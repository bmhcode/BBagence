from django.contrib import admin
from .models import Profile, Agence, Car, CarImages, Evenement, Promotion, ContactMessage, ArticleBlog
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
    fields = ('image', 'caption', 'is_main', 'order')
    
@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('agence', 'marque', 'annee','nouveau_prix', 'est_en_vedette')
    list_filter = ('agence', 'marque')
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
            'fields': ('ancien_prix', 'nouveau_prix')
        }),
    ]
    list_editable = ['nouveau_prix', 'est_en_vedette']

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
    list_display = ('titre', 'date', 'lieu')
    list_filter = ('date',)
    search_fields = ('titre', 'description')
    prepopulated_fields = {'slug': ('titre',)}

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('titre', 'agence', 'date_debut', 'date_fin')
    list_filter = ('agence', 'date_debut')
    search_fields = ('titre', 'description')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('nom', 'email', 'sujet', 'cree_le')
    readonly_fields = ('cree_le',)

@admin.register(ArticleBlog)
class ArticleBlogAdmin(admin.ModelAdmin):
    list_display = ('titre', 'date_publication')
    search_fields = ('titre', 'contenu')
    prepopulated_fields = {'slug': ('titre',)}
