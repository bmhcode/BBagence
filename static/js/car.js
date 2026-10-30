/* ============================================================
   BBCARS — CARS & WISHLIST JAVASCRIPT
   (static/js/car.js)
   ============================================================ */

/**
 * Récupère le jeton CSRF depuis les cookies
 */
function getCSRFToken() {
    return document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
}

/**
 * Met à jour le badge du compteur de wishlist dans la navbar
 */
function updateBadge(count) {
    const badge = document.getElementById("wishlist-count");
    if (!badge) return;
    badge.textContent = count;
    if (count > 0) {
        badge.style.display = "flex";
        badge.classList.remove("d-none");
    } else {
        badge.style.display = "none";
        badge.classList.add("d-none");
    }
}

/**
 * Bascule l'état d'un véhicule dans la wishlist (Ajout / Retrait)
 */
async function toggleWishlist(btn, carId) {
    if (!btn || btn.disabled) return;

    const icon = btn.querySelector("i");
    const previousState = btn.classList.contains("active");

    btn.disabled = true;
    btn.classList.add("loading");

    try {
        const response = await fetch(`/wishlist/toggle/${carId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "X-Requested-With": "XMLHttpRequest",
                "Accept": "application/json"
            },
            credentials: "same-origin"
        });

        if (!response.ok) {
            throw new Error(`Erreur HTTP : ${response.status}`);
        }

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.message || "Impossible de modifier les favoris.");
        }

        btn.classList.toggle("active", data.in_wishlist);

        if (icon) {
            icon.classList.toggle("fas", data.in_wishlist);
            icon.classList.toggle("far", !data.in_wishlist);
        }

        const label = data.in_wishlist ? "Retirer des favoris" : "Ajouter aux favoris";
        btn.setAttribute("aria-label", label);
        btn.setAttribute("title", label);
        btn.setAttribute("aria-pressed", data.in_wishlist ? "true" : "false");

        if (data.wishlist_count !== undefined) {
            updateBadge(data.wishlist_count);
        }

        // Si on est sur la page wishlist et qu'un élément est retiré
        const wishlistCard = document.getElementById(`car-${carId}`);
        if (wishlistCard && !data.in_wishlist) {
            wishlistCard.style.transition = "all .3s ease";
            wishlistCard.style.opacity = "0";
            wishlistCard.style.transform = "scale(.9)";
            setTimeout(() => {
                wishlistCard.remove();
                if (data.wishlist_count === 0) {
                    location.reload();
                }
            }, 300);
        }

    } catch (error) {
        console.error("Erreur wishlist :", error);
        btn.classList.toggle("active", previousState);
        if (icon) {
            icon.classList.toggle("fas", previousState);
            icon.classList.toggle("far", !previousState);
        }
    } finally {
        btn.disabled = false;
        btn.classList.remove("loading");
    }
}

/**
 * Changement fluide de l'image principale sur la fiche véhicule
 */
function changeMainImage(image) {
    const mainImage = document.getElementById("mainCarImage");
    if (!mainImage || !image) return;

    mainImage.style.opacity = "0";
    setTimeout(() => {
        mainImage.src = image.src;
        mainImage.style.opacity = "1";
    }, 200);

    document.querySelectorAll(".secondary-car-image").forEach(img => {
        if (img.parentElement) {
            img.parentElement.style.borderColor = "transparent";
        }
    });

    if (image.parentElement) {
        image.parentElement.style.borderColor = "var(--color-pink, #ff4f9a)";
    }
}

/**
 * Ouvrir une image d'agence ou de galerie dans un nouvel onglet
 */
function openAgencyImage(imageUrl) {
    if (!imageUrl) return;
    window.open(imageUrl, '_blank', 'noopener,noreferrer');
}

/**
 * Arrêt automatique des vidéos dans les modales Bootstrap à leur fermeture
 */
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('.modal').forEach(function (modal) {
        modal.addEventListener('hidden.bs.modal', function () {
            const video = modal.querySelector('video');
            if (video) {
                video.pause();
                video.currentTime = 0;
            }
        });
    });

    // Écouteur pour les boutons de retrait direct sur wishlist.html
    document.querySelectorAll('.wishlist-page-remove-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const carId = this.dataset.carId;
            if (carId) {
                toggleWishlist(this, carId);
            }
        });
    });
});
