document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('ville');
    const suggestionsBox = document.getElementById('suggestions');

    const villesDisponibles = [
        "Paris, France",
        "Lyon, France",
        "Strasbourg, France",
        "Marseille, France",
        "Tokyo, Japon",
        "Iloilo, Philippines",
        "New York, USA",
        "Lisbonne, Portugal",
        "Barcelone, Espagne",
        "Rome, Italie"
    ];

    input.addEventListener('input', () => {
        const query = input.value.toLowerCase();
        suggestionsBox.innerHTML = '';
        if (query.length === 0) return;

        const filtered = villesDisponibles.filter(ville => ville.toLowerCase().includes(query));

        filtered.slice(0, 5).forEach(ville => {
            const div = document.createElement('div');
            div.classList.add('suggestion-item');
            div.textContent = ville;
            div.addEventListener('click', () => {
                input.value = ville;
                suggestionsBox.innerHTML = '';
            });
            suggestionsBox.appendChild(div);
        });
    });

    document.addEventListener('click', (e) => {
        if (!suggestionsBox.contains(e.target) && e.target !== input) {
            suggestionsBox.innerHTML = '';
        }
    });
});
