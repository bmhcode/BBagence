from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.db.models import Q, Sum, Count
from django.db import transaction
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.views.decorators.http import require_POST 
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.views import View
from django.http import JsonResponse
from django.contrib.auth import logout
from django.utils import timezone

from .models import (
    Agence, AgenceImages, AgenceVideos, AgenceSocial, Car, CarImages, 
    Evenement, Promotion, ArticleBlog, ContactMessage, Wishlist, Profile
)
from .forms import (
    ContactForm, AgencePresentationForm, AgenceImageForm, AgenceVideoForm,
    SignupForm, UserForm, ProfileForm, CarForm, AgenceForm, AgenceSocialForm
)

# =========================================
# MIXINS & PERMISSIONS
# =========================================
class AgenceManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_superuser:
            return True
        
        # Check by agence_slug
        agence_slug = self.kwargs.get('agence_slug')
        if agence_slug:
            agence = get_object_or_404(Agence, slug=agence_slug)
            return agence.manager == self.request.user
            
        # Check by pk or car_id
        car_id = self.kwargs.get('car_id') or self.kwargs.get('pk')
        if car_id:
            car = get_object_or_404(Car, pk=car_id)
            return car.agence.manager == self.request.user
            
        return False

# =========================================
# AUTHENTICATION VIEWS
# =========================================
class SignupView(CreateView):
    form_class = SignupForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        # Automatically create wishlist for user
        Wishlist.objects.get_or_create(user=user)
        messages.success(self.request, "Votre compte a été créé avec succès ! Connectez-vous maintenant.")
        return super().form_valid(form)

class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, "Vous avez été déconnecté avec succès.")
        return redirect('home')
        
    def post(self, request):
        logout(request)
        messages.success(request, "Vous avez été déconnecté avec succès.")
        return redirect('home')

class UserProfileUpdateView(LoginRequiredMixin, View):
    def get(self, request):
        u_form = UserForm(instance=request.user)
        p_form = ProfileForm(instance=request.user.profile)
        return render(request, 'registration/user_update.html', {'u_form': u_form, 'p_form': p_form})

    def post(self, request):
        u_form = UserForm(request.POST, instance=request.user)
        p_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès !")
            return redirect('profile')
        return render(request, 'registration/user_update.html', {'u_form': u_form, 'p_form': p_form})

# =========================================
# HOME & GENERAL VIEWS
# =========================================
class HomeView(TemplateView):
    template_name = 'app/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['agences_vedette'] = Agence.objects.filter(est_en_vedette=True)[:6]
        context['evenements_prochains'] = Evenement.objects.all().order_by('date')[:3]
        # Active car promotions
        context['promotions_actives'] = Car.objects.filter(
            est_en_promotion=True,
            date_debut_promo__lte=timezone.now().date(),
            date_fin_promo__gte=timezone.now().date()
        ).select_related('agence').prefetch_related('images')[:6]
        return context

class AgenceListView(ListView):
    model = Agence
    template_name = 'app/agence_list.html'
    context_object_name = 'agences'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q')
        agence_nom = self.request.GET.get('agence_nom')
        queryset = Agence.objects.all()
        if query:
            queryset = queryset.filter(
                Q(nom__icontains=query) | Q(description__icontains=query)
            )
        if agence_nom:
            queryset = queryset.filter(nom=agence_nom)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['noms'] = Agence.objects.values_list('nom', flat=True).distinct()
        context["villes"] = (Agence.objects.values_list("ville", flat=True).distinct().order_by("ville"))
        return context

class AgenceDetailView(DetailView):
    model = Agence
    template_name = 'app/agence_detail.html'
    context_object_name = 'agence'
    slug_url_kwarg = 'agence_slug'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('cars', 'images', 'videos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['videos'] = self.object.videos.all()
        return context

# =========================================
# AGENCE CRUD VIEWS
# =========================================
class AgenceCreateView(LoginRequiredMixin, CreateView):
    model = Agence
    form_class = AgenceForm
    template_name = 'app/agence_form.html'
    success_url = reverse_lazy('agence_list')

    def form_valid(self, form):
        form.instance.manager = self.request.user
        messages.success(self.request, "L'agence a été créée avec succès.")
        return super().form_valid(form)

class AgenceUpdateView(AgenceManagerRequiredMixin, UpdateView):
    model = Agence
    form_class = AgenceForm
    template_name = 'app/agence_form.html'
    slug_url_kwarg = 'agence_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        social_instance, created = AgenceSocial.objects.get_or_create(agence=self.object)
        if self.request.POST:
            context['social_form'] = AgenceSocialForm(self.request.POST, instance=social_instance)
        else:
            context['social_form'] = AgenceSocialForm(instance=social_instance)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        social_form = context['social_form']
        if social_form.is_valid():
            with transaction.atomic():
                self.object = form.save()
                social_form.save()
            messages.success(self.request, "Le profil de l'agence a été mis à jour.")
            return redirect('agence_detail', agence_slug=self.object.slug)
        else:
            return self.form_invalid(form)

class AgenceDeleteView(AgenceManagerRequiredMixin, DeleteView):
    model = Agence
    template_name = 'app/agence_confirm_delete.html'
    success_url = reverse_lazy('agence_list')
    slug_url_kwarg = 'agence_slug'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "L'agence a été supprimée.")
        return super().delete(request, *args, **kwargs)

# =========================================
# CAR CRUD VIEWS
# =========================================
class CarListView(ListView):
    model = Car
    template_name = 'app/car_list.html'
    context_object_name = 'cars'
    paginate_by = 12

    def get_queryset(self):
        queryset = Car.objects.all().select_related('agence').prefetch_related('images')
        
        # Search query
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(marque__icontains=q) | 
                Q(modele__icontains=q) | 
                Q(description__icontains=q)
            )
            
        # Filters
        marque = self.request.GET.get('marque')
        if marque:
            queryset = queryset.filter(marque=marque)
            
        ville = self.request.GET.get('ville')
        if ville:
            queryset = queryset.filter(agence__ville=ville)
            
        energie = self.request.GET.get('energie')
        if energie:
            queryset = queryset.filter(energie=energie)
            
        boite = self.request.GET.get('boite')
        if boite:
            queryset = queryset.filter(boite_de_vitesse=boite)
            
        prix_min = self.request.GET.get('prix_min')
        if prix_min:
            queryset = queryset.filter(nouveau_prix__gte=prix_min)
            
        prix_max = self.request.GET.get('prix_max')
        if prix_max:
            queryset = queryset.filter(nouveau_prix__lte=prix_max)
            
        annee_min = self.request.GET.get('annee_min')
        if annee_min:
            queryset = queryset.filter(annee__gte=annee_min)
            
        annee_max = self.request.GET.get('annee_max')
        if annee_max:
            queryset = queryset.filter(annee__lte=annee_max)
            
        km_max = self.request.GET.get('km_max')
        if km_max:
            queryset = queryset.filter(kilometrage__lte=km_max)
            
        # Sorting
        sort = self.request.GET.get('sort')
        if sort == 'price_asc':
            queryset = queryset.order_by('nouveau_prix')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-nouveau_prix')
        elif sort == 'year_desc':
            queryset = queryset.order_by('-annee')
        elif sort == 'km_asc':
            queryset = queryset.order_by('kilometrage')
        else:
            queryset = queryset.order_by('-cree_le')
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['marques'] = Car.MARQUE_CHOICES
        context['energies'] = Car.FUEL_CHOICES
        context['boites'] = Car.TRANSMISSION_CHOICES
        context['villes'] = Agence.objects.values_list('ville', flat=True).distinct().order_by('ville')
        # Pass user's wishlist IDs so the heart buttons render correctly
        if self.request.user.is_authenticated:
            wishlist, _ = Wishlist.objects.get_or_create(user=self.request.user)
            context['user_wishlist_ids'] = list(wishlist.cars.values_list('id', flat=True))
        else:
            context['user_wishlist_ids'] = []
        return context

class CarDetailView(DetailView):
    model = Car
    template_name = 'app/car_detail.html'
    context_object_name = 'car'
    pk_url_kwarg = 'car_id'
    slug_url_kwarg = 'agence_slug'

    def get_queryset(self):
        return super().get_queryset().select_related('agence').prefetch_related('images')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Increment view count
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cars_related'] = Car.objects.filter(agence=self.object.agence).exclude(pk=self.object.pk).prefetch_related('images')[:4]
        context['agence'] = self.object.agence
        return context

class CarCreateView(AgenceManagerRequiredMixin, CreateView):
    model = Car
    form_class = CarForm
    template_name = 'app/car_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['agence'] = get_object_or_404(Agence, slug=self.kwargs.get('agence_slug'))
        return context

    def form_valid(self, form):
        agence = get_object_or_404(Agence, slug=self.kwargs.get('agence_slug'))
        form.instance.agence = agence
        with transaction.atomic():
            car = form.save()
            
            # Save main image
            main_image = self.request.FILES.get('image')
            if main_image:
                CarImages.objects.create(car=car, image=main_image, is_main=True)
                
            # Save gallery images
            gallery_files = self.request.FILES.getlist('gallery')
            for f in gallery_files:
                CarImages.objects.create(car=car, image=f, is_main=False)
                
        messages.success(self.request, "La voiture a été ajoutée avec succès.")
        return redirect('cars_agence_list', agence_slug=agence.slug)

class CarUpdateView(AgenceManagerRequiredMixin, UpdateView):
    model = Car
    form_class = CarForm
    template_name = 'app/car_form.html'
    pk_url_kwarg = 'car_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['agence'] = self.object.agence
        context['images'] = self.object.images.all()
        return context

    def form_valid(self, form):
        with transaction.atomic():
            car = form.save()
            
            # Save main image if provided
            main_image = self.request.FILES.get('image')
            if main_image:
                car.images.update(is_main=False)
                CarImages.objects.create(car=car, image=main_image, is_main=True)
                
            # Save gallery images
            gallery_files = self.request.FILES.getlist('gallery')
            for f in gallery_files:
                CarImages.objects.create(car=car, image=f, is_main=False)
                
        messages.success(self.request, "La voiture a été modifiée avec succès.")
        return redirect('car_detail', agence_slug=car.agence.slug, car_id=car.id)

class CarDeleteView(AgenceManagerRequiredMixin, DeleteView):
    model = Car
    template_name = 'app/car_confirm_delete.html'
    pk_url_kwarg = 'car_id'

    def get_success_url(self):
        return reverse_lazy('cars_agence_list', kwargs={'agence_slug': self.object.agence.slug})

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "La voiture a été supprimée.")
        return super().delete(request, *args, **kwargs)

@login_required
@require_POST
def car_image_delete(request, agence_slug, car_id, image_id):
    image = get_object_or_404(CarImages, id=image_id)
    car = image.car
    
    # Permission check
    if not request.user.is_superuser and car.agence.manager != request.user:
        raise PermissionDenied
        
    image.delete()
    messages.success(request, "L'image a été supprimée.")
    return redirect('car_update', agence_slug=agence_slug, car_id=car.id)

@login_required
@require_POST
def car_image_set_main(request, agence_slug, car_id, image_id):
    image = get_object_or_404(CarImages, id=image_id)
    car = image.car
    
    # Permission check
    if not request.user.is_superuser and car.agence.manager != request.user:
        raise PermissionDenied
        
    car.images.update(is_main=False)
    image.is_main = True
    image.save()
    messages.success(request, "Image principale mise à jour.")
    return redirect('car_update', agence_slug=agence_slug, car_id=car.id)

class CarsAgenceListView(ListView):
    model = Car
    template_name = 'app/cars_agence_list.html'
    context_object_name = 'cars'
    ordering = ['-cree_le']

    def get_queryset(self):
        queryset = super().get_queryset().filter(agence__slug=self.kwargs.get('agence_slug'))
        return queryset.select_related('agence').prefetch_related('images')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['agence'] = Agence.objects.get(slug=self.kwargs.get('agence_slug'))
        return context

# =========================================
# WISHLIST VIEWS
# =========================================
class WishlistToggleView(LoginRequiredMixin, View):
    def post(self, request, car_id):
        car = get_object_or_404(Car, id=car_id)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        
        if wishlist.cars.filter(id=car.id).exists():
            wishlist.cars.remove(car)
            status = 'removed'
        else:
            wishlist.cars.add(car)
            status = 'added'
            
        return JsonResponse({
            'status': status,
            'wishlist_count': wishlist.cars.count()
        })

class WishlistListView(LoginRequiredMixin, ListView):
    model = Car
    template_name = 'app/wishlist.html'
    context_object_name = 'cars'
    paginate_by = 12

    def get_queryset(self):
        wishlist, created = Wishlist.objects.get_or_create(user=self.request.user)
        return wishlist.cars.all().select_related('agence').prefetch_related('images')

# =========================================
# DASHBOARD VIEW
# =========================================
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'app/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.is_superuser:
            agences = Agence.objects.all()
        else:
            agences = Agence.objects.filter(manager=user)
            
        cars = Car.objects.filter(agence__in=agences)
        
        # Statistics
        total_cars = cars.count()
        total_views = cars.aggregate(total=Sum('views_count'))['total'] or 0
        
        # Favorites count: count occurrences of these cars in all wishlists
        total_favorites = Wishlist.objects.filter(cars__in=cars).count()
        
        # Promotions count
        total_promotions = cars.filter(
            est_en_promotion=True,
            date_debut_promo__lte=timezone.now().date(),
            date_fin_promo__gte=timezone.now().date()
        ).count()
        
        # Latest cars (10 items)
        latest_cars = cars.select_related('agence').prefetch_related('images')[:10]
        
        # Contact Messages (renamed to avoid shadowing Django's messages framework)
        contact_messages = ContactMessage.objects.filter(agence__in=agences).order_by('-cree_le')
        
        context.update({
            'agences': agences,
            'total_cars': total_cars,
            'total_views': total_views,
            'total_favorites': total_favorites,
            'total_promotions': total_promotions,
            'latest_cars': latest_cars,
            'messages_received': contact_messages,
        })
        return context

# =========================================
# AGENCE PRESENTATION & MEDIA MANAGEMENT
# =========================================
class AgencePresentationManageView(LoginRequiredMixin, TemplateView):
    template_name = 'app/agence_presentation_manage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agence = get_object_or_404(Agence, slug=self.kwargs.get('agence_slug'))
        
        if not self.request.user.is_superuser and agence.manager != self.request.user:
            raise PermissionDenied

        context['agence'] = agence
        context['map_form'] = AgencePresentationForm(instance=agence)
        context['image_form'] = AgenceImageForm()
        context['video_form'] = AgenceVideoForm()
        context['images'] = agence.images.all()
        context['videos'] = agence.videos.all()
        return context

    def post(self, request, *args, **kwargs):
        agence = get_object_or_404(Agence, slug=self.kwargs.get('agence_slug'))
        
        if not self.request.user.is_superuser and agence.manager != self.request.user:
            raise PermissionDenied

        if 'update_map' in request.POST:
            form = AgencePresentationForm(request.POST, request.FILES, instance=agence)
            if form.is_valid():
                form.save()
                messages.success(request, "La localisation a été mise à jour.")
        
        elif 'add_image' in request.POST:
            form = AgenceImageForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.save(commit=False)
                image.agence = agence
                image.save()
                messages.success(request, "Image ajoutée successfully.")
        
        elif 'add_video' in request.POST:
            form = AgenceVideoForm(request.POST, request.FILES)
            if form.is_valid():
                video = form.save(commit=False)
                video.agence = agence
                video.save()
                messages.success(request, "Vidéo ajoutée successfully.")

        return redirect('agence_presentation_manage', agence_slug=agence.slug)

class AgenceImageDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        image = get_object_or_404(AgenceImages, pk=pk)
        agence = image.agence
        if not request.user.is_superuser and agence.manager != request.user:
            raise PermissionDenied
        image.delete()
        messages.success(request, "Image supprimée.")
        return redirect('agence_presentation_manage', agence_slug=agence.slug)

class AgenceVideoDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        video = get_object_or_404(AgenceVideos, pk=pk)
        agence = video.agence
        if not request.user.is_superuser and agence.manager != request.user:
            raise PermissionDenied
        video.delete()
        messages.success(request, "Vidéo supprimée.")
        return redirect('agence_presentation_manage', agence_slug=agence.slug)

class AgencePresentationView(DetailView):
    model = Agence
    template_name = 'app/agence_presentation.html'
    context_object_name = 'agence'

    def get_object(self):
        slug = self.kwargs.get('agence_slug')
        return get_object_or_404(Agence, slug=slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = self.object.images.all()
        context['videos'] = self.object.videos.all()
        return context

class AgenceLocalisationAccesView(DetailView):
    model = Agence
    template_name = 'app/agence_localisation_acces.html'
    context_object_name = 'agence'
    slug_url_kwarg = 'agence_slug'

class AgenceVideoView(DetailView):
    model = Agence
    template_name = 'app/agence_visites_video.html'
    context_object_name = 'agence'
    slug_url_kwarg = 'agence_slug'

    def get_object(self):
        slug = self.kwargs.get('agence_slug')
        return get_object_or_404(Agence, slug=slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['videos'] = self.object.videos.all()
        return context

class AgencePhotosView(DetailView):
    model = Agence
    template_name = 'app/agence_galerie_photos.html'
    context_object_name = 'agence'
    slug_url_kwarg = 'agence_slug'

    def get_object(self):
        slug = self.kwargs.get('agence_slug')
        return get_object_or_404(Agence, slug=slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = self.object.images.all()
        return context

# =========================================
# OTHER VIEWS
# =========================================
class EvenementListView(ListView):
    model = Evenement
    template_name = 'app/evenement_list.html'
    context_object_name = 'evenements'
    ordering = ['-date']

class EvenementDetailView(DetailView):
    model = Evenement
    template_name = 'app/evenement_detail.html'
    context_object_name = 'evenement'

class PromotionListView(ListView):
    model = Promotion
    template_name = 'app/promotion_list.html'
    context_object_name = 'promotions'
    ordering = ['-cree_le']

class ArticleBlogListView(ListView):
    model = ArticleBlog
    template_name = 'app/blog_list.html'
    context_object_name = 'articles'
    ordering = ['-date_publication']

class ArticleBlogDetailView(DetailView):
    model = ArticleBlog
    template_name = 'app/blog_detail.html'
    context_object_name = 'article'

class ContactView(CreateView):
    model = ContactMessage
    form_class = ContactForm
    template_name = 'app/contact.html'
    success_url = reverse_lazy('contact')

    def get_initial(self):
        initial = super().get_initial()
        agence_name = self.request.GET.get('agence')
        if agence_name:
            agence = Agence.objects.filter(nom__iexact=agence_name).first()
            if agence:
                initial['agence'] = agence.id
        return initial

    def form_valid(self, form):
        messages.success(self.request, "Votre message a été envoyé avec succès !")
        return super().form_valid(form)
