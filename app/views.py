from django.template import context
from django.shortcuts import render, redirect, get_object_or_404

from django.views.generic import ListView, DetailView, TemplateView, CreateView
from django.db.models import Q
from .models import Agence, AgenceImages, AgenceVideos, Car,  Evenement, Promotion, ArticleBlog, ContactMessage
from .forms import ContactForm, AgencePresentationForm, AgenceImageForm, AgenceVideoForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.decorators.http import require_POST 
from django.contrib.auth.decorators import login_required, user_passes_test

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views import View


class HomeView(TemplateView):
    template_name = 'app/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['agences_vedette'] = Agence.objects.filter(est_en_vedette=True)[:6]
        context['evenements_prochains'] = Evenement.objects.all().order_by('date')[:3]
        context['promotions_actives'] = Promotion.objects.all().order_by('-cree_le')[:3]
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
        context['noms'] = Agence.nom
        context["villes"] = (Agence.objects.values_list("ville", flat=True).distinct().order_by("ville"))
        return context

class AgenceDetailView(DetailView):
    model = Agence
    template_name = 'app/agence_detail.html'
    context_object_name = 'agence'
    slug_url_kwarg = 'agence_slug'


# ================== Start agence views ================== 
class AgencePresentationManageView(LoginRequiredMixin, TemplateView):
    template_name = 'app/agence_presentation_manage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agence = get_object_or_404(Agence, slug=self.kwargs.get('agence_slug'))
        
        # Security check
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
        
        # Security check
        if not self.request.user.is_superuser and agence.manager != self.request.user:
            raise PermissionDenied

        if 'update_map' in request.POST:
            form = AgencePresentationForm(request.POST, request.FILES, instance=agence)
            if form.is_valid():
                form.save()
                messages.success(request, "Map updated successfully.")
        
        elif 'add_image' in request.POST:
            form = AgenceImageForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.save(commit=False)
                image.agence = agence
                image.save()
                messages.success(request, "Image added successfully.")
        
        elif 'add_video' in request.POST:
            form = AgenceVideoForm(request.POST, request.FILES)
            if form.is_valid():
                video = form.save(commit=False)
                video.agence = agence
                video.save()
                messages.success(request, "Video added successfully.")

        return redirect('agence_presentation_manage', agence_slug=agence.slug)
class AgenceImageDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        image = get_object_or_404(AgenceImages, pk=pk)
        agence = image.agence
        if not request.user.is_superuser and agence.manager != request.user:
            raise PermissionDenied
        image.delete()
        messages.success(request, "Image deleted.")
        return redirect('agence_presentation_manage', agence_slug=agence.slug)

class AgenceVideoDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        video = get_object_or_404(AgenceVideos, pk=pk)
        agence = video.agence
        if not request.user.is_superuser and agence.manager != request.user:
            raise PermissionDenied
        video.delete()
        messages.success(request, "Video deleted.")
        return redirect('agence_presentation_manage', agence_slug=agence.slug)




# ================== Start car views ================== 
class CarDetailView(DetailView):
    model = Car
    template_name = 'app/car_detail.html'
    context_object_name = 'car'
    pk_url_kwarg = 'car_id'
    slug_url_kwarg = 'agence_slug'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('agence')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cars_related'] = Car.objects.filter(agence=self.object.agence).exclude(pk=self.object.pk)[:4]
        return context

@require_POST # Delete car image
def car_image_delete(request, agence_slug, car_id, image_id):
    image = get_object_or_404(CarImages, id=image_id)
    car = image.car
    image.delete()
    return redirect('car_detail', agence_slug=agence_slug, car_id=car.id)

@login_required
@require_POST # product image set main
def car_image_set_main(request, agence_slug, car_id, image_id):
    image = get_object_or_404(CarImages, id=image_id)
    car = image.car
    car.images.update(is_main=False)
    image.is_main = True
    image.save()
    return redirect('car_detail', agence_slug=agence_slug, car_id=car.id)







# ================== End car views ================== 


# ================== Start evenement views ================== 
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

    def form_valid(self, form):
        messages.success(self.request, "Votre message a été envoyé avec succès !")
        return super().form_valid(form)
