from flask import Flask, render_template, jsonify, request
import threading
import deleter
import post
import capture
import cutpercent
import json
from pathlib import Path
import base64

app = Flask(__name__)

# Route to render the frontend
@app.route('/')
def index():
    return render_template('index.html')

# Route to delete items
@app.route('/delete_items', methods=['POST'])
def delete_items():
    try:
        result = deleter.delete_items()  # Call the deleter script
        # Check if result is a tuple (status, message) or just a message
        if isinstance(result, tuple):
            status, message = result
            return jsonify({"status": status, "message": message})
        else:
            return jsonify({"status": "success", "message": str(result)}) # Convert result to string
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/items', methods=['GET'])
def get_items():
    """Get all items from the items directory."""
    items = []
    items_dir = Path('C:/items')
    default_image_path = Path('templates/default.png')
    
    # Read default image as base64
    try:
        with open(default_image_path, 'rb') as img_file:
            default_image = f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"
    except:
        default_image = ''  # Empty string if default image can't be loaded
    
    try:
        # Get all folders in the items directory
        for item_folder in items_dir.iterdir():
            if item_folder.is_dir():
                json_file = item_folder / 'captured_post_request.json'
                if json_file.exists():
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if data and len(data) > 0:
                                post_data = json.loads(data[0]['postData'])
                                item_data = post_data['0']['json']
                                
                                # Use default image if no image in JSON or if image field is empty
                                image = item_data.get('image', '')
                                if not image:
                                    image = default_image
                                
                                items.append({
                                    'name': item_data.get('name', 'Unknown Item'),
                                    'price': item_data.get('price', 0),
                                    'image': image,
                                    'folder_name': item_folder.name
                                })
                    except (json.JSONDecodeError, KeyError, IndexError) as e:
                        print(f"Error processing {json_file}: {str(e)}")
                        continue  # Skip this file but continue with others
        
        # Sort items by price (optional, remove if not needed)
        items.sort(key=lambda x: x['price'], reverse=True)
        
        return jsonify(items)
    except Exception as e:
        print(f"Error in get_items: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/items/<path:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Delete an item folder and its contents."""
    items_dir = Path('C:/items')
    folder_path = items_dir / item_id
    
    try:
        if folder_path.exists():
            # Delete all files in the folder
            for file_path in folder_path.glob('*'):
                file_path.unlink()
            # Delete the folder
            folder_path.rmdir()
            return jsonify({'message': f'Successfully deleted {item_id}'})
        else:
            return jsonify({'error': 'Item not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to cut percentage from item prices
@app.route('/cut_percent', methods=['POST'])
def cut_percent_route():
    try:
        directory = request.json.get('directory', r'C:\items')
        percent = float(request.json.get('percent', 10))
        
        result = cutpercent.cut_percent(directory, percent)
        
        return jsonify({
            "status": "success", 
            "message": f"Reduced prices by {percent}%.",
            "details": result
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# Route to post items
@app.route('/post_items', methods=['POST'])
def post_items():
    try:
        if not request.is_json:
            return jsonify({"status": "error", "message": "Request must be JSON"}), 400
            
        data = request.get_json()
        if data is None:
            return jsonify({"status": "error", "message": "Invalid JSON data"}), 400
            
        directory = data.get('directory', r'C:\items')
        result = post.scan_and_post(directory)
        
        if isinstance(result, dict):
            return jsonify(result)
        else:
            return jsonify({"status": "success", "message": "POST requests sent successfully."})
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Updated capture routes to match capture.py
@app.route('/capture_toggle', methods=['POST'])
def capture_toggle():
    try:
        directory = request.json.get('directory', r'C:\items')
        result = capture.toggle_capture()  # Call the toggle_capture function from capture.py
        return result
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/capture_status', methods=['GET'])
def get_capture_status():
    try:
        return capture.get_capture_status()
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)