import os
import subprocess
from PIL import Image
import re

FOLDERS = [
    "real-estate", "travel", "theatre", 
    "video-travel", "video-music", "video-shorts", "video-theatre",
    "web-branding", "floor-plans", "3d-tours"
]

js_content = "// AUTO-GENERATED FILE. DO NOT EDIT MANUALLY.\n\n"

def get_avg_color(img_path):
    try:
        with Image.open(img_path) as img:
            return img.convert("RGB").resize((1, 1)).getpixel((0, 0))
    except Exception:
        return (0, 0, 0)

def color_distance(c1, c2):
    return sum((a - b) ** 2 for a, b in zip(c1, c2))

for folder in FOLDERS:
    fulls_dir = f"images/{folder}/fulls"
    thumbs_dir = f"images/{folder}/thumbs"
    
    os.makedirs(thumbs_dir, exist_ok=True)
    if not os.path.exists(fulls_dir):
        os.makedirs(fulls_dir, exist_ok=True)
        
    for thumb_file in os.listdir(thumbs_dir):
        if thumb_file.startswith('.') or not os.path.isfile(os.path.join(thumbs_dir, thumb_file)):
            continue
        if not thumb_file.startswith("web_"):
            os.remove(os.path.join(thumbs_dir, thumb_file))
            continue
        original_name = thumb_file.replace("web_", "", 1).rsplit(".", 1)[0]
        if not any(f.replace("web_", "", 1).startswith(original_name) for f in os.listdir(fulls_dir)):
            os.remove(os.path.join(thumbs_dir, thumb_file))
            
    images_data = []
    
    for filename in os.listdir(fulls_dir):
        if filename.startswith('.') or not os.path.isfile(os.path.join(fulls_dir, filename)):
            continue
            
        title, ext = os.path.splitext(filename)
        
        clean_title = title[4:] if title.startswith("web_") else title
        
        youtube_id = ""
        yt_match = re.search(r'\[([a-zA-Z0-9_-]{11})\]', clean_title)
        if yt_match:
            youtube_id = yt_match.group(1)
            
        # THE FIX: Allow brackets [] and dashes - to survive the web-safe renaming!
        safe_title = re.sub(r'[^A-Za-z0-9\[\]\-_]', '_', clean_title)
        new_filename = f"web_{safe_title}.jpg"
        
        orig_path = os.path.join(fulls_dir, filename)
        new_full_path = os.path.join(fulls_dir, new_filename)
        thumb_path = os.path.join(thumbs_dir, new_filename)
        
        if orig_path != new_full_path:
            if not os.path.exists(new_full_path):
                print(f"🗜 Optimizing & Renaming: {filename} -> {new_filename}")
                subprocess.run(['sips', '-Z', '2560', '-s', 'format', 'jpeg', '-s', 'formatOptions', '80', orig_path, '--out', new_full_path], capture_output=True)
            os.remove(orig_path)
                
        if not os.path.exists(thumb_path):
            print(f"📸 Generating thumbnail: {new_filename}")
            subprocess.run(['sips', '-Z', '600', '-s', 'formatOptions', '70', new_full_path, '--out', thumb_path], capture_output=True)
        
        avg_color = get_avg_color(thumb_path)
        images_data.append({"file": new_filename, "title": clean_title, "color": avg_color, "youtubeId": youtube_id})
        
    arranged_images = []
    if images_data:
        arranged_images.append(images_data.pop(0))
        while images_data:
            last_color = arranged_images[-1]["color"]
            furthest_img = max(images_data, key=lambda x: color_distance(last_color, x["color"]))
            arranged_images.append(furthest_img)
            images_data.remove(furthest_img)
            
    var_parts = folder.split('-')
    var_name = var_parts[0] + "".join(word.capitalize() for word in var_parts[1:]) + "Images"
    
    js_content += f"const {var_name} = [\n"
    for img in arranged_images:
        js_content += f'  {{ file: "{img["file"]}", title: "{img["title"]}", youtubeId: "{img["youtubeId"]}" }},\n'
    js_content += "];\n\n"

with open("data.js", "w") as f:
    f.write(js_content)

print("✅ Success! Images, Videos, and Categories processed!")