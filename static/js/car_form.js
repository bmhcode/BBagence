/* ============================================================
   BBCARS — CAR FORM JAVASCRIPT
   (static/js/car_form.js)
   ============================================================ */

document.addEventListener("DOMContentLoaded", function () {
    // 1. Promo toggle
    const promoSwitch = document.getElementById("id_est_en_promotion");
    const promoFields = document.getElementById("promo-fields");
    
    if (promoSwitch && promoFields) {
        function togglePromo() {
            promoFields.style.display = promoSwitch.checked ? "" : "none";
        }
        togglePromo();
        promoSwitch.addEventListener("change", togglePromo);
    }

    // 2. Galerie & SortableJS
    const preview = document.getElementById("preview");
    const imageOrderInput = document.getElementById("image_order");
    const galleryBox = document.getElementById("galleryUploadBox");
    const galleryInput = document.querySelector('#galleryUploadBox input[type="file"]') || 
                         document.getElementById("id_gallery");

    function updateMainBadge() {
        if (!preview) return;
        preview.querySelectorAll(".main-badge").forEach(b => b.remove());
        const firstBox = preview.querySelector(".preview-box");
        if (firstBox) {
            const badge = document.createElement("span");
            badge.className = "main-badge";
            badge.innerHTML = '<i class="fas fa-star text-warning"></i> Principale';
            firstBox.appendChild(badge);
        }
    }

    if (galleryBox && galleryInput) {
        galleryBox.addEventListener("click", function(e) {
            if (e.target !== galleryInput) {
                galleryInput.click();
            }
        });
    }

    if (galleryInput && preview) {
        galleryInput.addEventListener("change", function () {
            const files = Array.from(this.files);
            if (files.length === 0) return;

            // Vider les prévisualisations NOUVELLES (pas celles existantes de la BDD)
            preview.querySelectorAll(".preview-box:not([data-old-image-id])").forEach(b => b.remove());

            files.forEach(file => {
                if (!file.type.startsWith("image/")) return;

                const reader = new FileReader();
                reader.onload = function(e) {
                    const box = document.createElement("div");
                    box.className = "preview-box";

                    const img = document.createElement("img");
                    img.src = e.target.result;
                    img.draggable = false;

                    box.appendChild(img);
                    preview.appendChild(box);
                    updateMainBadge();
                };
                reader.readAsDataURL(file);
            });
        });
    }

    if (preview && typeof Sortable !== 'undefined') {
        Sortable.create(preview, {
            animation: 150,
            ghostClass: "sortable-ghost",
            onEnd: function () { updateMainBadge(); }
        });
    }

    if (preview) {
        // Suppression d'images existantes (BDD uniquement via AJAX)
        preview.addEventListener("click", function(e) {
            if (e.target.closest(".remove-btn")) {
                const box = e.target.closest(".preview-box");
                const oldImageId = box?.dataset.oldImageId;
                const deleteUrlTemplate = preview.dataset.deleteUrlTemplate;

                if (oldImageId && deleteUrlTemplate) {
                    const deleteUrl = deleteUrlTemplate.replace("0", oldImageId);
                    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';

                    fetch(deleteUrl, {
                        method: "POST",
                        headers: {
                            "X-CSRFToken": csrfToken,
                            "X-Requested-With": "XMLHttpRequest"
                        }
                    }).then(() => {
                        box.remove();
                        updateMainBadge();
                    }).catch(err => console.error("Erreur suppression image:", err));
                }
            }
        });
    }

    // 3. Aperçu Vidéo
    const videoInput = document.getElementById("id_video");
    const uploadVideoBox = videoInput ? videoInput.closest("#media")?.querySelector(".upload-video-box") : null;
    
    if (videoInput && uploadVideoBox) {
        videoInput.addEventListener("change", function () {
            const file = this.files[0];
            if (!file || !file.type.startsWith("video/")) return;
            
            const oldPreview = document.querySelector(".new-video-preview");
            if (oldPreview) {
                if (oldPreview.dataset.objectUrl) URL.revokeObjectURL(oldPreview.dataset.objectUrl);
                oldPreview.remove();
            }
            
            const videoUrl = URL.createObjectURL(file);
            const videoPreview = document.createElement("div");
            videoPreview.className = "video-preview new-video-preview mt-4";
            videoPreview.dataset.objectUrl = videoUrl;
            
            videoPreview.innerHTML = `
                <video controls class="w-100">
                    <source src="${videoUrl}" type="${file.type}">
                </video>
                <div class="video-footer">
                    <strong>${file.name}</strong>
                </div>
            `;
            uploadVideoBox.after(videoPreview);
        });
    }

    // 4. Sauvegarde de l'ordre au Submit
    const form = document.getElementById("carForm");
    if (form) {
        form.addEventListener("submit", function() {
            if (preview && imageOrderInput) {
                const order = [];
                preview.querySelectorAll(".preview-box").forEach((box, index) => {
                    const imageId = box.dataset.oldImageId;
                    if (imageId) {
                        order.push({ id: imageId, order: index });
                    }
                });
                imageOrderInput.value = JSON.stringify(order);
            }
        });
    }
});
