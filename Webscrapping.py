from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import time

start_time = time.time()

ua = UserAgent()
user_agent = ua.random

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument(f'user-agent={user_agent}')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://www.rome2rio.com/fr/")

# Now handle cookie preferences (click to manage preferences and confirm)
WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button//p[contains(text(), 'Gérer vos préférences')]"))
).click()
print("Clicked on 'Gérer vos préférences'.")

# Function to click the correct button ('Confirmer les choix' or 'Enregistrer et fermer')
def click_confirm_button():
    try:
        # Try to click on 'Confirmer les choix'
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button//p[contains(text(), 'Confirmer les choix')]"))
        ).click()
        print("Clicked on 'Confirmer les choix'.")
    except:
        # If not found, try 'Enregistrer et fermer'
        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button//p[contains(text(), 'Enregistrer et fermer')]"))
        ).click()
        print("Clicked on 'Enregistrer et fermer'.")

click_confirm_button()

# Clear and update the origin field (Strasbourg)
origin_input = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.ID, "place-autocomplete-origin"))
)

origin_input.clear()  # Clear the initial value in the origin field
origin_input.send_keys('Strasbourg, France')

# Click somewhere on the page (e.g., on the body element) to "blur" the inputs and make the website register the updated values
body = driver.find_element(By.TAG_NAME, 'body')
body.click()  # Click somewhere else on the page

# Clear and update the destination field (Paris)
destination_input = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.ID, "place-autocomplete-destination"))
)

# Pause to allow the page to process the changes
time.sleep(0.1)

destination_input.clear()  # Clear the initial value in the destination field
destination_input.send_keys('Paris, France')

# Use double quotes to enclose the XPath string
discover_button = driver.find_element(By.XPATH, "//span[text()=\"Découvrez comment aller n'importe où\"]")
discover_button.click()

# Pause to allow the page to process the changes
time.sleep(1)

# Uncheck the checkbox to show the itinerary table
checkbox = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "s0-1-0-0-17-10-0-5-7-search-partners"))
)
if checkbox.is_selected():  # Uncheck the box if it's already checked
    checkbox.click()

# After updating both locations, click the search button
WebDriverWait(driver, 15).until(
    EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "a.flex.h-11.items-center.justify-center.rounded-lg.bg-rome2rio-pink"))
).click()
print("Clicked on search button.")

# Function to click on the "Voir x options supplémentaires" button
def click_show_more(driver):
    load_more_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='show-more-0']"))
    )
    load_more_button.click()
    return True

# Wait for the itinerary results to be fully loaded
WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='trip-search-result-0']"))
)
click_show_more(driver)

# Scraping itinerary details after clicking 'Voir x options supplémentaires'
itinerary_details = []

# Locate all itinerary sections (vehicles, distance, price)
itinerary_items = driver.find_elements(By.CSS_SELECTOR, "div[data-testid^='trip-search-result-']")

# Scrape the details as before
for item in itinerary_items:
    vehicle = item.find_element(By.XPATH, ".//h1[contains(@class, 'sc')]").text

    # Distance (in minutes)
    distance = item.find_element(By.CSS_SELECTOR, "time").text

    # Attempt to extract price using XPath for specific span with price range
    price = item.find_element(By.XPATH, ".//span[contains(text(), '€')]").text

    itinerary_details.append({
        'vehicle': vehicle,
        'distance': distance,
        'price': price
    })

# Print extracted itinerary details
for idx, itinerary in enumerate(itinerary_details, 1):
    print(f"Itinerary {idx}:")
    print(f"  Vehicle: {itinerary['vehicle']}")
    print(f"  Distance: {itinerary['distance']}")
    print(f"  Price: {itinerary['price']}")
    print("-" * 50)

print(time.time() - start_time)
