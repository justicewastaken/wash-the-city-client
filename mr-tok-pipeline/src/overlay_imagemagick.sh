#!/bin/bash
set -e
INPUT="output/base_image.jpg"
OUTPUT="output/final_imagemagick.png"
TOP="When your dog asks for a second date 😂"
BOTTOM="PupJewelry.com • Link in bio"

convert "$INPUT" \
  -gravity North -pointsize 52 -fill white -stroke black -strokewidth 3 -annotate +0+60 "$TOP" \
  -gravity South -pointsize 52 -fill white -stroke black -strokewidth 3 -annotate +0+60 "$BOTTOM" \
  "$OUTPUT"

echo "Saved final slide: $OUTPUT"
