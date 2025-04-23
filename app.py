from flask import Flask, render_template, request, jsonify
from api import RecuperateurSitesTouristiques
from scraping import get_itineraries_for_pair

app = Flask(__name__)
recup = RecuperateurSitesTouristiques()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lieux', methods=['POST'])
def lieux():
    ville = request.form.get('ville')
    lieux = recup.obtenir_sites_filtres(ville, [], [], nombre_sites=10, langue='fr')
    return render_template('lieux.html', ville=ville, lieux=lieux)

@app.route('/calcul-itineraire', methods=['POST'])
def calcul_itineraire():
    data = request.get_json()
    lieux = data['lieux']  # Chaque lieu a un nom et une adresse

    adresses = [lieu['adresse'] for lieu in lieux]
    results = []

    for i in range(len(adresses) - 1):
        origine = adresses[i]
        destination = adresses[i + 1]
        trajet = get_itineraries_for_pair(origine, destination)
        results.extend(trajet)

    return jsonify(results)


@app.route('/resultats')
def resultats():
    return render_template('resultats.html')

if __name__ == '__main__':
    app.run(debug=True)
