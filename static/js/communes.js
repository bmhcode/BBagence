/* ============================================================
   BBCARS — ALGERIAN WILAYAS & COMMUNES CASCADE
   (static/js/communes.js)
   ============================================================ */

document.addEventListener("DOMContentLoaded", function () {
    const cityNames = [
        'Adrar', 'Chlef', 'Laghouat', 'Oum El Bouaghi', 'Batna', 'Béjaïa',
        'Biskra', 'Béchar', 'Blida', 'Bouira', 'Tamanrasset', 'Tébessa',
        'Tlemcen', 'Tiaret', 'Tizi Ouzou', 'Alger', 'Djelfa', 'Jijel',
        'Sétif', 'Saïda', 'Skikda', 'Sidi Bel Abbès', 'Annaba', 'Guelma',
        'Constantine', 'Médéa', 'Mostaganem', "M'Sila", 'Mascara', 'Ouargla',
        'Oran', 'El Bayadh', 'Illizi', 'Bordj Bou Arreridj', 'Boumerdès',
        'El Tarf', 'Tindouf', 'Tissemsilt', 'El Oued', 'Khenchela',
        'Souk Ahras', 'Tipaza', 'Mila', 'Aïn Defla', 'Naâma',
        'Aïn Témouchent', 'Ghardaïa', 'Relizane', 'Timimoun',
        'Bordj Badji Mokhtar', 'Ouled Djellal', 'Béni Abbès', 'In Salah',
        'In Guezzam', 'Touggourt', 'Djanet', "El M'Ghair", 'El Meniaa'
    ];

    // Trouver soit villeSelect (agence_form), soit citySelect (user_update)
    const citySelect = document.getElementById('id_ville') || 
                       document.getElementById('id_city') ||
                       document.querySelector('[data-commune-city]');

    const communeSelect = document.getElementById('id_commune') ||
                          document.querySelector('[data-commune-target]');

    if (!citySelect || !communeSelect) return;

    // Récupérer la commune pré-sélectionnée depuis un data-attribute s'il existe
    const currentCommune = communeSelect.dataset.currentCommune || 
                           citySelect.dataset.currentCommune || 
                           communeSelect.getAttribute('data-initial') || '';

    // URL du JSON de communes (depuis un attribut data ou chemin par défaut)
    const jsonUrl = citySelect.dataset.jsonUrl || 
                    communeSelect.dataset.jsonUrl || 
                    '/static/js/algeria_communes.json';

    let communesData = [];

    function updateCommunes(selectedCity, preselectedCommune) {
        communeSelect.innerHTML = '<option value="">---------</option>';

        if (!selectedCity) return;

        const cityIndex = cityNames.indexOf(selectedCity);
        if (cityIndex === -1) {
            console.warn("Wilaya introuvable dans la liste :", selectedCity);
            return;
        }

        const cityId = (cityIndex + 1).toString();

        const filtered = communesData.filter(c => String(c.wilaya_id) === cityId);

        filtered.forEach(commune => {
            const option = document.createElement("option");
            option.value = commune.name;
            option.textContent = commune.name;

            if (preselectedCommune && preselectedCommune === commune.name) {
                option.selected = true;
            }

            communeSelect.appendChild(option);
        });
    }

    fetch(jsonUrl)
        .then(res => {
            if (!res.ok) throw new Error("Impossible de charger les communes");
            return res.json();
        })
        .then(data => {
            communesData = data;
            if (citySelect.value) {
                updateCommunes(citySelect.value, currentCommune);
            }
        })
        .catch(err => console.error("Erreur chargement communes :", err));

    citySelect.addEventListener("change", function () {
        updateCommunes(this.value, null);
    });
});
