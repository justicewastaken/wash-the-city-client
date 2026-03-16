"""Markdown to Notion blocks converter."""
import re
from typing import List, Dict, Any


class MarkdownToNotion:
    """Convert markdown to Notion API block format."""

    @staticmethod
    def convert(markdown: str) -> List[Dict[str, Any]]:
        """Convert markdown string to list of Notion blocks."""
        blocks = []
        lines = markdown.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].rstrip()

            # Headings
            if line.startswith('# '):
                blocks.append(MarkdownToNotion._heading(line[2:], 'heading_1'))
                i += 1
            elif line.startswith('## '):
                blocks.append(MarkdownToNotion._heading(line[3:], 'heading_2'))
                i += 1
            elif line.startswith('### '):
                blocks.append(MarkdownToNotion._heading(line[4:], 'heading_3'))
                i += 1
            # Code blocks
            elif line.startswith('```'):
                # Find closing ```
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                i += 1  # skip closing ```
                blocks.append(MarkdownToNotion._code('\n'.join(code_lines)))
            # Blockquotes
            elif line.startswith('> '):
                quote_lines = [line[2:]]
                i += 1
                while i < len(lines) and lines[i].startswith('> '):
                    quote_lines.append(lines[i][2:])
                    i += 1
                blocks.append(MarkdownToNotion._quote('\n'.join(quote_lines)))
            # Bullet lists
            elif line.startswith('- ') or line.startswith('* '):
                list_items = []
                while i < len(lines) and (lines[i].startswith('- ') or lines[i].startswith('* ')):
                    list_items.append(MarkdownToNotion._clean_line(lines[i][2:]))
                    i += 1
                for item in list_items:
                    blocks.append(MarkdownToNotion._bulleted_list_item(item))
            # Numbered lists (Notion needs numbered_list_item)
            elif re.match(r'^\d+\. ', line):
                list_items = []
                while i < len(lines) and re.match(r'^\d+\. ', lines[i]):
                    list_items.append(MarkdownToNotion._clean_line(re.sub(r'^\d+\. ', '', lines[i])))
                    i += 1
                for item in list_items:
                    blocks.append(MarkdownToNotion._numbered_list_item(item))
            # Paragraphs
            elif line.strip() == '':
                i += 1  # skip blank lines
            else:
                # Collect multi-line paragraph
                para_lines = []
                while i < len(lines) and lines[i].strip() != '' and not lines[i].startswith(('#', '-', '*', '>', '```')):
                    para_lines.append(MarkdownToNotion._clean_line(lines[i]))
                    i += 1
                if para_lines:
                    blocks.append(MarkdownToNotion._paragraph(' '.join(para_lines)))
                else:
                    i += 1

        return blocks

    @staticmethod
    def _heading(text: str, heading_type: str) -> Dict[str, Any]:
        return {
            "object": "block",
            "type": heading_type,
            heading_type: {
                "rich_text": [{"type": "text", "text": {"content": text.strip()}}]
            }
        }

    @staticmethod
    def _paragraph(text: str) -> Dict[str, Any]:
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": text.strip()}}]
            }
        }

    @staticmethod
    def _code(text: str) -> Dict[str, Any]:
        return {
            "object": "block",
            "type": "code",
            "code": {
                "rich_text": [{"type": "text", "text": {"content": text.strip()}}],
                "language": "plain text"
            }
        }

    @staticmethod
    def _quote(text: str) -> Dict[str, Any]:
        return {
            "object": "block",
            "type": "quote",
            "quote": {
                "rich_text": [{"type": "text", "text": {"content": text.strip()}}]
            }
        }

    @staticmethod
    def _bulleted_list_item(text: str) -> Dict[str, Any]:
        return {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": text.strip()}}]
            }
        }

    @staticmethod
    def _numbered_list_item(text: str) -> Dict[str, Any]:
        return {
            "object": "block",
            "type": "numbered_list_item",
            "numbered_list_item": {
                "rich_text": [{"type": "text", "text": {"content": text.strip()}}]
            }
        }

    @staticmethod
    def _clean_line(line: str) -> str:
        """Remove inline markdown formatting (bold, italic, links) for plain text."""
        # Remove **bold**
        line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
        # Remove *italic*
        line = re.sub(r'\*(.*?)\*', r'\1', line)
        # Remove links [text](url)
        line = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', line)
        return line.strip()


# Test
if __name__ == "__main__":
    test_md = """# Hello World

This is a paragraph with **bold** and *italic*.

- Item 1
- Item 2

## Subheading

> A quote

```
code block
```
"""
    blocks = MarkdownToNotion.convert(test_md)
    import json
    print(json.dumps(blocks, indent=2))
