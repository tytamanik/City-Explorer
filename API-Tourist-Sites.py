!pip install requests python-dotenv
import requests
import json
import os
from dotenv import load_dotenv
import time

# Chargement des variables d'environnement ou configuration directe de la clé
try:
    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", " key! ")
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
        self.cache = {}  
    
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
            "model": "llama3-70b-8192",  
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

    def obtenir_sites_filtres_par_categorie(self, ville, categories, nombre_sites=20, langue="français"):
        """
        Obtient des sites touristiques filtrés par certaines catégories

        Args:
            ville (str): Le nom de la ville
            categories (list): La liste des catégories souhaitées
            nombre_sites (int): Le nombre total de sites à obtenir
            langue (str): La langue dans laquelle retourner les résultats
            
