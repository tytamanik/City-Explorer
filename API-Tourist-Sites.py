!pip install requests python-dotenv
import requests
import json
import os
from dotenv import load_dotenv
import time
import http.cookies as cookies


DEFAULT_API_KEY = " key! "

try:
    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", DEFAULT_API_KEY)
except:
    GROQ_API_KEY = DEFAULT_API_KEY

class RecuperateurSitesTouristiques:
    """
    Classe pour récupérer les sites touristiques d'une ville en utilisant l'API Groq
    """
    
    def __init__(self, cle_api=None):
        """
        Initialise le récupérateur avec la clé API
        
        Args:
            cle_api (str): La clé API pour Groq
        """
        self.cle_api = cle_api or GROQ_API_KEY
        if not self.cle_api:
            self.cle_api = input("Veuillez entrer votre clé API Groq: ")
            
        self.url_base = "https://api.groq.com/openai/v1/chat/completions"
        self.cache = {}  # Cache pour éviter des requêtes répétées pour la même ville
        self.cookies = cookies.SimpleCookie()  # Pour stocker les résultats pour le site web
        self.limite_sites = 20  # Limite maximale de sites touristiques à récupérer
        
        # Liste prédéfinie des catégories de sites touristiques communes
        self.categories_predefinies = {
            "fr": [
                "Édifices et patrimoine religieux",
                "Châteaux et architectures civiles",
                "Sites à caractère militaire et lieux de mémoire",
                "Sites et musées archéologiques",
                "Musées des beaux-arts",
                "Écomusées et musées d'art traditionnel",
                "Muséums et musées d'histoire naturelle",
                "Musées thématiques",
                "Parcs à thèmes",
                "Parcs animaliers",
                "Grottes et sites naturels",
                "Villes et villages pittoresques",
                "Transports touristiques",
                "Parcs, jardins et arboretums",
                "Festivals et événements culturels",
                "Sites industriels et visites techniques",
                "Lieux de divertissement et casinos",
                "Marchés et quartiers commerciaux",
                "Centres historiques",
                "Monuments et sites emblématiques"
            ],
            "en": [
                "Religious buildings and heritage",
                "Castles and remarkable civil architecture",
                "Military sites and memorial places",
                "Archaeological sites and museums",
                "Fine arts museums",
                "Ecomuseums and traditional arts museums",
                "Natural history museums",
                "Thematic museums",
                "Theme parks",
                "Animal parks and zoos",
                "Caves and natural sites",
                "Picturesque towns and villages",
                "Tourist transport and attractions",
                "Parks, gardens and arboretums",
                "Festivals and cultural events",
                "Industrial sites and technical visits",
                "Entertainment venues and casinos",
                "Markets and shopping districts",
                "Historic centers",
                "Monuments and iconic landmarks"
            ],
            "ro": [
                "Edificii și patrimoniu religios",
                "Castele și arhitectură civilă remarcabilă",
                "Situri militare și locuri memoriale",
                "Situri și muzee arheologice",
                "Muzee de artă",
                "Ecomuzee și muzee de artă tradițională",
                "Muzee de istorie naturală",
                "Muzee tematice",
                "Parcuri tematice",
                "Parcuri zoologice",
                "Peșteri și situri naturale",
                "Orașe și sate pitorești",
                "Transport turistic",
                "Parcuri, grădini și arboretumuri",
                "Festivaluri și evenimente culturale",
                "Situri industriale și vizite tehnice",
                "Locuri de divertisment și cazinouri",
                "Piețe și cartiere comerciale",
                "Centre istorice",
                "Monumente și obiective emblematice"
            ]
        }
        
        # Dictionnaire de traduction pour les messages
        self.traductions = {
            "fr": {
                "ville": "Entrez le nom de la ville pour laquelle vous souhaitez des sites touristiques: ",
                "nombre_sites": "Combien de sites touristiques souhaitez-vous obtenir? (max 20): ",
                "recuperation": "Récupération des sites touristiques pour {}...",
                "trouve": "J'ai trouvé {} sites touristiques à {}:",
                "adresse": "Adresse",
                "categories_disponibles": "Catégories de sites touristiques disponibles à {}:",
                "filtrer": "Souhaitez-vous filtrer les résultats par catégorie? (oui/non): ",
                "categories_souhaitees": "Entrez les catégories souhaitées séparées par des virgules\nCatégories disponibles: {}",
                "exclure": "Souhaitez-vous exclure certains types de sites? (oui/non): ",
                "types_exclus": "Entrez les types de sites que vous ne souhaitez PAS visiter, séparés par des virgules\nCatégories disponibles: {}",
                "resultats_filtres": "J'ai trouvé {} sites correspondant à vos critères:",
                "pas_resultats": "Je n'ai pas pu obtenir de sites touristiques pour {}."
            },
            "en": {
                "ville": "Enter the name of the city for which you want tourist sites: ",
                "nombre_sites": "How many tourist sites would you like to get? (max 20): ",
                "recuperation": "Retrieving tourist sites for {}...",
                "trouve": "I found {} tourist sites in {}:",
                "adresse": "Address",
                "categories_disponibles": "Available tourist site categories in {}:",
                "filtrer": "Would you like to filter the results by category? (yes/no): ",
                "categories_souhaitees": "Enter the desired categories separated by commas\nAvailable categories: {}",
                "exclure": "Would you like to exclude certain types of sites? (yes/no): ",
                "types_exclus": "Enter the types of sites you do NOT want to visit, separated by commas\nAvailable categories: {}",
                "resultats_filtres": "I found {} sites matching your criteria:",
                "pas_resultats": "I couldn't get tourist sites for {}."
            },
            "ro": {
                "ville": "Introduceți numele orașului pentru care doriți să obțineți obiective turistice: ",
                "nombre_sites": "Câte obiective turistice doriți să obțineți? (max 20): ",
                "recuperation": "Se recuperează obiectivele turistice pentru {}...",
                "trouve": "Am găsit {} obiective turistice în {}:",
                "adresse": "Adresă",
                "categories_disponibles": "Categorii de obiective turistice disponibile în {}:",
                "filtrer": "Doriți să filtrați rezultatele după categorie? (da/nu): ",
                "categories_souhaitees": "Introduceți categoriile dorite separate prin virgulă\nCategorii disponibile: {}",
                "exclure": "Doriți să excludeți anumite tipuri de obiective? (da/nu): ",
                "types_exclus": "Introduceți tipurile de obiective pe care NU doriți să le vizitați, separate prin virgulă\nCategorii disponibile: {}",
                "resultats_filtres": "Am găsit {} obiective care corespund criteriilor dvs.:",
                "pas_resultats": "Nu am putut obține obiective turistice pentru {}."
            }
        }
    
    def traduire(self, cle, langue, *args):
        """
        Traduit un message selon la langue choisie
        
        Args:
            cle (str): La clé du message à traduire
            langue (str): Le code de langue (fr, en, ro)
            *args: Arguments pour le formatage du message
            
        Returns:
            str: Le message traduit
        """
        if langue in self.traductions and cle in self.traductions[langue]:
            return self.traductions[langue][cle].format(*args)
        # Fallback sur le français si la traduction n'existe pas
        return self.traductions["fr"][cle].format(*args)
    
    def obtenir_categories_disponibles(self, ville, langue="fr"):
        """
        Retourne la liste prédéfinie des catégories de sites touristiques
        
        Args:
            ville (str): Le nom de la ville (non utilisé dans cette version)
            langue (str): La langue dans laquelle retourner les résultats
            
        Returns:
            list: Liste des catégories de sites touristiques disponibles
        """
        # Retourne la liste prédéfinie des catégories selon la langue
        return self.categories_predefinies.get(langue, self.categories_predefinies["fr"])
    
    def obtenir_sites_filtres(self, ville, categories_souhaitees, categories_exclues, nombre_sites=10, langue="fr"):
        """
        Fait une requête API pour obtenir des sites touristiques selon les préférences de l'utilisateur
        
        Args:
            ville (str): Le nom de la ville
            categories_souhaitees (list): Liste des catégories souhaitées
            categories_exclues (list): Liste des catégories à exclure
            nombre_sites (int): Le nombre de sites à retourner
            langue (str): La langue des résultats
            
        Returns:
            list: Liste des sites touristiques correspondant aux critères
        """
        # Vérification de la limite maximum
        nombre_sites = min(nombre_sites, self.limite_sites)
        
        # Mappages de langue pour l'API
        mapping_langue = {
            "fr": "français",
            "en": "anglais",
            "ro": "roumain"
        }
        langue_complete = mapping_langue.get(langue, "français")
        
        # Construction du prompt pour Groq avec les préférences utilisateur
        prompt = f"""
        Veuillez fournir une liste des {nombre_sites} sites touristiques les plus importants de {ville} qui correspondent aux critères suivants:
        
        """
        
        if categories_souhaitees:
            prompt += f"""
        Sites touristiques à inclure (catégories): {', '.join(categories_souhaitees)}
        """
        
        if categories_exclues:
            prompt += f"""
        Sites touristiques à exclure (catégories): {', '.join(categories_exclues)}
        """
        
        prompt += f"""
        Pour chaque site touristique, incluez:
        1. Le nom
        2. Une brève description (1-2 phrases)  
        3. La catégorie (une des catégories mentionnées ci-dessus)
        4. L'adresse (aussi précise que possible)
        
        La réponse doit être en {langue_complete} et au format JSON, comme suit:
        [
            {{
                "nom": "Nom du site",
                "description": "Description brève",
                "categorie": "Catégorie",
                "adresse": "Adresse complète"
            }},
            ...
        ]
        
        Ne mettez AUCUN TEXTE supplémentaire avant ou après le JSON, juste le tableau JSON lui-même.
        """
        
        # Préparation de la requête API
        en_tetes = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.cle_api}"
        }
        charge_utile = {
            "model": "llama3-70b-8192",  # Utilisation du modèle Llama 3 70B de Groq
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,
            "max_tokens": 2048
        }
        
        try:
            # Envoi de la requête à l'API
            reponse = requests.post(self.url_base, headers=en_tetes, json=charge_utile)
            reponse.raise_for_status()  # Lève une exception pour les erreurs HTTP
            
            # Analyse de la réponse
            resultat = reponse.json()
            
            # Extraction du contenu de la réponse
            contenu = resultat['choices'][0]['message']['content']
            
            # Nettoyage du contenu pour obtenir uniquement le JSON
            contenu = contenu.strip()
            if contenu.startswith('```json'):
                contenu = contenu[7:]
            if contenu.endswith('```'):
                contenu = contenu[:-3]
            contenu = contenu.strip()
            
            # Analyse du JSON
            try:
                sites_touristiques = json.loads(contenu)
                
                # Limitation du nombre de sites selon la limite configurée
                sites_touristiques = sites_touristiques[:self.limite_sites]
                
                # Sauvegarde dans les cookies pour usage web futur
                self.sauvegarder_dans_cookie(ville, sites_touristiques, langue)
                
                # Sauvegarde dans un fichier local
                self.sauvegarder_dans_fichier(ville, sites_touristiques)
                
                return sites_touristiques
            except json.JSONDecodeError as e:
                print(f"Erreur lors du décodage JSON: {e}")
                print(f"Contenu reçu: {contenu}")
                
                # Tentative de correction du JSON mal formaté
                try:
                    # Suppression de caractères non-JSON potentiels au début et à la fin
                    while not (contenu.startswith('[') and contenu.endswith(']')):
                        if not contenu.startswith('['):
                            contenu = contenu[contenu.find('['):]
                        if not contenu.endswith(']'):
                            contenu = contenu[:contenu.rfind(']')+1]
                    
                    sites_touristiques = json.loads(contenu)
                    return sites_touristiques[:self.limite_sites]
                except (json.JSONDecodeError, ValueError) as e2:
                    print(f"Impossible de corriger le JSON: {e2}")
                    return []
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la requête API pour les sites filtrés: {e}")
            return []
        except Exception as e:
            print(f"Erreur inattendue lors de l'obtention des sites filtrés: {e}")
            return []
    
    def sauvegarder_dans_fichier(self, ville, sites, nom_fichier=None):
        """
        Sauvegarde les sites touristiques dans un fichier JSON
        
        Args:
            ville (str): Le nom de la ville
            sites (list): La liste des sites touristiques
            nom_fichier (str, optional): Le nom du fichier
        """
        if not nom_fichier:
            nom_fichier = f"{ville.lower().replace(' ', '_')}_sites_touristiques.json"
        
        try:
            with open(nom_fichier, 'w', encoding='utf-8') as f:
                json.dump(sites, f, ensure_ascii=False, indent=4)
            # Am eliminat mesajul de salvare pentru a păstra interfața curată
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des données: {e}")
            
    def sauvegarder_dans_cookie(self, ville, sites, langue):
        """
        Sauvegarde les sites touristiques dans un cookie pour usage web futur
        
        Args:
            ville (str): Le nom de la ville
            sites (list): La liste des sites touristiques
            langue (str): La langue des données
        """
        try:
            # Création d'un identifiant unique pour cette ville et langue
            cookie_id = f"sites_{ville.lower().replace(' ', '_')}_{langue}"
            
            # Sérialisation des données (limité à une taille raisonnable pour un cookie)
            data_json = json.dumps(sites, ensure_ascii=False)
            
            # Création du cookie qui expire dans 30 jours
            self.cookies[cookie_id] = data_json
            self.cookies[cookie_id]["path"] = "/"
            self.cookies[cookie_id]["max-age"] = 30 * 24 * 60 * 60  # 30 jours
            self.cookies[cookie_id]["secure"] = True
            self.cookies[cookie_id]["httponly"] = True
            self.cookies[cookie_id]["samesite"] = "Strict"
            
            # Pour usage web, cette méthode renverrait le cookie pour être défini dans la réponse HTTP
            # Dans ce cas, nous stockons simplement le cookie pour une démonstration
        except Exception as e:
            print(f"Erreur lors de la sauvegarde dans le cookie: {e}")
    
    def adapter_reponse_oui_non(self, reponse, langue):
        """
        Adapte la réponse oui/non à la langue
        
        Args:
            reponse (str): La réponse saisie par l'utilisateur
            langue (str): La langue utilisée
            
        Returns:
            bool: True si la réponse est positive, False sinon
        """
        reponse = reponse.lower().strip()
        
        # Réponses positives dans chaque langue spécifique
        positif = {
            "fr": ["oui", "o", "y", "yes"],
            "en": ["yes", "y", "oui", "yep", "yeah"],
            "ro": ["da", "d", "y", "yes"]
        }
        
        return reponse in positif.get(langue, positif["fr"])

    def afficher_resultats(self, sites, langue):
        """
        Affiche les résultats des sites touristiques
        
        Args:
            sites (list): La liste des sites touristiques
            langue (str): La langue d'affichage
        """
        # Mappages des clés selon la langue
        cle_nom = "nom" if langue == "fr" else ("name" if langue == "en" else "nume")
        cle_categorie = "categorie" if langue == "fr" else ("category" if langue == "en" else "categorie")
        cle_description = "description"
        cle_adresse = "adresse" if langue == "fr" else ("address" if langue == "en" else "adresa")
        
        for i, site in enumerate(sites, 1):
            nom = site.get(cle_nom, site.get("nom", ""))
            categorie = site.get(cle_categorie, site.get("categorie", ""))
            description = site.get(cle_description, "")
            adresse = site.get(cle_adresse, site.get("adresse", ""))
            
            print(f"{i}. {nom} - {categorie}")
            print(f"   {description}")
            print(f"   {self.traduire('adresse', langue)}: {adresse}")
            print()


# Exemple d'utilisation
def main():
    # Création d'une instance
    recuperateur = RecuperateurSitesTouristiques()
    
    # Sélection de la langue
    print("Choisissez la langue / Choose the language / Alegeți limba:")
    print("Fr (Français) / En (English) / Ro (Română)")
    langue_input = input().lower().strip()
    
    # Conversion de l'entrée en code de langue standard
    if langue_input.startswith("fr"):
        langue = "fr"
    elif langue_input.startswith("en"):
        langue = "en"
    elif langue_input.startswith("ro"):
        langue = "ro"
    else:
        # Par défaut, français
        langue = "fr"
    
    # Obtention des sites touristiques pour une ville
    ville = input(recuperateur.traduire("ville", langue))
    
    nombre_sites_input = input(recuperateur.traduire("nombre_sites", langue))
    try:
        nombre_sites = min(int(nombre_sites_input), recuperateur.limite_sites)
    except ValueError:
        nombre_sites = 10  # Valeur par défaut
    
    print(recuperateur.traduire("recuperation", langue, ville))
    
    # Utilisation des catégories prédéfinies au lieu de faire une requête API
    categories_disponibles = recuperateur.obtenir_categories_disponibles(ville, langue)
    
    if categories_disponibles:
        print(recuperateur.traduire("categories_disponibles", langue, ville))
        for categorie in categories_disponibles:
            print(f"- {categorie}")
        
        print()
        # Variables pour stocker les préférences utilisateur
        categories_souhaitees = []
        categories_exclues = []
        
        # Demande des catégories souhaitées
        reponse_filtre = input(recuperateur.traduire("filtrer", langue))
        if recuperateur.adapter_reponse_oui_non(reponse_filtre, langue):
            categories_str = ", ".join(categories_disponibles)
            print(recuperateur.traduire("categories_souhaitees", langue, categories_str))
            categories_input = input()
            categories_souhaitees = [cat.strip() for cat in categories_input.split(",")] if categories_input.strip() else []
            
            # Filtrer les catégories disponibles pour l'exclusion en enlevant celles déjà choisies
            categories_restantes = [cat for cat in categories_disponibles if cat not in categories_souhaitees]
            
            # Demande des catégories à exclure parmi celles qui restent
            if categories_restantes:  # Vérifier s'il reste des catégories à exclure
                reponse_exclusion = input(recuperateur.traduire("exclure", langue))
                if recuperateur.adapter_reponse_oui_non(reponse_exclusion, langue):
                    categories_restantes_str = ", ".join(categories_restantes)
                    print(recuperateur.traduire("types_exclus", langue, categories_restantes_str))
                    exclusions_input = input()
                    categories_exclues = [exc.strip() for exc in exclusions_input.split(",")] if exclusions_input.strip() else []
        
        # Requête API avec les préférences utilisateur
        sites_touristiques = recuperateur.obtenir_sites_filtres(
            ville, 
            categories_souhaitees, 
            categories_exclues, 
            nombre_sites, 
            langue
        )
        
        if sites_touristiques:
            print(recuperateur.traduire("resultats_filtres", langue, len(sites_touristiques)))
            recuperateur.afficher_resultats(sites_touristiques, langue)
        else:
            print(recuperateur.traduire("pas_resultats", langue, ville))
    else:
        print(recuperateur.traduire("pas_resultats", langue, ville))

if __name__ == "__main__":
    main()
