name: send-image
description: Send an image file in a chat message. Usage: send-image <relative/path/to/image> "optional caption"
os: ["linux", "darwin"]
---

# Send Image Skill

Use this skill to send an image file in the current conversation.

## When to use
- You've generated an image and want to share it with the user
- You need to send a screenshot or diagram
- You want to attach a photo to a message

## How to call
- `send-image ./path/to/image.jpg` — sends the image with no caption
- `send-image ./path/to/image.png "Here's the result"` — sends image with accompanying text

The path must be relative to the workspace root and the file must exist.

## Notes
- Supports PNG, JPEG, GIF, WebP
- Max size: 10MB
- Avoid absolute paths; use relative paths (e.g., `output/result.png`)
