from flask import Flask, jsonify, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

# Route to delete items
@app.route('/delete_items', methods=['POST'])
def delete_items():
    try:
        # WebDriver setup
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(options=options)

        # Navigate to Diablo Trade listings and wait for the grid to load
        listings_grid = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".grid.grid-cols-\\[repeat\\(1\\,_280px\\)\\]"))
        )
        time.sleep(1)  # Wait for JavaScript to fully load the listings

        # Get the HTML and parse it with BeautifulSoup
        grid_html = listings_grid.get_attribute('outerHTML')
        soup = BeautifulSoup(grid_html, 'html.parser')

        # Find all listings and extract div IDs
        listings = soup.find_all("div", class_="bg-[#111212]")
        div_ids = []

        for listing in listings:
            div_element = listing.find("div", id=True)
            if div_element:
                div_id = div_element.get('id')
                div_ids.append(div_id)

        # Delete each offer by executing JavaScript in the browser
        for div_id in div_ids:
            delete_offer(driver, div_id)

        return jsonify({"status": "success", "message": f"Deleted {len(div_ids)} items."})
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    
    finally:
        driver.quit()

def delete_offer(driver, div_id):
    url = "https://diablo.trade/api/trpc/offer.removeOffer?batch=1"
    headers = {
        "sec-ch-ua-platform": "\"Windows\"",
        "Referer": "https://diablo.trade/my-listings/items",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "sec-ch-ua": "\"Google Chrome\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"",
        "content-type": "application/json",
        "sec-ch-ua-mobile": "?0"
    }
    post_data = {
        "0": {
            "json": div_id
        }
    }

    # Execute the POST request in the browser using Selenium
    js_script = f"""
    fetch("{url}", {{
        method: "POST",
        headers: {json.dumps(headers)},
        body: JSON.stringify({json.dumps(post_data)})
    }})
    .then(response => response.text())
    .then(data => {{
        console.log("Deleted offer with ID {div_id}: ", data);
    }})
    .catch(error => {{
        console.error("Error deleting offer {div_id}: ", error);
    }});
    """

    driver.execute_script(js_script)
    time.sleep(2)

if __name__ == '__main__':
    app.run(debug=True)
