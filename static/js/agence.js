/* ============================================================
   BBCARS — AGENCE CLIENT JAVASCRIPT
   (static/js/agence.js)
   ============================================================ */

/**
 * Ouvrir la modale d'édition de vidéo avec son action dynamique
 */
function openVideoEditModal(videoId, titre) {
    const form = document.getElementById('editVideoForm');
    const titreInput = document.getElementById('editVideoTitre');
    const modalElement = document.getElementById('editVideoModal');

    if (!form || !modalElement) return;

    const baseAction = form.dataset.editBaseUrl || '';
    if (baseAction) {
        form.action = baseAction.replace('0', videoId);
    }

    if (titreInput) {
        titreInput.value = titre || '';
    }

    if (typeof bootstrap !== 'undefined') {
        const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
        modal.show();
    }
}

document.addEventListener("DOMContentLoaded", function () {
    // ── 1. Upload & Aperçu de plusieurs photos dans l'agence ──
    const photosInput = document.getElementById("photos");
    const photosPreview = document.getElementById("photosPreview");

    if (photosInput && photosPreview) {
        let selectedPhotos = [];

        function renderPreview() {
            photosPreview.innerHTML = "";
            selectedPhotos.forEach(function (photo, index) {
                const file = photo.file;
                if (!file.type.startsWith("image/")) return;

                const reader = new FileReader();
                reader.onload = function (event) {
                    const col = document.createElement("div");
                    col.className = "col-12 col-md-6";
                    col.innerHTML = `
                        <div class="card border-0 shadow-sm h-100">
                            <div class="position-relative">
                                <img src="${event.target.result}"
                                     class="w-100 rounded-top"
                                     style="height:180px; object-fit:cover;"
                                     alt="${file.name}">
                                <button type="button"
                                        class="btn btn-danger btn-sm rounded-circle position-absolute"
                                        style="top:10px; right:10px; width:35px; height:35px; padding:0; z-index:10;"
                                        data-index="${index}"
                                        title="Supprimer cette photo">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                            <div class="card-body">
                                <div class="small text-muted mb-2 text-truncate">
                                    <i class="fas fa-image me-1"></i>
                                    ${file.name}
                                </div>
                                <label class="form-label fw-bold">Légende</label>
                                <input type="text"
                                       class="form-control photo-legende"
                                       value="${escapeHtml(photo.legende)}"
                                       data-index="${index}"
                                       maxlength="200"
                                       placeholder="Légende de cette photo">
                            </div>
                        </div>
                    `;
                    photosPreview.appendChild(col);
                };
                reader.readAsDataURL(file);
            });
        }

        photosInput.addEventListener("change", function () {
            const newFiles = Array.from(this.files);
            selectedPhotos = newFiles.map(file => ({ file: file, legende: "" }));
            renderPreview();
        });

        photosPreview.addEventListener("input", function (event) {
            const inputLegende = event.target.closest(".photo-legende");
            if (!inputLegende) return;
            const index = parseInt(inputLegende.dataset.index);
            if (selectedPhotos[index]) {
                selectedPhotos[index].legende = inputLegende.value;
            }
        });

        photosPreview.addEventListener("click", function (event) {
            const button = event.target.closest("button[data-index]");
            if (!button) return;
            const index = parseInt(button.dataset.index);
            selectedPhotos.splice(index, 1);
            updatePhotosInput();
            renderPreview();
        });

        function updatePhotosInput() {
            if (typeof DataTransfer !== 'undefined') {
                const dt = new DataTransfer();
                selectedPhotos.forEach(p => dt.items.add(p.file));
                photosInput.files = dt.files;
            }
        }

        function escapeHtml(text) {
            const div = document.createElement("div");
            div.textContent = text || "";
            return div.innerHTML;
        }
    }

    // ── 2. Modale de modification d'une photo d'agence ──
    const editPhotoModal = document.getElementById('editPhotoModal');
    const editPhotoForm = document.getElementById('editPhotoForm');
    const editPhotoPreview = document.getElementById('editPhotoPreview');
    const editPhoto = document.getElementById('editPhoto');
    const editLegende = document.getElementById('editLegende');

    if (editPhotoModal && editPhotoForm) {
        editPhotoModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            if (!button) return;

            const imageUrl = button.dataset.imageUrl || '';
            const legende = button.dataset.legende || '';
            const editUrl = button.dataset.editUrl || '';

            if (editPhotoPreview) editPhotoPreview.src = imageUrl;
            if (editLegende) editLegende.value = legende;
            editPhotoForm.action = editUrl;
            if (editPhoto) editPhoto.value = '';
        });

        if (editPhoto && editPhotoPreview) {
            editPhoto.addEventListener('change', function () {
                const file = this.files[0];
                if (!file) return;
                if (!file.type.startsWith('image/')) {
                    alert('Veuillez sélectionner une image valide.');
                    this.value = '';
                    return;
                }
                const reader = new FileReader();
                reader.onload = function (e) {
                    editPhotoPreview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            });
        }

        editPhotoModal.addEventListener('hidden.bs.modal', function () {
            editPhotoForm.reset();
            if (editPhotoPreview) editPhotoPreview.src = '';
            editPhotoForm.action = '';
        });
    }

    // ── 3. Ajout d'une vidéo avec aperçu local ──
    const videoInput = document.getElementById('videoFile');
    const videoPreview = document.getElementById('videoPreview');
    const videoPreviewContainer = document.getElementById('videoPreviewContainer');
    const addVideoModal = document.getElementById('addVideoModal');

    if (videoInput && videoPreview && videoPreviewContainer) {
        videoInput.addEventListener('change', function () {
            const file = this.files[0];
            if (!file) {
                videoPreviewContainer.style.display = 'none';
                videoPreview.removeAttribute('src');
                return;
            }
            if (!file.type.startsWith('video/')) {
                alert('Veuillez sélectionner un fichier vidéo.');
                this.value = '';
                videoPreviewContainer.style.display = 'none';
                return;
            }
            const videoURL = URL.createObjectURL(file);
            videoPreview.src = videoURL;
            videoPreviewContainer.style.display = 'block';
            videoPreview.load();
        });

        if (addVideoModal) {
            addVideoModal.addEventListener('hidden.bs.modal', function () {
                videoPreview.pause();
                videoPreview.removeAttribute('src');
                videoPreview.load();
                videoInput.value = '';
                videoPreviewContainer.style.display = 'none';
                const legende = document.getElementById('videoLegende');
                if (legende) legende.value = '';
            });
        }
    }
});
