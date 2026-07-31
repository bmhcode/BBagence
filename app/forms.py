from django import forms
from .models import Agence, AgenceImages, AgenceVideos, ContactMessage



class AgencePresentationForm(forms.ModelForm):
    class Meta:
        model = Agence
        fields = ['google_map']
        widgets = {
            'map_image': forms.ClearableFileInput(attrs={'class': 'form-file'}),
            'google_map':    forms.URLInput(attrs={'placeholder': 'Ex : https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3213.788125040453!2d6.648492250352666!3d36.34168453072031!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x12f177002ce3aef1%3A0x9ad95dfb0b6bf646!2z2K3ZiiDZgtmF2KfYtQ!5e0!3m2!1sfr!2sdz!4v1783250604868!5m2!1sfr!2sdz'}),
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
        fields = ['nom', 'email', 'sujet', 'message']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Votre email'}),
            'sujet': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sujet'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Votre message', 'rows': 5}),
        }
