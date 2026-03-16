"""Research findings storage and retrieval."""
import json
from pathlib import Path
from typing import Dict, List, Any


class ResearchStorage:
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.research_file = self.output_dir / 'research.json'
        self.data = self._load() or {
            'pain_points': [],
            'quotes': [],
            'objections': [],
            'metrics': [],
            'source_posts': []
        }

    def _load(self) -> Dict[str, Any]:
        if self.research_file.exists():
            with open(self.research_file, 'r') as f:
                return json.load(f)
        return None

    def save(self):
        with open(self.research_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def add_pain_point(self, name: str, count: int, engagement: int, examples: List[str]):
        self.data['pain_points'].append({
            'name': name,
            'count': count,
            'engagement': engagement,
            'examples': examples[:3]  # keep top 3
        })

    def add_quote(self, text: str, upvotes: int, subreddit: str):
        self.data['quotes'].append({
            'text': text,
            'upvotes': upvotes,
            'subreddit': subreddit
        })

    def add_objection(self, text: str, source: str):
        self.data['objections'].append({
            'text': text,
            'source': source
        })

    def add_metric(self, name: str, value: str, source: str):
        self.data['metrics'].append({
            'name': name,
            'value': value,
            'source': source
        })

    def add_source_post(self, title: str, url: str, subreddit: str, score: int):
        self.data['source_posts'].append({
            'title': title,
            'url': url,
            'subreddit': subreddit,
            'score': score
        })

    def get_summary(self) -> str:
        """Generate a concise summary of research for prompts."""
        lines = []
        if self.data['pain_points']:
            lines.append("Pain points found:")
            for pp in self.data['pain_points'][:5]:
                lines.append(f"- {pp['name']} (mentioned {pp['count']} times, {pp['engagement']} engagement)")
        if self.data['quotes']:
            lines.append("\nKey quotes from Reddit:")
            for q in self.data['quotes'][:3]:
                lines.append(f"- \"{q['text']}\" ({q['upvotes']} upvotes, r/{q['subreddit']})")
        if self.data['metrics']:
            lines.append("\nMetrics mentioned:")
            for m in self.data['metrics'][:5]:
                lines.append(f"- {m['name']}: {m['value']} (source: {m['source']})")
        if self.data['objections']:
            lines.append("\nCommon objections:")
            for o in self.data['objections'][:5]:
                lines.append(f"- {o['text']}")
        return '\n'.join(lines)
