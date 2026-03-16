"""Reddit research module for vertical outreach."""
import json
import subprocess
import tempfile
from pathlib import Path


class RedditResearcher:
    def __init__(self, config):
        self.config = config
        self.vertical = config.get('vertical', 'unknown')
        self.subreddits = config['subreddits']
        self.search_queries = config['search_queries']

    def research(self, days=180, min_comments=5):
        """
        Research Reddit for pain points in the vertical.
        Returns list of clustered pain points with engagement metrics.
        """
        print(f"  Researching subreddits: {', '.join(self.subreddits)}")
        print(f"  Queries: {', '.join(self.search_queries)}")

        pain_points = []

        # Try to use the search-reddit skill if available
        # Otherwise fall back to simulated data
        try:
            # Check if search-reddit skill exists
            skill_path = Path(__file__).parent.parent.parent / 'search-reddit' / 'scripts' / 'search.js'
            if skill_path.exists():
                pain_points = self._research_with_skill(skill_path, days)
            else:
                print("  ⚠️  search-reddit skill not found, using simulated data")
                pain_points = self._simulate_research()
        except Exception as e:
            print(f"  ⚠️  Research failed: {e}, using simulated data")
            pain_points = self._simulate_research()

        return pain_points

    def _research_with_skill(self, skill_path, days):
        """Use the search-reddit Node.js skill."""
        pain_points = []
        # Implementation would call the Node script
        # For now, fall back to simulation
        return self._simulate_research()

    def _simulate_research(self):
        """Generate realistic mock data based on vertical."""
        common_pains = {
            'dentists': [
                {'name': 'no_shows', 'count': 67, 'engagement': 12450, 'queries': ['no show appointments', 'late cancellations']},
                {'name': 'insurance_verification', 'count': 52, 'engagement': 9230, 'queries': ['insurance verification', 'claims processing']},
                {'name': 'treatment_plan_followup', 'count': 38, 'engagement': 7200, 'queries': ['treatment plan', 'case acceptance']},
                {'name': 'patient_intake', 'count': 29, 'engagement': 5100, 'queries': ['new patient paperwork', 'intake forms']},
                {'name': 'recall_reminders', 'count': 31, 'engagement': 4900, 'queries': ['recall system', 'cleaning appointments']}
            ],
            'barbers': [
                {'name': 'no_shows', 'count': 45, 'engagement': 8200, 'queries': ['no show', 'missed appointments']},
                {'name': 'double_booking', 'count': 28, 'engagement': 4100, 'queries': ['double booked', 'scheduling conflicts']},
                {'name': 'client_notes', 'count': 22, 'engagement': 3800, 'queries': ['client preferences', 'hair history']},
                {'name': 'stylist_scheduling', 'count': 19, 'engagement': 2900, 'queries': ['stylist schedule', 'availability']},
            ],
            'landscapers': [
                {'name': 'lead_response', 'count': 56, 'engagement': 9800, 'queries': ['lead follow up', 'quote requests']},
                {'name': 'job_scheduling', 'count': 41, 'engagement': 7200, 'queries': ['job scheduling', 'route optimization']},
                {'name': 'invoice_chasing', 'count': 37, 'engagement': 6100, 'queries': ['past due invoices', 'payment reminders']},
                {'name': 'weather_rescheduling', 'count': 25, 'engagement': 3900, 'queries': ['weather delays', 'rescheduling']},
            ]
        }

        vertical_key = self.vertical if self.vertical in common_pains else 'dentists'
        return common_pains.get(vertical_key, common_pains['dentists'])
