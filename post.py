from flask import Flask, jsonify, request
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

def send_post_via_selenium(captured_requests):
    try:
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(options=chrome_options)
        
        results = []
        for req in captured_requests:
            url = req.get('url')
            headers = req.get('headers', {})
            post_data = req.get('postData')

            if url and post_data:
                js_script = f"""
                fetch("{url}", {{
                    method: "POST",
                    headers: {json.dumps(headers)},
                    body: JSON.stringify({post_data})
                }})
                .then(response => response.text())
                .then(data => {{
                    console.log("Response from {url}: ", data);
                }})
                .catch(error => {{
                    console.error("Error:", error);
                }});
                """
                try:
                    driver.execute_script(js_script)
                    results.append({
                        "url": url, 
                        "status": "success",
                        "message": f"Successfully posted to {url}"
                    })
                except Exception as e:
                    results.append({
                        "url": url, 
                        "status": "error", 
                        "message": f"Error posting to {url}: {str(e)}"
                    })
            else:
                results.append({
                    "status": "error", 
                    "message": "Missing URL or POST data"
                })

        driver.quit()
        return {"status": "success", "results": results}
    except Exception as e:
        return {"status": "error", "message": f"Selenium error: {str(e)}"}

def scan_and_post(directory):
    try:
        if not os.path.exists(directory):
            return {"status": "error", "message": f"Directory not found: {directory}"}
        
        results = []
        files_processed = 0
        
        for subdir, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".json"):
                    json_file_path = os.path.join(subdir, file)
                    try:
                        with open(json_file_path, 'r') as f:
                            captured_requests = json.load(f)
                            result = send_post_via_selenium(captured_requests)
                            results.append({
                                "file": json_file_path,
                                "result": result,
                                "message": f"Processing file: {json_file_path}"
                            })
                            files_processed += 1
                    except json.JSONDecodeError as e:
                        results.append({
                            "file": json_file_path,
                            "status": "error",
                            "message": f"Invalid JSON in file: {str(e)}"
                        })
                    except Exception as e:
                        results.append({
                            "file": json_file_path,
                            "status": "error",
                            "message": f"Error processing file: {str(e)}"
                        })
        
        if files_processed == 0:
            return {"status": "warning", "message": "No JSON files found to process"}
            
        return {
            "status": "success",
            "message": f"Processed {files_processed} files",
            "results": results
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Scan error: {str(e)}"}

@app.route('/post_items', methods=['POST'])
def post_items():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No JSON data received"}), 400
            
        directory = data.get('directory', r'C:\items')
        result = scan_and_post(directory)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)