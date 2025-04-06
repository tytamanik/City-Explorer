from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import time

ua = UserAgent()
user_agent = ua.random

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument(f'user-agent={user_agent}')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://www.rome2rio.com/fr/")

# Now handle cookie preferences (click to manage preferences and confirm)
try:
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button//p[contains(text(), 'Gérer vos préférences')]"))
    ).click()
    print("Clicked on 'Gérer vos préférences'.")
except:
    print("No 'Gérer vos préférences' button appeared, continuing...")

try:
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button//p[contains(text(), 'Confirmer les choix')]"))
    ).click()
    print("Clicked on 'Confirmer les choix'.")
except:
    print("No 'Confirmer les choix' button appeared, continuing...")

# Clear and update the origin field (Strasbourg)
origin_input = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.ID, "place-autocomplete-origin"))
)

origin_input.clear()  # Clear the initial value in the origin field
origin_input.send_keys('Strasbourg, France')

# Click somewhere on the page (e.g., on the body element) to "blur" the inputs and make the website register the updated values
body = driver.find_element(By.TAG_NAME, 'body')
body.click()  # Click somewhere else on the page

# Pause to allow the page to process the changes
time.sleep(0.01)

# Clear and update the destination field (Paris)
destination_input = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.ID, "place-autocomplete-destination"))
)
destination_input.clear()  # Clear the initial value in the destination field
destination_input.send_keys('Paris, France')

time.sleep(0.01)

# Click somewhere on the page (e.g., on the body element) to "blur" the inputs and make the website register the updated values
body = driver.find_element(By.TAG_NAME, 'body')
body.click()  # Click somewhere else on the page


# Pause to allow the page to process the changes
time.sleep(0.1)


# Uncheck the checkbox to show the itinerary table
try:
    checkbox = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "s0-1-0-0-17-10-0-5-7-search-partners"))
    )
    if checkbox.is_selected():  # Uncheck the box if it's already checked
        checkbox.click()
        print("Unchecked the box to show the itinerary table.")
    else:
        print("The checkbox is already unchecked.")
except Exception as e:
    print(f"Error unchecking the box: {e}")


