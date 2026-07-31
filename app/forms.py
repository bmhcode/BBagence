from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Agence, AgenceImages, AgenceVideos, AgenceSocial, Car, CarImages, ContactMessage, Profile, ALGERIA_CITIES

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Adresse e-mail")
    first_name = forms.CharField(max_length=150, required=True, label="Prénom")
    last_name = forms.CharField(max_length=150, required=True, label="Nom")
    role = forms.ChoiceField(choices=Profile.USER_ROLES, initial='customer', label="Rôle")
    phone = forms.CharField(max_length=20, required=False, label="Téléphone")
    city = forms.ChoiceField(choices=[('', '---------')] + ALGERIA_CITIES, required=False, label="Wilaya")
    commune = forms.CharField(max_length=100, required=False, label="Commune")
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label="Adresse")
    image = forms.ImageField(required=False, label="Photo de profil")

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # The receiver post_save automatically creates the profile
            profile = user.profile
            profile.role = self.cleaned_data.get('role', 'customer')
            profile.telephone = self.cleaned_data.get('phone', '')
            profile.ville = self.cleaned_data.get('city', '')
            profile.commune = self.cleaned_data.get('commune', '')
            profile.adresse = self.cleaned_data.get('address', '')
            if self.cleaned_data.get('image'):
                profile.image = self.cleaned_data.get('image')
            profile.save()
        return user

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class ProfileForm(forms.ModelForm):
    phone = forms.CharField(max_length=20, required=False, label="Téléphone", widget=forms.TextInput(attrs={'class': 'form-control'}))
    city = forms.ChoiceField(choices=[('', '---------')] + ALGERIA_CITIES, required=False, label="Wilaya", widget=forms.Select(attrs={'class': 'form-select'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False, label="Adresse")

    class Meta:
        model = Profile
        fields = ['role', 'image', 'commune']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'id': 'imageUpload'}),
            'commune': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['phone'].initial = self.instance.telephone
            self.fields['city'].initial = self.instance.ville
            self.fields['address'].initial = self.instance.adresse

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.telephone = self.cleaned_data.get('phone', '')
        profile.ville = self.cleaned_data.get('city', '')
        profile.adresse = self.cleaned_data.get('address', '')
        if commit:
            profile.save()
        return profile

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class CarForm(forms.ModelForm):
    image = forms.ImageField(required=False, label="Image principale (remplace l'actuelle)")
    gallery = forms.FileField(widget=MultipleFileInput(), required=False, label="Ajouter d'autres images")

    class Meta:
        model = Car
        fields = [
            'marque', 'modele', 'annee', 'couleur', 'finition', 'moteur', 
            'energie', 'boite_de_vitesse', 'kilometrage', 'description', 
            'ancien_prix', 'nouveau_prix', 'est_en_promotion', 'prix_promo', 
            'date_debut_promo', 'date_fin_promo', 'est_en_vedette', 'est_disponible'
        ]
        widgets = {
            'marque': forms.Select(attrs={'class': 'form-select'}),
            'modele': forms.TextInput(attrs={'class': 'form-control'}),
            'annee': forms.NumberInput(attrs={'class': 'form-control'}),
            'couleur': forms.TextInput(attrs={'class': 'form-control'}),
            'finition': forms.TextInput(attrs={'class': 'form-control'}),
            'moteur': forms.TextInput(attrs={'class': 'form-control'}),
            'energie': forms.Select(attrs={'class': 'form-select'}),
            'boite_de_vitesse': forms.Select(attrs={'class': 'form-select'}),
            'kilometrage': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'ancien_prix': forms.NumberInput(attrs={'class': 'form-control'}),
            'nouveau_prix': forms.NumberInput(attrs={'class': 'form-control'}),
            'est_en_promotion': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'prix_promo': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_debut_promo': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin_promo': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'est_en_vedette': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'est_disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class AgenceForm(forms.ModelForm):
    class Meta:
        model = Agence
        fields = [
            'nom', 'description', 'image', 'banniere', 'telephone', 'site_web', 
            'email', 'ville', 'commune', 'adresse', 'google_map', 
            'heure_ouverture', 'heure_fermeture', 'est_ferme', 'observation'
        ]
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'banniere': forms.FileInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'site_web': forms.URLInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'ville': forms.Select(attrs={'class': 'form-select'}),
            'commune': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'google_map': forms.URLInput(attrs={'class': 'form-control'}),
            'heure_ouverture': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'heure_fermeture': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'est_ferme': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observation': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class AgenceSocialForm(forms.ModelForm):
    class Meta:
        model = AgenceSocial
        fields = ['facebook', 'instagram', 'twitter', 'tiktok', 'whatsapp', 'telegram', 'youtube']
        widgets = {
            'facebook': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Facebook URL'}),
            'instagram': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Instagram URL'}),
            'twitter': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Twitter URL'}),
            'tiktok': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'TikTok URL'}),
            'whatsapp': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'WhatsApp Link/Number'}),
            'telegram': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Telegram Link'}),
            'youtube': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'YouTube URL'}),
        }

class AgencePresentationForm(forms.ModelForm):
    class Meta:
        model = Agence
        fields = ['google_map']
        widgets = {
            'google_map': forms.URLInput(attrs={'placeholder': 'Ex : https://www.google.com/maps/embed?pb=...'}),
        }

class AgenceImageForm(forms.ModelForm):
    class Meta:
        model = AgenceImages
        fields = ['image', 'legende','is_main']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-file'}),
            'legende': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Légende de l\'image'}),
            'is_main': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class AgenceVideoForm(forms.ModelForm):
    class Meta:
        model = AgenceVideos
        fields = ['video', 'legende','is_main']
        widgets = {
            'video': forms.ClearableFileInput(attrs={'class': 'form-file'}),
            'legende': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Légende de la vidéo'}),
            'is_main': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['nom', 'email', 'sujet', 'message', 'agence']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Votre email'}),
            'sujet': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sujet'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Votre message', 'rows': 5}),
            'agence': forms.Select(attrs={'class': 'form-select'}),
        }
