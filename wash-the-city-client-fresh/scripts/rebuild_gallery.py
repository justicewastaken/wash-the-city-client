#!/usr/bin/env python3
"""
Rebuild the customer photos gallery grid from all images in images/reviews/.

Usage:
  python rebuild_gallery.py
"""

import os
import re

def rebuild_gallery():
    # Get all image files, sorted
    img_dir = 'images/reviews'
    img_files = sorted([
        f for f in os.listdir(img_dir)
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))
    ])
    print(f"Found {len(img_files)} images in {img_dir}")

    # Build HTML items
    grid_items = []
    for f in img_files:
        grid_items.append(f'''    <div class="gallery-item" onclick="openLightbox(this)">
      <img src="images/reviews/{f}" alt="Customer photo" loading="lazy">
      <div class="overlay"><span>Customer Photo</span></div>
    </div>''')

    # Read index.html
    with open('index.html', 'r') as file:
        content = file.read()

    # Replace photos-grid section
    pattern = r'(<div class="photos-grid" id="photosGrid">)(.*?)(</div>\s*</section>)'
    replacement = r'\1\n' + '\n'.join(grid_items) + r'\n  </div>\n</section>'
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # Write back
    with open('index.html', 'w') as file:
        file.write(new_content)

    print(f"Gallery grid rebuilt with {len(img_files)} images")

if __name__ == '__main__':
    rebuild_gallery()
