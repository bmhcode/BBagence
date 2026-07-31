def wishlist_context(request):
    if request.user.is_authenticated:
        try:
            wishlist = request.user.wishlist
            return {
                'wishlist_count': wishlist.cars.count(),
                'user_wishlist_ids': list(wishlist.cars.values_list('id', flat=True))
            }
        except Exception:
            # In case the Wishlist object is not created yet
            return {
                'wishlist_count': 0,
                'user_wishlist_ids': []
            }
    return {
        'wishlist_count': 0,
        'user_wishlist_ids': []
    }
