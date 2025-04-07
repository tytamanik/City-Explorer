import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import time

# Define your list of cities
cities = ['Paris, France', 'Strasbourg, France', 'Iloilo, Philippines', 'Tokyo, Japon']

# Initialize UserAgent
ua = UserAgent()
user_agent = ua.random

# Setup WebDriver options
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument(f'user-agent={user_agent}')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Initialize a DataFrame to store the results
itinerary_df = pd.DataFrame()

# Start the scraping process
start_time = time.time()


def get_itineraries_for_pair(origin, destination):
    driver.get("https://www.rome2rio.com/fr/")

    # Wait and click 'Gérer vos préférences' for cookies
    try:
        WebDriverWait(driver, 0.1).until(
            EC.element_to_be_clickable((By.XPATH, "//button//p[contains(text(), 'Gérer vos préférences')]"))
        ).click()
    except:
        print("pass")

    # Function to click the correct button ('Confirmer les choix' or 'Enregistrer et fermer')
    def click_confirm_button():
        try:
            WebDriverWait(driver, 0.1).until(
                EC.element_to_be_clickable((By.XPATH, "//button//p[contains(text(), 'Confirmer les choix')]"))
            ).click()
        except:
            WebDriverWait(driver, 0.1).until(
                EC.element_to_be_clickable((By.XPATH, "//button//p[contains(text(), 'Enregistrer et fermer')]"))
            ).click()

    try:
        click_confirm_button()
    except:
        print("pas de cookies")

    # Clear and update the origin and destination fields
    origin_input = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "place-autocomplete-origin"))
    )
    origin_input.clear()
    origin_input.send_keys(origin)

    # Use double quotes to enclose the XPath string
    discover_button = driver.find_element(By.XPATH, "//span[text()=\"Découvrez comment aller n'importe où\"]")
    discover_button.click()

    destination_input = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "place-autocomplete-destination"))
    )
    time.sleep(0.1)  # Wait for the page to process
    destination_input.clear()
    destination_input.send_keys(destination)

    # Click the "Discover how to get anywhere" button
    discover_button = driver.find_element(By.XPATH, "//span[text()=\"Découvrez comment aller n'importe où\"]")
    discover_button.click()

    time.sleep(1)  # Wait for the results to load

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

    # Wait for the itinerary results to be fully loaded
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='trip-search-result-0']"))
    )

    # Function to click on the "Voir x options supplémentaires" button
    def click_show_more(driver):
        load_more_button = WebDriverWait(driver, 0.1).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='show-more-0']"))
        )
        load_more_button.click()
        return True

    try:
        click_show_more(driver)
    except:
        print("Pas d'autres itinéraires")

    # Scraping itinerary details
    itinerary_details = []
    itinerary_items = driver.find_elements(By.CSS_SELECTOR, "div[data-testid^='trip-search-result-']")

    for item in itinerary_items:
        vehicle = item.find_element(By.XPATH, ".//h1[contains(@class, 'sc')]").text
        distance = item.find_element(By.CSS_SELECTOR, "time").text
        price = item.find_element(By.XPATH, ".//span[contains(text(), '€')]").text

        itinerary_details.append({
            'vehicle': vehicle,
            'distance': distance,
            'price': price
        })

    # Extract the itineraries
    itineraries = []
    for itinerary in itinerary_details:
        itineraries.append(
            f"Vehicle: {itinerary['vehicle']} | Distance: {itinerary['distance']} | Price: {itinerary['price']}")

    print(itineraries)

    return itineraries


# Loop through each city pair and get the itineraries
for i, origin in enumerate(cities):
    for j, destination in enumerate(cities):
        if i != j:  # Avoid same city pair (e.g., Paris to Paris)
            print(f"Scraping {origin} to {destination}...")
            itineraries = get_itineraries_for_pair(origin, destination)

            # Ensure the column exists in the DataFrame for each pair
            column_name = f"{origin} to {destination}"
            itinerary_df[column_name] = pd.Series(itineraries)

# Print the DataFrame with results
print(itinerary_df)

# Print time taken
print(f"Total time: {time.time() - start_time:.2f} seconds")

# Close the driver
driver.quit()
