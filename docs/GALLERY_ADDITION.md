# Adding Images to Customer Photos Gallery

## Process Overview

1. Copy new image files to `images/reviews/`
2. Rebuild the photos-grid HTML to include all images in the folder
3. Commit and push changes

---

## Step-by-Step

### 1. Copy Images
Place all new customer review images into the `wash-the-city-client/images/reviews/` directory.

```bash
# Example (adjust paths as needed)
cp /path/to/new/images/*.jpg /path/to/wash-the-city-client/images/reviews/
cp /path/to/new/images/*.png /path/to/wash-the-city-client/images/reviews/
```

### 2. Rebuild the Grid
Run the Python script that automatically regenerates the entire `photos-grid` section based on all files in `images/reviews/`.

```bash
cd /root/.openclaw/workspace/wash-the-city-client
python3 << 'PYEOF'
import os
img_files = sorted([f for f in os.listdir('images/reviews') if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))])
grid_items = []
for f in img_files:
    grid_items.append(f'''    <div class="gallery-item" onclick="openLightbox(this)">
      <img src="images/reviews/{f}" alt="Customer photo" loading="lazy">
      <div class="overlay"><span>Customer Photo</span></div>
    </div>''')
with open('index.html', 'r') as f:
    content = f.read()
import re
pattern = r'(<div class="photos-grid" id="photosGrid">)(.*?)(</div>\s*</section>)'
replacement = r'\1\n' + '\n'.join(grid_items) + r'\n  </div>\n</section>'
new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
with open('index.html', 'w') as f:
    f.write(new_content)
print(f"Updated grid with {len(img_files)} images")
PYEOF
```

**Note:** This script replaces the entire `photos-grid` div with a fresh list of all images in the folder. It ensures no stale or missing references.

### 3. Verify Changes (Optional)
Check that the HTML now includes all expected images:

```bash
grep -c 'gallery-item' index.html  # should equal number of images
```

### 4. Git Commit & Push
```bash
git add -A
git commit -m "feat: add X new customer photos (total N)"
git push origin main
```

---

## Important Notes

- **Image tracking:** Always run `git add -A` to ensure new image files are staged. Forgetting this causes 404s on Netlify.
- **Clean state:** The rebuild script starts fresh from the `images/reviews/` folder contents. Do not manually edit individual `<img>` tags in HTML; the script will overwrite them.
- **CSS:** The grid uses responsive breakpoints (4 columns on large screens, 3 on medium, 2 on small, 1 on mobile). Do not add manual `grid-column` rules that override the grid.
- **Filename safety:** Use only alphanumeric, hyphens, underscores in filenames. Avoid spaces or special characters.

---

## Troubleshooting

**Symptom:** Images show alt text but not actual picture
- **Cause:** File not tracked by git or not deployed
- **Fix:** Ensure file exists in `images/reviews/`, run `git add -A`, commit, push

**Symptom:** Grid layout breaks (odd row counts, overlapping)
- **Cause:** Old CSS rules (`.gallery-item:nth-child(...)`) from previous layout
- **Fix:** Remove any manual `grid-column` / `grid-row` declarations; rely on auto-flow grid

**Symptom:** Only some images load, others 404
- **Cause:** Missing files in repo or uncommitted
- **Fix:** Verify all files present with `ls images/reviews/`, check `git status`, add and push any untracked files

---

## Quick Reference Commands

```bash
# Copy new images
cp /source/*.jpg /root/.openclaw/workspace/wash-the-city-client/images/reviews/

# Rebuild grid
python3 rebuild_grid.py  # (consider saving the script to a file)

# Commit
git add -A
git commit -m "feat: add new customer photos"
git push origin main
```

---

*Keep this document handy to maintain consistency.*