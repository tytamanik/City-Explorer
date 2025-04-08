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
        
        
