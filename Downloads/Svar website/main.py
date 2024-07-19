import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException, ElementClickInterceptedException

# Set up Chrome options
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run headless Chrome - this line is commented out to see the browser
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Automatically detect and set up the Chrome driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL to scrape
base_url = "https://rive.app/community/files/"

# Open the URL
driver.get(base_url)
print("Opened base URL")

# Scroll to the bottom to load all files (adjust if necessary)
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Wait for new content to load
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height
print("Scrolled to the bottom of the main page")

# Parse the page and find file links
file_elements = driver.find_elements(By.CSS_SELECTOR, "li.CommunityGridItem_CommunityGridItem__g9QSN a")
print(f"Found {len(file_elements)} file elements")

# Folder to save downloaded files
download_folder = "downloaded_files"
os.makedirs(download_folder, exist_ok=True)
print(f"Created download folder: {download_folder}")

# Function to download a file
def download_file(file_url, download_folder):
    # Check if the URL points to a file
    file_name = file_url.split('/')[-1]
    local_filename = os.path.join(download_folder, file_name)
    
    # Verify the content type to ensure it's a file
    head = requests.head(file_url, allow_redirects=True)
    content_type = head.headers.get('content-type')
    
    if 'text/html' not in content_type:
        with requests.get(file_url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Downloaded: {local_filename}")
    else:
        print(f"Skipping URL as it is not a file: {file_url}")

# Function to interact with elements within the shadow DOM using JavaScript
def click_element_with_js(driver, selector):
    script = f"""
    const shadowRoot = document.querySelector('flt-glass-pane').shadowRoot;
    const element = shadowRoot.querySelector('{selector}');
    element.click();
    """
    driver.execute_script(script)

# Loop through the file elements and process each file
for index in range(len(file_elements)):
    print(f"Processing file element {index + 1} of {len(file_elements)}")
    
    try:
        # Re-fetch the file elements to avoid stale element reference
        file_elements = driver.find_elements(By.CSS_SELECTOR, "li.CommunityGridItem_CommunityGridItem__g9QSN a")
        if index >= len(file_elements):
            print(f"Index {index} out of range after re-fetching elements.")
            break
        file_element = file_elements[index]

        # Scroll the file element into view
        driver.execute_script("arguments[0].scrollIntoView();", file_element)
        time.sleep(1)  # Give time for the scrolling to complete
        print("Scrolled file element into view")

        # Click on the file element to navigate to its page
        file_element.click()
        print("Clicked on file element to navigate to its page")
        
        # Wait for the page to load
        time.sleep(3)  # Adjust the sleep time if necessary

        # Print the current URL
        current_url = driver.current_url
        print(f"Visited URL: {current_url}")

        # Find and click the "Preview in Rive" button
        try:
            preview_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.OpenInRiveCommunityButton_Container__20R4I'))
            )
            preview_button.click()
            print("Clicked 'Preview in Rive' button")
        except TimeoutException as e:
            print(f"Preview in Rive button not found or clickable within the time frame: {e}")
            continue

        # Switch to the new tab
        driver.switch_to.window(driver.window_handles[-1])
        print("Switched to the new tab")

        # Print the current URL of the new tab
        current_url = driver.current_url
        print(f"Visited URL in new tab: {current_url}")

        time.sleep(5)

        try:
            # Wait for the menu button and click it using JavaScript
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.querySelector('flt-glass-pane').shadowRoot.querySelector('button[aria-label=\"Open menu\"]') !== null")
            )
            click_element_with_js(driver, 'button[aria-label="Open menu"]')
            print("Clicked menu button using JavaScript")

            # Wait for the "Export" option and click it using JavaScript
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.querySelector('flt-glass-pane').shadowRoot.querySelector('div[text()=\"Export\"]') !== null")
            )
            click_element_with_js(driver, 'div[text()="Export"]')
            print("Clicked 'Export' option using JavaScript")

            # Wait for the "For runtime" option and click it using JavaScript
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.querySelector('flt-glass-pane').shadowRoot.querySelector('div[text()=\"For runtime\"]') !== null")
            )
            click_element_with_js(driver, 'div[text()="For runtime"]')
            print("Clicked 'For runtime' option using JavaScript")

            time.sleep(5)  # Wait for the file to download

            # Close the current tab and switch back to the main tab
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            print("Closed current tab and switched back to main tab")

            # Navigate back to the base URL
            driver.get(base_url)
            print("Navigated back to the base URL")

        except (TimeoutException, Exception) as e:
            print(f"Error processing element {index + 1}: {e}")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            driver.get(base_url)
            continue

    except (NoSuchElementException, StaleElementReferenceException, TimeoutException, ElementClickInterceptedException) as e:
        print(f"Error processing element {index + 1}: {e}")
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        driver.get(base_url)
        continue

# Close the browser
driver.quit()
print("Closed the browser")
