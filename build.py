import os
import subprocess
from PIL import Image
import re
import json
import random # 🚀 NEW: Required for our Home Page shuffle

FOLDERS = [
    "real-estate", "travel", "theatre", 
    "video-travel", "video-music", "video-shorts", "video-theatre",
    "web-branding", "floor-plans", "3d-tours"
]

js_content = "// AUTO-GENERATED FILE. DO NOT EDIT MANUALLY.\n\n"

# PARSE DESCRIPTIONS INTO JAVASCRIPT
descriptions = {}
if os.path.exists("descriptions.txt"):
    with open("descriptions.txt", "r") as f:
        for line in f.readlines():
            if not line.strip() or line.strip().startswith('#'):
                continue
            parts = line.split(',', 1)
            if len(parts) == 2:
                folder = parts[0].strip()
                desc = parts[1].strip()
                descriptions[f"tab-{folder}"] = desc

js_content += "const categoryDescriptions = {\n"
for tab_class, desc in descriptions.items():
    safe_desc = desc.replace('"', '\\"').replace('\n', ' ')
    js_content += f'  "{tab_class}": "{safe_desc}",\n'
js_content += "};\n\n"

category_logos = {} 

# 🚀 NEW: Our global pool for the Home Page
all_portfolio_images = []

def get_avg_color(img_path):
    try:
        with Image.open(img_path) as img:
            return img.convert("RGB").resize((1, 1)).getpixel((0, 0))
    except Exception:
        return (0, 0, 0)

def color_distance(c1, c2):
    return sum((a - b) ** 2 for a, b in zip(c1, c2))

def get_aspect_ratio(img_path):
    try:
        with Image.open(img_path) as img:
            return img.width / img.height
    except Exception:
        return 1.0

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
    blurb_logos = [] 
    
    for filename in os.listdir(fulls_dir):
        if filename.startswith('.') or not os.path.isfile(os.path.join(fulls_dir, filename)):
            continue
            
        title, ext = os.path.splitext(filename)
        clean_title = title[4:] if title.startswith("web_") else title
        
        is_blurb = "[blurb]" in clean_title.lower()
        
        media_id = ""
        media_match = re.search(r'\[(.*?)\]', clean_title)
        if media_match:
            raw_id = media_match.group(1)
            if raw_id.startswith("mp_"):
                media_id = f"https://my.matterport.com/show/?m={raw_id[3:]}"
            elif raw_id.startswith("vw_"):
                media_id = f"https://3dtour.vieweet.com/?tour={raw_id[3:]}"
            elif raw_id.startswith("ry_"):
                media_id = f"https://www.rayon.design/app/model/{raw_id[3:]}/presentation"
            else:
                media_id = raw_id
            
        safe_title = re.sub(r'[^A-Za-z0-9\[\]\-_ ]', '_', clean_title)
        
        target_ext = ".png" if ext.lower() == ".png" else ".jpg"
        new_filename = f"web_{safe_title}{target_ext}"
        
        orig_path = os.path.join(fulls_dir, filename)
        new_full_path = os.path.join(fulls_dir, new_filename)
        thumb_path = os.path.join(thumbs_dir, new_filename)
        
        if orig_path != new_full_path:
            if not os.path.exists(new_full_path):
                print(f"🗜 Optimizing & Renaming: {filename} -> {new_filename}")
                if target_ext == ".png":
                    subprocess.run(['sips', '-Z', '2560', orig_path, '--out', new_full_path], capture_output=True)
                else:
                    subprocess.run(['sips', '-Z', '2560', '-s', 'format', 'jpeg', '-s', 'formatOptions', '80', orig_path, '--out', new_full_path], capture_output=True)
            os.remove(orig_path)
                
        if not os.path.exists(thumb_path):
            print(f"📸 Generating thumbnail: {new_filename}")
            if target_ext == ".png":
                subprocess.run(['sips', '-Z', '600', new_full_path, '--out', thumb_path], capture_output=True)
            else:
                subprocess.run(['sips', '-Z', '600', '-s', 'formatOptions', '70', new_full_path, '--out', thumb_path], capture_output=True)
        
        if is_blurb:
            aspect = get_aspect_ratio(thumb_path)
            blurb_logos.append({"path": f"images/{folder}/thumbs/{new_filename}", "aspect": aspect})
        else:
            avg_color = get_avg_color(thumb_path)
            
            # 🚀 NEW: Calculate the orientation for the locked grid
            orientation = "square"
            try:
                with Image.open(thumb_path) as img:
                    w, h = img.size
                    if w > h * 1.15: # 15% wider than tall = landscape
                        orientation = "landscape"
                    elif h > w * 1.15: # 15% taller than wide = portrait
                        orientation = "portrait"
            except Exception:
                pass

            images_data.append({"file": new_filename, "title": clean_title, "color": avg_color, "mediaId": media_id})
            
            # Add to global pool WITH the orientation tag
            all_portfolio_images.append({
                "file": new_filename, 
                "folder": folder, 
                "title": clean_title, 
                "color": avg_color, 
                "mediaId": media_id,
                "originTab": f"tab-{folder}",
                "orientation": orientation # 🚀 NEW
            })        
    if blurb_logos:
        blurb_logos.sort(key=lambda x: x["aspect"], reverse=True)
        arranged_logos = []
        left = 0
        right = len(blurb_logos) - 1
        while left <= right:
            arranged_logos.append(blurb_logos[left]["path"])
            left += 1
            if left <= right:
                arranged_logos.append(blurb_logos[right]["path"])
                right -= 1
        category_logos[f"tab-{folder}"] = arranged_logos
        
    arranged_images = []
    if images_data:
        arranged_images.append(images_data.pop(0))
        while images_data:
            idx = len(arranged_images)
            best_img = None
            best_score = -1
            
            for img in images_data:
                c_color = img["color"]
                dist_prev = color_distance(arranged_images[idx - 1]["color"], c_color)
                if idx >= 2:
                    dist_above = color_distance(arranged_images[idx - 2]["color"], c_color)
                    score = min(dist_prev, dist_above)
                else:
                    score = dist_prev
                    
                if score > best_score:
                    best_score = score
                    best_img = img
                    
            arranged_images.append(best_img)
            images_data.remove(best_img)
            
    var_parts = folder.split('-')
    var_name = var_parts[0] + "".join(word.capitalize() for word in var_parts[1:]) + "Images"
    
    if var_name[0].isdigit():
        var_name = "_" + var_name
        
    js_content += f"const {var_name} = [\n"
    for img in arranged_images:
        js_content += f'  {{ file: "{img["file"]}", title: "{img["title"]}", mediaId: "{img["mediaId"]}" }},\n'
    js_content += "];\n\n"

# 🚀 NEW: BUILD THE HOME PAGE GRID ARRAY
TOTAL_HOME_IMAGES = 64 

# 🚀 PURIST ROUTE: Only allow aesthetic photo/video folders
purist_folders = ["real-estate", "travel", "theatre", "video-travel", "video-music", "video-shorts", "video-theatre"]
pure_portfolio = [img for img in all_portfolio_images if img["folder"] in purist_folders]

sample_size = min(TOTAL_HOME_IMAGES, len(pure_portfolio))
home_raw_selection = random.sample(pure_portfolio, sample_size)

arranged_home_images = []
if home_raw_selection:
    arranged_home_images.append(home_raw_selection.pop(0))
    while home_raw_selection:
        idx = len(arranged_home_images)
        best_img = None
        best_score = -1
        
        for img in home_raw_selection:
            c_color = img["color"]
            dist_prev = color_distance(arranged_home_images[idx - 1]["color"], c_color)
            if idx >= 2:
                dist_above = color_distance(arranged_home_images[idx - 2]["color"], c_color)
                score = min(dist_prev, dist_above)
            else:
                score = dist_prev
                
            if score > best_score:
                best_score = score
                best_img = img
                
        arranged_home_images.append(best_img)
        home_raw_selection.remove(best_img)

# Output the new array to data.js
js_content += "const homeImages = [\n"
for img in arranged_home_images:
    # 🚀 NEW: Added the isVideo tag to power the auto-play engine
    is_video = "true" if "video" in img["folder"].lower() else "false"
    js_content += f'  {{ file: "{img["file"]}", folder: "{img["folder"]}", title: "{img["title"]}", mediaId: "{img["mediaId"]}", originTab: "{img["originTab"]}", orientation: "{img["orientation"]}", isVideo: {is_video} }},\n'
js_content += "];\n\n"
with open("data.js", "w") as f:
    f.write(js_content)

print("✅ Success! Images, Videos, Text Descriptions, Logos, Interactive Tours, AND Home Grid processed!")