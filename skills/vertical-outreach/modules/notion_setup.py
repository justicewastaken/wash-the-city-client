"""Notion setup module."""
import requests
from typing import Dict
from markdown_to_notion import MarkdownToNotion


class NotionManager:
    def __init__(self, token: str, parent_page_id: str = None):
        self.token = token
        self.parent_page_id = parent_page_id
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def create_case_study_page(self, content: str, config: Dict, calculator_url: str = None) -> str:
        """Create a case study page under the parent."""
        title = f"{config['business_type'].title()} No-Show Automation: Case Study & Proposal"

        # Convert markdown to Notion blocks
        blocks = MarkdownToNotion.convert(content)

        # Add calculator embed if URL provided
        if calculator_url:
            embed_block = {
                "object": "block",
                "type": "embed",
                "embed": {"url": calculator_url}
            }
            for i, block in enumerate(blocks):
                if block.get('type') in ['heading_1', 'heading_2', 'heading_3']:
                    key = block.get('type')
                    text_content = block.get(key, {}).get('rich_text', [{}])[0].get('text', {}).get('content', '')
                    if 'How Much Are You Missing Out On' in text_content:
                        blocks.insert(i + 1, embed_block)
                        break

        payload = {
            "parent": {"page_id": self.parent_page_id} if self.parent_page_id else {},
            "properties": {
                "title": {
                    "title": [{"text": {"content": title}}]
                }
            },
            "icon": {"type": "emoji", "emoji": "🦷"},
            "children": blocks
        }

        try:
            response = requests.post(
                f"{self.base_url}/pages",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            if response.status_code == 200:
                page_id = response.json()['id']
                return f"https://notion.so/{page_id}"
            else:
                print(f"  ❌ Notion API error: {response.status_code} - {response.text}")
                return "https://notion.so/example-case-study (simulated)"
        except Exception as e:
            print(f"  ❌ Error creating Notion page: {e}")
            return "https://notion.so/example-case-study (simulated)"

    def create_leads_database(self, config: Dict) -> str:
        """Create a leads database under the parent."""
        db_payload = {
            "parent": {"page_id": self.parent_page_id} if self.parent_page_id else {},
            "title": [
                {"text": {"content": f"{config['business_type'].title()} Outreach Leads"}}
            ],
            "icon": {"type": "emoji", "emoji": "📇"},
            "properties": {
                "Practice Name": {"title": {}},
                "Dentist Name": {"rich_text": {}},
                "Email": {"email": {}},
                "City": {"rich_text": {}},
                "Source": {
                    "select": {
                        "options": [
                            {"name": "Web Design Scrape", "color": "default"},
                            {"name": "Yelp", "color": "default"},
                            {"name": "Healthgrades", "color": "default"},
                            {"name": "Zocdoc", "color": "default"},
                            {"name": "Referral", "color": "default"},
                            {"name": "Other", "color": "default"}
                        ]
                    }
                },
                "Status": {
                    "select": {
                        "options": [
                            {"name": "Contacted", "color": "blue"},
                            {"name": "Replied", "color": "yellow"},
                            {"name": "Call Booked", "color": "orange"},
                            {"name": "Closed Won", "color": "green"},
                            {"name": "Closed Lost", "color": "red"}
                        ]
                    }
                },
                "Last Emailed": {"date": {}},
                "Next Follow-up": {"date": {}},
                "Case Study Viewed?": {"checkbox": {}},
                "Calculator Used?": {"checkbox": {}},
                "Calendly Event": {"url": {}},
                "Deal Value": {"number": {"format": "dollar"}},
                "Notes": {"rich_text": {}}
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/databases",
                headers=self.headers,
                json=db_payload,
                timeout=30
            )
            if response.status_code == 200:
                db_id = response.json()['id']
                return f"https://notion.so/{db_id}"
            else:
                print(f"  ❌ Notion API error: {response.status_code} - {response.text}")
                return "https://notion.so/example-database (simulated)"
        except Exception as e:
            print(f"  ❌ Error creating Notion database: {e}")
            return "https://notion.so/example-database (simulated)"
