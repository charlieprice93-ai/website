#!/bin/bash

# 1. Create a fresh data.js file
echo "// AUTO-GENERATED FILE. DO NOT EDIT MANUALLY." > data.js
echo "" >> data.js

# 2. Function to scan a folder, build the array, and make thumbnails
generate_array() {
    folder=$1
    arrayName=$2
    
    echo "const $arrayName = [" >> data.js
    
    if [ -d "images/$folder/fulls" ]; then
        for filepath in images/$folder/fulls/*.*; do
            [ -e "$filepath" ] || continue
            
            # Get the raw file info
            filename=$(basename "$filepath")
            title="${filename%.*}"
            
            # We are going to force EVERY web image to be a standard .jpg
            new_filename="${title}.jpg"
            new_filepath="images/$folder/fulls/$new_filename"
            thumb_path="images/$folder/thumbs/$new_filename"
            
            # Auto-create the thumbs folder if it doesn't exist
            mkdir -p "images/$folder/thumbs"
            
            # If the thumbnail doesn't exist, it means this is a brand new file to process
            if [ ! -f "$thumb_path" ]; then
                echo "🗜 Optimizing massive original: $filename -> 2560px Web JPEG"
                
                # Shrink the "full" image to 2560px, convert to JPEG, and compress to 80%
                sips -Z 2560 -s format jpeg -s formatOptions 80 "$filepath" --out "$new_filepath" > /dev/null 2>&1
                
                # If the original file was a .png or .tiff, delete it so it doesn't go to GitHub
                if [ "$filepath" != "$new_filepath" ]; then
                    rm "$filepath"
                fi
                
                echo "📸 Generating 800px thumbnail for: $new_filename"
                # Generate the tiny thumbnail from the newly optimized JPEG
                sips -Z 600 -s formatOptions 70 "$new_filepath" --out "$thumb_path" > /dev/null 2>&1
            fi
            
            # Write the new .jpg info into the JavaScript array
            echo "  { file: \"$new_filename\", title: \"$title\", desc: \"\" }," >> data.js
        done
    fi
    
    echo "];" >> data.js
    echo "" >> data.js
}

# 3. Tell the script which folders to scan
generate_array "real-estate" "realEstateImages"
generate_array "travel" "travelImages"
generate_array "video" "videoImages"
generate_array "theatre" "theatreImages"

echo "✅ Success! All images optimized, thumbnails generated, and data.js updated."