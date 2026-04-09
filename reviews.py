import json
import os
import re

print("⭐ Starting Review Extractor & Smart GDPR Scrubber...")

def get_believable_location(address):
    if not address:
        return "Isle of Wight Vendor"
        
    # 1. Strip the postcode (PO followed by numbers and letters)
    addr = re.sub(r'\bPO\d{1,2}\s*\d[A-Z]{2}\b', '', address, flags=re.IGNORECASE)
    
    # 2. Strip "Isle of Wight" to avoid repetition (we know where we are!)
    addr = re.sub(r',?\s*Isle of Wight\s*', '', addr, flags=re.IGNORECASE)
    
    # 3. Strip leading house numbers (e.g., "13 ", "45A ")
    addr = re.sub(r'^\d+[a-zA-Z]?\s+', '', addr)
    
    # 4. Strip "Flat X" or "Apartment X"
    addr = re.sub(r'^(Flat|Apartment|Unit)\s*\d*[a-zA-Z]?\s*', '', addr, flags=re.IGNORECASE)
    
    # Clean up any stray commas and spaces left behind
    return addr.strip(', ').strip()

# 2. Load the raw JSON
try:
    with open('raw_reviews.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
except Exception as e:
    print("❌ Error loading JSON. Check your raw_reviews.json file.")
    exit()

# 3. Extract, Scrub, and Filter
valid_reviews = []
recent_feedback = data.get("RecentFeedback", [])

for item in recent_feedback:
    try:
        rate = float(item.get("FeedbackRate", 0))
    except (ValueError, TypeError):
        rate = 0.0
        
    text = item.get("FeedbackText", "").strip()
    raw_address = item.get("OrderAddress", "")
    
    if rate >= 5.0 and text != "":
        safe_location = get_believable_location(raw_address)
        
        valid_reviews.append({
            "text": text,
            "location": safe_location
        })

print(f"✅ Found and scrubbed {len(valid_reviews)} highly believable 5-star reviews.")

# 4. Save to JS
js_content = "// AUTO-GENERATED FILE. DO NOT EDIT MANUALLY.\n\n"
js_content += f"const clientReviews = {json.dumps(valid_reviews, indent=2)};\n"

with open('reviews_data.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("🎉 Successfully built reviews_data.js!")