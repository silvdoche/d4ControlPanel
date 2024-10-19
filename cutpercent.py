import os
import json

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

def reduce_price_and_rename_folder(directory, percentage=10):
    """Reduce the price of items in the captured requests by the given percentage."""
    success_count = 0
    error_count = 0
    
    # Convert percentage to float
    percentage = float(percentage)
    
    # Collect all work to be done first
    work_items = []
    
    # First pass: collect all the work that needs to be done
    for subdir, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                json_file_path = os.path.join(subdir, file)
                try:
                    with open(json_file_path, 'r') as f:
                        captured_requests = json.load(f)
                    
                    for req in captured_requests:
                        post_data = req.get('postData')
                        post_data_json = json.loads(post_data)
                        
                        # Get current price and calculate new price
                        current_price = float(post_data_json['0']['json']['price'])
                        new_price = int(current_price * (1 - percentage / 100))
                        item_name = post_data_json['0']['json']['name']
                        
                        # Store the work to be done
                        work_items.append({
                            'json_path': json_file_path,
                            'current_folder': subdir,
                            'item_name': item_name,
                            'new_price': new_price,
                            'captured_requests': captured_requests,
                            'request_index': captured_requests.index(req),
                            'post_data_json': post_data_json
                        })
                        
                except Exception as e:
                    print(f"Error reading {json_file_path}: {e}")
                    error_count += 1
    
    # Second pass: process all the collected work
    processed_folders = set()
    
    for work in work_items:
        try:
            # Update the JSON data
            post_data_json = work['post_data_json']
            post_data_json['0']['json']['price'] = work['new_price']
            captured_requests = work['captured_requests']
            captured_requests[work['request_index']]['postData'] = json.dumps(post_data_json)
            
            # Save the updated JSON file
            with open(work['json_path'], 'w') as f:
                json.dump(captured_requests, f, indent=2)
            
            print(f"Updated price in {work['json_path']} to {work['new_price']} ({format_price(work['new_price'])})")
            
            # Handle folder renaming (only once per folder)
            if work['current_folder'] not in processed_folders:
                processed_folders.add(work['current_folder'])
                
                new_folder_name = f"{work['item_name']}-{format_price(work['new_price'])}"
                new_folder_path = os.path.join(os.path.dirname(work['current_folder']), new_folder_name)
                
                if work['current_folder'] != new_folder_path:
                    if not os.path.exists(new_folder_path):
                        os.rename(work['current_folder'], new_folder_path)
                        print(f"Renamed folder from {work['current_folder']} to {new_folder_name}")
            
            success_count += 1
            
        except Exception as e:
            print(f"Error processing work item: {e}")
            error_count += 1
    
    return {"success_count": success_count, "error_count": error_count}

def cut_percent(directory, percentage):
    """Wrapper function for Flask API."""
    return reduce_price_and_rename_folder(directory, percentage)