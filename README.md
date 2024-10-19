# d4ControlPanel

This application provides a control panel for managing Diablo 4 trade listings. It allows you to delete existing listings, post new items from captured requests, and adjust prices.

## Prerequisites

* **Python 3.7+:** Ensure you have Python installed. You can download it from [https://www.python.org/downloads/](https://www.python.org/downloads/).
* **Google Chrome:** Install Google Chrome from [https://www.google.com/chrome/](https://www.google.com/chrome/).
* **Required Python Packages:** Install the necessary Python packages using pip:

   ```bash
   pip install -r requirements.txt
   ```
   ## Running the Application

1. **Enable Remote Debugging in Chrome:**
   * Close all existing Chrome instances.
   * Open a command prompt or terminal.
   * Launch Chrome with the remote debugging flag:
     ```bash
     chrome.exe --remote-debugging-port=9222
     ```
   * **(Optional) Keep Chrome Running in the Background:**  If you want the Chrome window to remain open but minimized, you can use the following command instead:
     ```bash
     start /min chrome.exe --remote-debugging-port=9222
     ```
     This uses the `start /min` command on Windows to start Chrome minimized.  Adjust this command appropriately for other operating systems if needed.

2. **Run the Flask Application:**
   * Navigate to the project directory in your terminal.
   * Run the `app.py` script:
     ```bash
     python app.py
     ```

3. **Access the Control Panel:**
   * Open a web browser and go to `http://127.0.0.1:5000/`.

## Usage

* **Working Directory:** Specify the directory where your captured item JSON files are located. The default is `C:\items`.
* **Delete Items:** Deletes all current Diablo 4 trade listings.  Make sure you are logged into `diablo.trade` in the Chrome instance you started with remote debugging.
* **Post Items:** Posts items from the JSON files in the specified directory to Diablo 4 trade.
* **Cut Prices:** Reduces the prices of items in the JSON files by a specified percentage and renames the folders accordingly.
* **Capture:** Starts and stops the capture of new item postings on diablo.trade. Captured items are saved as JSON files in the specified directory.  Make sure you have the `diablo.trade` website with your listings open in the Chrome instance you started with remote debugging.

## Troubleshooting

* **Chrome not running:** Ensure Chrome is running with the `--remote-debugging-port=9222` flag.
* **Port in use:** If port 5000 is already in use, try a different port by setting the `PORT` environment variable or modifying the `app.run()` command in `app.py`.
* **Missing packages:** Install all required packages listed in `requirements.txt`.
* **Incorrect directory:** Verify the working directory is correct and contains valid JSON files.
