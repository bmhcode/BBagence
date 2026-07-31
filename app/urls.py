from django.urls import path
from . import views

urlpatterns = [

    path('', views.HomeView.as_view(), name='home'),


    # =========================== Agences =================================
    path('agences/', views.AgenceListView.as_view(), name='agence_list'),
    path('agence/<slug:agence_slug>/', views.AgenceDetailView.as_view(), name='agence_detail'),
    
    path('agence/<slug:agence_slug>/car/<int:car_id>/', views.CarDetailView.as_view(), name='car_detail'),
    path('agence/<slug:agence_slug>/cars/', views.CarsAgenceListView.as_view(), name='cars_agence_list'),

    # car images (AJAX / Actions)
    path('agence/<slug:agence_slug>/car/<int:car_id>/car-image/<int:image_id>/delete/', views.car_image_delete, name='car_image_delete'),
    path('agence/<slug:agence_slug>/car/<int:car_id>/car-image/<int:image_id>/set-main/', views.car_image_set_main, name='car_image_set_main'),

    path('agence/<slug:agence_slug>/car/create/', views.CarCreateView.as_view(), name='car_create'),




    # Agence Presentation Manage
    path('agence/<slug:agence_slug>/presentation/manage/', views.AgencePresentationManageView.as_view(), name='agence_presentation_manage'),
    path('agence/image/<int:pk>/delete/', views.AgenceImageDeleteView.as_view(), name='agence_image_delete'),
    path('agence/video/<int:pk>/delete/', views.AgenceVideoDeleteView.as_view(), name='agence_video_delete'),
    path('agence/<slug:agence_slug>/presentation/', views.AgencePresentationView.as_view(), name='agence_presentation'),
    path('agence/<slug:agence_slug>/localisation-acces/', views.AgenceLocalisationAccesView.as_view(), name='agence_localisation_acces'),
    path('agence/<slug:agence_slug>/video/', views.AgenceVideoView.as_view(), name='agence_video'),
    path('agence/<slug:agence_slug>/photos/', views.AgencePhotosView.as_view(), name='agence_photos'),

    
    path('evenements/', views.EvenementListView.as_view(), name='evenement_list'),
    path('evenement/<slug:slug>/', views.EvenementDetailView.as_view(), name='evenement_detail'),
    path('promotions/', views.PromotionListView.as_view(), name='promotion_list'),
    path('blog/', views.ArticleBlogListView.as_view(), name='blog_list'),
    path('blog/<slug:slug>/', views.ArticleBlogDetailView.as_view(), name='blog_detail'),
    path('contact/', views.ContactView.as_view(), name='contact'),

]
