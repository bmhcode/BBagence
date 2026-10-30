/* ============================================================
   BBCARS — CAR DETAIL GALLERY MANAGEMENT JAVASCRIPT
   (static/js/car_gallery.js)
   ============================================================ */

let selectedPhotos = [];
let photoIdCounter = 0;

function updatePhotoCounter() {
    const counter = document.getElementById('photoCounter');
    if (counter) {
        counter.textContent = `${selectedPhotos.length} photo(s) sélectionnée(s)`;
    }
}

function removePhoto(id) {
    selectedPhotos = selectedPhotos.filter(p => p.id !== id);
    renderPhotos();
    updatePhotoCounter();
}

function renderPhotos() {
    const container = document.getElementById('previewContainer');
    if (!container) return;
    container.innerHTML = '';

    selectedPhotos.forEach(photo => {
        const reader = new FileReader();
        reader.onload = function(e) {
            const col = document.createElement('div');
            col.className = 'col-md-4 col-lg-3';
            col.dataset.id = photo.id;

            col.innerHTML = `
                <div class="photo-preview-card">
                    <div class="drag-handle" title="Déplacer">
                        <i class="fas fa-grip-vertical"></i>
                    </div>
                    <button type="button" class="remove-photo" onclick="removePhoto(${photo.id})" title="Supprimer">
                        <i class="fas fa-times"></i>
                    </button>
                    <img src="${e.target.result}" class="photo-preview" alt="Aperçu">
                    <div class="mt-2">
                        <label class="form-label small fw-semibold">Légende</label>
                        <input type="text" class="form-control form-control-sm"
                               value="${escapeHtml(photo.legende)}"
                               placeholder="Légende..."
                               oninput="updatePhotoLegende(${photo.id}, this.value)">
                    </div>
                </div>
            `;
            container.appendChild(col);
        };
        reader.readAsDataURL(photo.file);
    });
}

function updatePhotoLegende(id, value) {
    const photo = selectedPhotos.find(p => p.id === id);
    if (photo) photo.legende = value;
}

function escapeHtml(value) {
    const div = document.createElement('div');
    div.textContent = value || '';
    return div.innerHTML;
}

/**
 * Upload des nouvelles photos sélectionnées dans la modale
 */
async function uploadGalleryPhotos() {
    if (selectedPhotos.length === 0) {
        alert('Veuillez sélectionner au moins une photo.');
        return;
    }

    const button = document.getElementById('submitPhotosBtn');
    const modalElement = document.getElementById('addPhotosModal');
    const uploadUrl = modalElement?.dataset.uploadUrl;
    const carId = modalElement?.dataset.carId;

    if (!uploadUrl) {
        console.error("URL d'upload non configurée");
        return;
    }

    if (button) {
        button.disabled = true;
        button.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span> Enregistrement...`;
    }

    const formData = new FormData();
    if (carId) formData.append('car_id', carId);

    selectedPhotos.forEach(photo => {
        formData.append('images', photo.file);
        formData.append('legendes', photo.legende);
    });

    try {
        const response = await fetch(uploadUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            location.reload();
        } else {
            alert(data.error || 'Une erreur est survenue.');
            if (button) {
                button.disabled = false;
                button.innerHTML = `<i class="fas fa-save me-1"></i> Ajouter les photos`;
            }
        }
    } catch (error) {
        console.error("Erreur upload:", error);
        alert("Erreur lors de l'enregistrement.");
        if (button) {
            button.disabled = false;
            button.innerHTML = `<i class="fas fa-save me-1"></i> Ajouter les photos`;
        }
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const galleryInput = document.getElementById('galleryInput');
    if (galleryInput) {
        galleryInput.addEventListener('change', function(event) {
            const files = Array.from(event.target.files);
            files.forEach(file => {
                if (file.type.startsWith('image/')) {
                    const id = photoIdCounter++;
                    selectedPhotos.push({ id: id, file: file, legende: '' });
                }
            });
            renderPhotos();
            updatePhotoCounter();
            this.value = '';
        });
    }

    // SortableJS pour les previews de modale
    const previewContainer = document.getElementById('previewContainer');
    if (previewContainer && typeof Sortable !== 'undefined') {
        Sortable.create(previewContainer, {
            handle: '.drag-handle',
            animation: 150,
            onEnd: function () {
                const newOrder = [];
                previewContainer.querySelectorAll('[data-id]').forEach(el => {
                    const id = parseInt(el.dataset.id);
                    const photo = selectedPhotos.find(p => p.id === id);
                    if (photo) newOrder.push(photo);
                });
                selectedPhotos = newOrder;
            }
        });
    }

    // Modale édition photo existante de voiture
    const editPhotoForm = document.getElementById('editPhotoForm');
    const editPhotoPreview = document.getElementById('editPhotoPreview');
    const editPhotoInput = document.getElementById('editPhoto');
    const editLegende = document.getElementById('editLegende');

    if (editPhotoForm) {
        document.querySelectorAll('.agency-gallery-action.edit').forEach(button => {
            button.addEventListener('click', function () {
                const imageUrl = this.dataset.imageUrl;
                const legende = this.dataset.legende || '';
                const editUrl = this.dataset.editUrl;

                if (editPhotoForm) editPhotoForm.action = editUrl;
                if (editPhotoPreview) editPhotoPreview.src = imageUrl;
                if (editLegende) editLegende.value = legende;
                if (editPhotoInput) editPhotoInput.value = '';
            });
        });

        if (editPhotoInput && editPhotoPreview) {
            editPhotoInput.addEventListener('change', function () {
                const file = this.files[0];
                if (!file) return;
                const reader = new FileReader();
                reader.onload = function (e) {
                    editPhotoPreview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            });
        }

        editPhotoForm.addEventListener('submit', function (event) {
            event.preventDefault();
            const form = this;
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span> Enregistrement...`;
            }

            const formData = new FormData(form);
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const modalElement = document.getElementById('editPhotoModal');
                    if (modalElement && typeof bootstrap !== 'undefined') {
                        const modal = bootstrap.Modal.getInstance(modalElement);
                        if (modal) modal.hide();
                    }
                    setTimeout(() => location.reload(), 300);
                } else {
                    alert(data.error || "Erreur de modification");
                    if (submitButton) {
                        submitButton.disabled = false;
                        submitButton.innerHTML = `<i class="fas fa-save me-2"></i> Enregistrer`;
                    }
                }
            })
            .catch(err => {
                console.error(err);
                alert("Erreur lors de l'enregistrement");
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.innerHTML = `<i class="fas fa-save me-2"></i> Enregistrer`;
                }
            });
        });
    }
});
