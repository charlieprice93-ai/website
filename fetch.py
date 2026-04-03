import os
import urllib.request
import urllib.error
import re

print("🚀 Starting YouTube Thumbnail Ripper...")

# Check if the text file exists
if not os.path.exists('videos.txt'):
    print("❌ Cannot find videos.txt. Please create it first.")
    exit()

with open('videos.txt', 'r') as file:
    lines = file.readlines()

for line in lines:
    # Skip empty lines or comments (lines starting with #)
    if not line.strip() or line.strip().startswith('#'):
        continue
        
    parts = line.split(',')
    
    if len(parts) >= 3:
        folder = parts[0].strip()
        title = parts[1].strip()
        url = parts[2].strip()
        
        # Extract the YouTube ID from various URL formats
        match = re.search(r'(?:v=|youtu\.be\/)([\w-]+)', url)
        
        if match:
            yt_id = match.group(1)
            
            # YouTube stores thumbnails at these specific URLs
            url_maxres = f"https://img.youtube.com/vi/{yt_id}/maxresdefault.jpg"
            url_hq = f"https://img.youtube.com/vi/{yt_id}/hqdefault.jpg"
            
            # Create the folder if it doesn't exist
            target_dir = f"images/{folder}/fulls"
            os.makedirs(target_dir, exist_ok=True)
            
            # Setup the final file path with our Bracket Trick
            # Note: We replace weird characters in the title just to be safe for Mac folders
            safe_title = re.sub(r'[^A-Za-z0-9 ]', '', title)
            target_path = os.path.join(target_dir, f"{safe_title} [{yt_id}].jpg")
            
            # Skip if we already downloaded it previously
            if os.path.exists(target_path):
                print(f"⏩ Already exists, skipping: {safe_title}")
                continue
                
            print(f"📥 Downloading: {safe_title}...")
            
            try:
                # Try to get the 4K/1080p thumbnail first
                urllib.request.urlretrieve(url_maxres, target_path)
            except urllib.error.HTTPError:
                # If the video doesn't have a 4K thumbnail, fallback to High Quality
                try:
                    urllib.request.urlretrieve(url_hq, target_path)
                except Exception as e:
                    print(f"❌ Failed to download {safe_title}: {e}")
        else:
            print(f"⚠️ Could not find a valid YouTube ID in this URL: {url}")

print("✅ All thumbnails successfully ripped and saved!")