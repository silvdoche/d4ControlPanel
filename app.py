from flask import Flask, render_template, jsonify, request
import threading
import deleter
import post
import capture
import cutpercent

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
        return jsonify({"status": "success", "message": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

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