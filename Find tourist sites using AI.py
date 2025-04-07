!pip install requests python-dotenv
import requests
import json
import os
from dotenv import load_dotenv
import time

# Chargement des variables d'environnement ou configuration directe de la clé
try:
    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
except:
    GROQ_API_KEY = "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"

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
