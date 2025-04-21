from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent
import time

def get_itineraries_for_pair(origin, destination):
    print(f"Scraping {origin} → {destination}...")

    ua = UserAgent()
    options = webdriver.ChromeOptions()
    #options.add_argument("--headless")
    options.add_argument("--lang=fr")
    options.add_argument(f"user-agent={ua.random}")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Aller sur la page
        driver.get("https://www.rome2rio.com/fr/")
        time.sleep(1)

        # Gérer les cookies
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//p[contains(text(), 'Autoriser tout')]"))
            ).click()
        except:
            try:
                WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//p[contains(text(), 'Gérer vos préférences')]"))
                ).click()
                WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//p[contains(text(), 'Confirmer les choix')]"))
                ).click()
            except:
                pass

        # Champ origine
        try:
            origin_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "place-autocomplete-origin"))
            )
            origin_input.clear()
            origin_input.send_keys(origin)

            # Use double quotes to enclose the XPath string
            discover_button = driver.find_element(By.XPATH, "//span[text()=\"Découvrez comment aller n'importe où\"]")
            discover_button.click()
            print("Origine renseignée.")
            
        except Exception as e:
            print("Erreur sur le champ origine :", e)
            driver.save_screenshot("origin_input_error.png")
            return [f"Erreur de saisie de l'origine : {origin}"]

        # Champ destination
        try:
            destination_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "place-autocomplete-destination"))
            )
            destination_input.clear()
            destination_input.send_keys(destination)
            time.sleep(1)  # laisse le temps aux suggestions de se charger

            destination_input.clear()
            destination_input.send_keys(destination)
            print("Destination sélectionnée via autocomplete.")

        except Exception as e:
            print("Erreur sur le champ destination :", e)
            driver.save_screenshot("destination_input_error.png")
            return [f"Erreur de saisie de la destination : {destination}"]

        # Uncheck the checkbox to show the itinerary table if it's already checked
        checkbox = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "s0-1-0-0-17-10-0-5-7-search-partners"))
        )
        if checkbox.is_selected():
            checkbox.click()

        # After updating both locations, click the search button
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a.flex.h-11.items-center.justify-center.rounded-lg.bg-rome2rio-pink"))
        ).click()

        # ⏳ Attente des résultats
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid^='trip-search-result-']"))
            )
        except Exception as e:
            driver.save_screenshot("error_screenshot.png")
            print(f"Erreur de chargement des résultats: {e}")
            return [f"Échec du chargement pour {origin} → {destination}"]

        # ⬇️ Charger plus de résultats si possible
        try:
            load_more_button = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='show-more-0']"))
            )
            load_more_button.click()
        except:
            pass

        # 📋 Extraction des itinéraires
        itinerary_details = []
        itinerary_items = driver.find_elements(By.CSS_SELECTOR, "div[data-testid^='trip-search-result-']")

        for item in itinerary_items:
            try:
                vehicle = item.find_element(By.XPATH, ".//h1[contains(@class, 'sc')]").text
                distance = item.find_element(By.CSS_SELECTOR, "time").text
                price = item.find_element(By.XPATH, ".//span[contains(text(), '€')]").text

                itinerary_details.append({
                    'vehicle': vehicle,
                    'distance': distance,
                    'price': price,
                    'adresse_origine': origin,
                    'adresse_destination': destination
                })
            except:
                continue

        itineraries = []
        for i in itinerary_details:
            itineraries.append(
                f"Adresse: {i['adresse_origine']} → {i['adresse_destination']} | Moyen: {i['vehicle']} | Temps: {i['distance']} | Prix: {i['price']}"
            )

        return itineraries

    finally:
        driver.quit()
