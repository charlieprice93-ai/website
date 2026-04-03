import os
import subprocess
from PIL import Image

FOLDERS = ["real-estate", "travel", "video", "theatre"]

# Start writing the new data.js file
js_content = "// AUTO-GENERATED FILE. DO NOT EDIT MANUALLY.\n\n"

def get_avg_color(img_path):
    """Opens an image, shrinks it to 1 pixel, and extracts the RGB value."""
    try:
        with Image.open(img_path) as img:
            return img.convert("RGB").resize((1, 1)).getpixel((0, 0))
    except Exception:
        return (0, 0, 0)

def color_distance(c1, c2):
    """Calculates the mathematical distance between two RGB colors."""
    return sum((a - b) ** 2 for a, b in zip(c1, c2))

for folder in FOLDERS:
    fulls_dir = f"images/{folder}/fulls"
    thumbs_dir = f"images/{folder}/thumbs"
    
    # Ensure folders exist
    os.makedirs(thumbs_dir, exist_ok=True)
    if not os.path.exists(fulls_dir):
        os.makedirs(fulls_dir, exist_ok=True)
        
    images_data = []
    
    # 1. OPTIMIZE AND GATHER DATA
    for filename in os.listdir(fulls_dir):
        if filename.startswith('.') or not os.path.isfile(os.path.join(fulls_dir, filename)):
            continue
            
        title, ext = os.path.splitext(filename)
        new_filename = f"{title}.jpg"
        
        orig_path = os.path.join(fulls_dir, filename)
        new_full_path = os.path.join(fulls_dir, new_filename)
        thumb_path = os.path.join(thumbs_dir, new_filename)
        
        # Optimize if thumbnail doesn't exist (using Mac's native 'sips')
        if not os.path.exists(thumb_path):
            print(f"🗜 Optimizing: {filename} -> Web JPEG")
            subprocess.run(['sips', '-Z', '2560', '-s', 'format', 'jpeg', '-s', 'formatOptions', '80', orig_path, '--out', new_full_path], capture_output=True)
            
            if orig_path != new_full_path:
                os.remove(orig_path) # Delete original PNG/TIFF to save space
                
            print(f"📸 Generating thumbnail: {new_filename}")
            subprocess.run(['sips', '-Z', '600', '-s', 'formatOptions', '70', new_full_path, '--out', thumb_path], capture_output=True)
        
        # Analyze color
        avg_color = get_avg_color(thumb_path)
        images_data.append({
            "file": new_filename,
            "title": title,
            "color": avg_color
        })
        
    # 2. THE INTELLIGENT SHUFFLE (Greedy Contrast Algorithm)
    arranged_images = []
    if images_data:
        # Place the first image to start the chain
        arranged_images.append(images_data.pop(0))
        
        while images_data:
            last_color = arranged_images[-1]["color"]
            # Find the image with the MAXIMUM color distance from the last placed image
            furthest_img = max(images_data, key=lambda x: color_distance(last_color, x["color"]))
            arranged_images.append(furthest_img)
            images_data.remove(furthest_img)
            
    # 3. WRITE TO JAVASCRIPT
    # Format the variable name correctly (e.g., 'real-estate' becomes 'realEstateImages')
    var_parts = folder.split('-')
    var_name = var_parts[0] + "".join(word.capitalize() for word in var_parts[1:]) + "Images"
    
    js_content += f"const {var_name} = [\n"
    for img in arranged_images:
        js_content += f'  {{ file: "{img["file"]}", title: "{img["title"]}", desc: "" }},\n'
    js_content += "];\n\n"

# Save the final file
with open("data.js", "w") as f:
    f.write(js_content)

print("✅ Success! Images optimized, color-analyzed, beautifully contrasted, and data.js updated.")