!pip install requests python-dotenv
import requests
import json
import os
from dotenv import load_dotenv
import time

# Chargement des variables d'environnement ou configuration directe de la clé
try:
    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", " key!")
except:
    GROQ_API_KEY = " key! "

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
        self.url_base = "https://api.groq.com/openai/v1/chat/completions"
        self.cache = {}  # Cache pour éviter des requêtes répétées pour la même ville
    
    def obtenir_sites_touristiques(self, ville, nombre_sites=10, langue="français"):
        """
        Obtient les principaux sites touristiques pour une ville
        
        Args:
            ville (str): Le nom de la ville
            nombre_sites (int): Le nombre de sites touristiques à retourner
            langue (str): La langue dans laquelle retourner les résultats
            
        Returns:
            list: Liste de dictionnaires contenant les informations sur les sites touristiques
        """
        # Vérification du cache
        cle_cache = f"{ville}_{nombre_sites}_{langue}"
        if cle_cache in self.cache:
            print(f"Utilisation des données en cache pour {ville}")
            return self.cache[cle_cache]
        
        # Construction du prompt pour Groq
        prompt = f"""
        Veuillez fournir une liste des {nombre_sites} sites touristiques les plus importants de {ville}.
        
        Pour chaque site touristique, incluez:
        1. Le nom
        2. Une brève description (1-2 phrases)  
        3. La catégorie (musée, monument, parc, site historique, site religieux, etc.)
        4. L'adresse (aussi précise que possible)
        
        La réponse doit être en {langue} et au format JSON, comme suit:
        [
            {{
                "nom": "Nom du site",
                "description": "Description brève",
                "categorie": "Catégorie",
                "adresse": "Adresse complète"
            }},
            ...
        ]
        
        Répondez uniquement avec le tableau JSON, sans texte supplémentaire ou markdown.
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
            sites_touristiques = json.loads(contenu)
            
            # Ajout des données dans le cache
            self.cache[cle_cache] = sites_touristiques
            
            return sites_touristiques
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la requête API: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"Erreur lors du décodage JSON: {e}")
            print(f"Contenu reçu: {contenu}")
            return []
        except Exception as e:
            print(f"Erreur inattendue: {e}")
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
            print(f"Les données ont été sauvegardées dans {nom_fichier}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des données: {e}")

    def obtenir_sites_filtres_par_categorie(self, ville, categories, exclusions=None, nombre_sites=20, langue="français"):
        """
        Obtient des sites touristiques filtrés par certaines catégories et exclut d'autres
        
        Args:
            ville (str): Le nom de la ville
            categories (list): La liste des catégories souhaitées
            exclusions (list): La liste des catégories à exclure
            nombre_sites (int): Le nombre total de sites à obtenir
            langue (str): La langue dans laquelle retourner les résultats
            
        Returns:
            list: La liste filtrée des sites touristiques
        """
        # Obtient un plus grand nombre de sites pour avoir de quoi filtrer
        tous_sites = self.obtenir_sites_touristiques(ville, nombre_sites, langue)
        
        # Si aucun filtre d'inclusion ou d'exclusion, retourne tous les sites
        if not categories and not exclusions:
            return tous_sites
            
        sites_filtres = []
        for site in tous_sites:
            # Récupère la catégorie du site (en s'adaptant aux différentes langues)
            categorie_site = site.get("categorie", site.get("category", "")).lower()
            
            # Vérifie si la catégorie est dans les exclusions
            if exclusions and any(exclusion.lower() in categorie_site for exclusion in exclusions):
                continue
                
            # Si des catégories d'inclusion sont spécifiées, vérifie si le site correspond
            if categories:
                if any(categorie.lower() in categorie_site for categorie in categories):
                    sites_filtres.append(site)
            else:
                # Si pas de catégories d'inclusion mais seulement des exclusions, ajoute le site
                sites_filtres.append(site)
                
        return sites_filtres
    
    def extraire_categories_disponibles(self, ville, nombre_sites=20, langue="français"):
        """
        Extrait toutes les catégories disponibles pour une ville
        
        Args:
            ville (str): Le nom de la ville
            nombre_sites (int): Le nombre de sites à analyser
            langue (str): La langue des résultats
            
        Returns:
            list: Liste des catégories uniques disponibles
        """
        tous_sites = self.obtenir_sites_touristiques(ville, nombre_sites, langue)
        
        # Extraction des catégories uniques
        categories = set()
        for site in tous_sites:
            categorie = site.get("categorie", site.get("category", ""))
            if categorie:
                categories.add(categorie)
                
        return sorted(list(categories))


# Exemple d'utilisation
if __name__ == "__main__":
    # Création d'une instance de la classe pour récupérer les sites touristiques
    recuperateur = RecuperateurSitesTouristiques()
    
    # Obtention des sites touristiques pour une ville
    nom_ville = input("Entrez le nom de la ville pour laquelle vous souhaitez des sites touristiques: ")
    nombre_sites = int(input("Combien de sites touristiques souhaitez-vous obtenir? "))
    langue = input("Dans quelle langue souhaitez-vous les résultats (français, anglais, roumain)? ")
    
    print(f"\nRécupération des sites touristiques pour {nom_ville}...")
    sites_touristiques = recuperateur.obtenir_sites_touristiques(nom_ville, nombre_sites, langue)
    
    if sites_touristiques:
        print(f"\nJ'ai trouvé {len(sites_touristiques)} sites touristiques à {nom_ville}:\n")
        for i, site in enumerate(sites_touristiques, 1):
            # Adaptation aux différentes structures de réponse possibles (français ou autre langue)
            nom = site.get('nom', site.get('name', 'Non spécifié'))
            categorie = site.get('categorie', site.get('category', 'Non spécifiée'))
            description = site.get('description', 'Non spécifiée')
            adresse = site.get('adresse', site.get('address', 'Non spécifiée'))
            
            print(f"{i}. {nom} - {categorie}")
            print(f"   {description}")
            print(f"   Adresse: {adresse}")
            print()
        
        # Sauvegarde des données dans un fichier JSON
        recuperateur.sauvegarder_dans_fichier(nom_ville, sites_touristiques)
        
        # Affichage de toutes les catégories disponibles
        categories_disponibles = recuperateur.extraire_categories_disponibles(nom_ville)
        print("\nCatégories de sites touristiques disponibles à", nom_ville, ":")
        for categorie in categories_disponibles:
            print(f"- {categorie}")
        
        # Filtrage par catégorie
        print("\nSouhaitez-vous filtrer les résultats par catégorie? (oui/non)")
        choix_filtre = input().lower()
        if choix_filtre == "oui":
            print("Entrez les catégories souhaitées séparées par des virgules (musée, parc, église, monument, site historique, etc.):")
            categories = [cat.strip() for cat in input().split(",")]
            
            # Ajout du filtre d'exclusion
            print("\nSouhaitez-vous exclure certains types de sites? (oui/non)")
            choix_exclusion = input().lower()
            exclusions = []
            if choix_exclusion == "oui":
                print("Entrez les types de sites que vous ne souhaitez PAS visiter, séparés par des virgules:")
                exclusions = [exc.strip() for exc in input().split(",")]
            
            sites_filtres = recuperateur.obtenir_sites_filtres_par_categorie(nom_ville, categories, exclusions)
            print(f"\nJ'ai trouvé {len(sites_filtres)} sites correspondant à vos critères:")
            
            for i, site in enumerate(sites_filtres, 1):
                nom = site.get('nom', site.get('name', 'Non spécifié'))
                categorie = site.get('categorie', site.get('category', 'Non spécifiée'))
                description = site.get('description', 'Non spécifiée')
                adresse = site.get('adresse', site.get('address', 'Non spécifiée'))
                
                print(f"{i}. {nom} - {categorie}")
                print(f"   {description}")
                print(f"   Adresse: {adresse}")
                print()
    else:
        print(f"Je n'ai pas pu obtenir de sites touristiques pour {nom_ville}.")
