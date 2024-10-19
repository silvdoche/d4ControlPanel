from flask import Flask, jsonify, request
import pychrome
import json
import os
import threading
import time
from datetime import datetime

app = Flask(__name__)

# Global state management
class CaptureState:
    def __init__(self):
        self.is_capturing = False
        self.current_tab = None
        self.browser = None
        self.capture_thread = None
        self.last_error = None
        self.captured_items = []
        self.stop_flag = threading.Event()

capture_state = CaptureState()

def format_price(price):
    if isinstance(price, str):
        price = float(price)
    
    if price >= 1_000_000_000:
        billions = price / 1_000_000_000
        return f"{billions:.1f}b".rstrip('0').rstrip('.')  # Removes trailing zeros and decimal point if whole number
    elif price >= 1_000_000:
        millions = price / 1_000_000
        return f"{millions:.1f}m".rstrip('0').rstrip('.')  # Removes trailing zeros and decimal point if whole number
    else:
        return str(int(price))

def handle_request_will_be_sent(capture_directory, **kwargs):
    """Handle captured requests and return capture details."""
    try:
        request = kwargs.get('request', {})
        method = request.get('method', '')
        
        if method.upper() == 'POST':
            post_data = request.get('postData')
            if not post_data:
                return None
                
            post_data_json = json.loads(post_data)
            item_name = post_data_json['0']['json']['name']
            item_price = post_data_json['0']['json']['price']
            
            # Format the price into human-readable form
            formatted_price = format_price(item_price)
            
            # Create folder path
            folder_name = f"{item_name}-{formatted_price}"
            folder_path = os.path.join(capture_directory, folder_name)
            
            # Create directory if it doesn't exist
            os.makedirs(folder_path, exist_ok=True)
            
            # Save request data
            file_path = os.path.join(folder_path, 'captured_post_request.json')
            request_data = [{
                'url': request.get('url'),
                'headers': request.get('headers'),
                'postData': post_data
            }]
            
            with open(file_path, 'w') as f:
                json.dump(request_data, f, indent=2)
            
            # Return capture details
            return {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'item_name': item_name,
                'price': formatted_price,
                'file_path': file_path
            }
            
    except Exception as e:
        capture_state.last_error = str(e)
        return None

def capture_post_requests(capture_directory):
    """Main capture function running in separate thread."""
    try:
        # Connect to Chrome
        capture_state.browser = pychrome.Browser(url="http://127.0.0.1:9222")
        tabs = capture_state.browser.list_tab()
        
        if not tabs:
            raise Exception("No Chrome tabs found. Make sure Chrome is running with --remote-debugging-port=9222")
        
        capture_state.current_tab = tabs[0]
        capture_state.current_tab.start()
        
        # Enable network tracking
        capture_state.current_tab.call_method("Network.enable")
        
        def event_handler(**kwargs):
            if capture_state.is_capturing:
                capture_details = handle_request_will_be_sent(capture_directory, **kwargs)
                if capture_details:
                    capture_state.captured_items.append(capture_details)
        
        # Set up event listener
        capture_state.current_tab.set_listener("Network.requestWillBeSent", event_handler)
        
        while not capture_state.stop_flag.is_set():
            capture_state.current_tab.wait(1)
            
    except Exception as e:
        capture_state.last_error = str(e)
    finally:
        cleanup_capture()

def cleanup_capture():
    """Clean up capture resources."""
    try:
        if capture_state.current_tab:
            capture_state.current_tab.stop()
        capture_state.is_capturing = False
        capture_state.current_tab = None
        capture_state.browser = None
        capture_state.stop_flag.clear()
    except Exception as e:
        capture_state.last_error = str(e)

@app.route('/capture_status', methods=['GET'])
def get_capture_status():
    """Get current capture status and recent captures."""
    return jsonify({
        'is_capturing': capture_state.is_capturing,
        'last_error': capture_state.last_error,
        'captured_items': capture_state.captured_items[-10:],  # Return last 10 items
    })

@app.route('/capture_toggle', methods=['POST'])
def toggle_capture():
    """Toggle capture state on/off."""
    try:
        if capture_state.is_capturing:
            # Stop capture
            capture_state.is_capturing = False
            capture_state.stop_flag.set()
            if capture_state.capture_thread:
                capture_state.capture_thread.join(timeout=5)
            cleanup_capture()
            return jsonify({
                "status": "success",
                "message": "Capture stopped successfully.",
                "is_capturing": False
            })
        else:
            # Start capture
            # Check if request has JSON data
            directory = r'C:\items'  # Default directory
            if request.is_json:
                directory = request.json.get('directory', directory)
                
            capture_state.is_capturing = True
            capture_state.last_error = None
            capture_state.captured_items = []
            capture_state.stop_flag.clear()
            
            capture_state.capture_thread = threading.Thread(
                target=capture_post_requests,
                args=(directory,)
            )
            capture_state.capture_thread.daemon = True
            capture_state.capture_thread.start()
            
            return jsonify({
                "status": "success",
                "message": "Capture started successfully.",
                "is_capturing": True
            })
            
    except Exception as e:
        capture_state.is_capturing = False
        capture_state.last_error = str(e)
        return jsonify({
            "status": "error",
            "message": str(e),
            "is_capturing": False
        }), 500

if __name__ == '__main__':
    app.run(debug=True)