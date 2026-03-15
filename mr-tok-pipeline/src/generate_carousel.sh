#!/bin/bash
# Generate 6 TikTok slides with colored backgrounds and text overlay
# Uses ImageMagick convert

OUTPUT_DIR="output"
mkdir -p "$OUTPUT_DIR"

# Colors for each slide: R G B in hex (backgrounds)
declare -a COLORS=(
  "4A90E2"  # Blue (hook)
  "9B59B6"  # Purple (reaction)
  "2ECC71"  # Green (build-up)
  "E67E22"  # Orange (solution)
  "E91E63"  # Pink (showcase)
  "E74C3C"  # Red (CTA)
)

# Top text for each slide
declare -a TOP_TEXTS=(
  "When your dog asks for a second date 😂"
  "The audacity of this man"
  "Sir, my dog lives here. You are the guest."
  "PupJewelry.com — Personalized pet accessories"
  "Handcrafted, custom name jewelry for your furry friend"
  "PupJewelry.com • Link in bio"
)

# Bottom text (CTA) appears on all except maybe last one? Keep consistent.
BOTTOM="PupJewelry.com • Link in bio"

for i in {0..5}; do
  COLOR=${COLORS[$i]}
  TOP=${TOP_TEXTS[$i]}
  OUT="${OUTPUT_DIR}/slide_$((i+1)).png"
  convert -size 1024x1024 "xc:#${COLOR}" \
    -fill white -stroke black -strokewidth 3 -pointsize 52 \
    -gravity North -annotate +0+60 "$TOP" \
    -gravity South -annotate +0+60 "$BOTTOM" \
    "$OUT"
  echo "Created $OUT"
done

echo "All slides generated."
