from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),

    # =========================== Authentication ==========================
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('profile/', views.UserProfileUpdateView.as_view(), name='profile'),
    
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change_form.html'), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # =========================== Dashboard ===============================
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # =========================== Wishlist ================================
    path('wishlist/', views.WishlistListView.as_view(), name='wishlist_list'),
    path('wishlist/toggle/<int:car_id>/', views.WishlistToggleView.as_view(), name='wishlist_toggle'),

    # =========================== Agences CRUD =============================
    path('agences/', views.AgenceListView.as_view(), name='agence_list'),
    path('agence/create/', views.AgenceCreateView.as_view(), name='agence_create'),
    path('agence/<slug:agence_slug>/', views.AgenceDetailView.as_view(), name='agence_detail'),
    path('agence/<slug:agence_slug>/edit/', views.AgenceUpdateView.as_view(), name='agence_update'),
    path('agence/<slug:agence_slug>/delete/', views.AgenceDeleteView.as_view(), name='agence_delete'),

    # =========================== Cars CRUD ================================
    path('cars/', views.CarListView.as_view(), name='car_list'),
    path('agence/<slug:agence_slug>/car/create/', views.CarCreateView.as_view(), name='car_create'),
    path('agence/<slug:agence_slug>/car/<int:car_id>/', views.CarDetailView.as_view(), name='car_detail'),
    path('agence/<slug:agence_slug>/car/<int:car_id>/edit/', views.CarUpdateView.as_view(), name='car_update'),
    path('agence/<slug:agence_slug>/car/<int:car_id>/delete/', views.CarDeleteView.as_view(), name='car_delete'),
    path('agence/<slug:agence_slug>/cars/', views.CarsAgenceListView.as_view(), name='cars_agence_list'),

    # Car images (AJAX / Actions)
    path('agence/<slug:agence_slug>/car/<int:car_id>/car-image/<int:image_id>/delete/', views.car_image_delete, name='car_image_delete'),
    path('agence/<slug:agence_slug>/car/<int:car_id>/car-image/<int:image_id>/set-main/', views.car_image_set_main, name='car_image_set_main'),

    # =========================== Agence Media Manage ======================
    path('agence/<slug:agence_slug>/presentation/manage/', views.AgencePresentationManageView.as_view(), name='agence_presentation_manage'),
    path('agence/image/<int:pk>/delete/', views.AgenceImageDeleteView.as_view(), name='agence_image_delete'),
    path('agence/video/<int:pk>/delete/', views.AgenceVideoDeleteView.as_view(), name='agence_video_delete'),
    path('agence/<slug:agence_slug>/presentation/', views.AgencePresentationView.as_view(), name='agence_presentation'),
    path('agence/<slug:agence_slug>/localisation-acces/', views.AgenceLocalisationAccesView.as_view(), name='agence_localisation_acces'),
    path('agence/<slug:agence_slug>/video/', views.AgenceVideoView.as_view(), name='agence_video'),
    path('agence/<slug:agence_slug>/photos/', views.AgencePhotosView.as_view(), name='agence_photos'),

    # =========================== Events, Promotions, Blog, Contact ========
    path('evenements/', views.EvenementListView.as_view(), name='evenement_list'),
    path('evenement/<slug:slug>/', views.EvenementDetailView.as_view(), name='evenement_detail'),
    path('promotions/', views.PromotionListView.as_view(), name='promotion_list'),
    path('blog/', views.ArticleBlogListView.as_view(), name='blog_list'),
    path('blog/<slug:slug>/', views.ArticleBlogDetailView.as_view(), name='blog_detail'),
    path('contact/', views.ContactView.as_view(), name='contact'),
]
