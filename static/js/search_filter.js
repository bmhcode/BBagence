/* ============================================================
   BBCARS — REALTIME SEARCH & FILTER
   (static/js/search_filter.js)
   ============================================================ */

document.addEventListener("DOMContentLoaded", function () {
    // ── 1. Recherche par ville / nom dans agence_list ──
    const searchInput = document.getElementById("citySearch");
    const clearButton = document.getElementById("clearSearch");
    const cards = document.querySelectorAll(".agence-card");

    if (searchInput && cards.length) {
        function normalizeText(text) {
            return (text || "")
                .toString()
                .toLowerCase()
                .normalize("NFD")
                .replace(/[\u0300-\u036f]/g, "")
                .trim();
        }

        function filterAgences() {
            const value = normalizeText(searchInput.value);
            cards.forEach(function (card) {
                const city = normalizeText(card.dataset.city);
                const name = normalizeText(card.dataset.name);
                const owner = normalizeText(card.dataset.owner);

                const matches = value === "" ||
                    city.includes(value) ||
                    name.includes(value) ||
                    owner.includes(value);

                card.style.display = matches ? "" : "none";
            });

            if (clearButton) {
                if (searchInput.value.trim() !== "") {
                    clearButton.classList.remove("d-none");
                } else {
                    clearButton.classList.add("d-none");
                }
            }
        }

        searchInput.addEventListener("input", filterAgences);

        if (clearButton) {
            clearButton.addEventListener("click", function () {
                searchInput.value = "";
                filterAgences();
                searchInput.focus();
            });
        }
    }

    // ── 2. Recherche dans le tableau agence_admin_list ──
    const agencySearch = document.getElementById('agencySearch');
    const rows = document.querySelectorAll('.agency-row');
    const noResults = document.getElementById('noSearchResults');

    if (agencySearch && rows.length) {
        agencySearch.addEventListener('input', function () {
            const query = this.value.trim().toLocaleLowerCase();
            let visibleCount = 0;

            rows.forEach(function (row) {
                const matches = row.textContent.toLocaleLowerCase().includes(query);
                row.style.display = matches ? '' : 'none';
                if (matches) visibleCount++;
            });

            if (noResults) {
                noResults.style.display = rows.length > 0 && visibleCount === 0 ? '' : 'none';
            }
        });
    }

    // ── 3. Toggle mot de passe (login / registration) ──
    const togglePassword = document.getElementById("togglePassword");
    const passwordInput = document.getElementById("id_password") || 
                          document.querySelector('input[type="password"]');

    if (togglePassword && passwordInput) {
        togglePassword.addEventListener("click", function () {
            const icon = this.querySelector("i");
            if (passwordInput.type === "password") {
                passwordInput.type = "text";
                if (icon) {
                    icon.classList.remove("fa-eye");
                    icon.classList.add("fa-eye-slash");
                }
            } else {
                passwordInput.type = "password";
                if (icon) {
                    icon.classList.remove("fa-eye-slash");
                    icon.classList.add("fa-eye");
                }
            }
        });
    }
});
