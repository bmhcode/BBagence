# from .views import _get_store
from .models import  Wishlist


# def global_data(request):
#     return {
#         'store': _get_store(),
#         'categories': Category.objects.filter(is_active=True)
#     }
def user_has_agence(request):
    if request.user.is_authenticated:
        return {
            "has_agence": request.user.agences.exists(),
            "first_agence": request.user.agences.first(),
        }
    return {}

def wishlist_context(request):
    wishlist_count = 0
    user_wishlist_ids = []

    if request.user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        wishlist_count = wishlist.cars.count()
        user_wishlist_ids = list(
            wishlist.cars.values_list("id", flat=True)
        )

    return {
        "wishlist_count": wishlist_count,
        "user_wishlist_ids": user_wishlist_ids,
    }

