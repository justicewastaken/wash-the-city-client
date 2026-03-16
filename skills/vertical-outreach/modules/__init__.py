"""Modules for vertical-outreach skill."""

from researcher import RedditResearcher
from content_generator import CaseStudyGenerator
from notion_setup import NotionManager
from calculator import CalculatorBuilder
from lead_gen import LeadScraper
from email_sequence import EmailSequenceBuilder

__all__ = [
    'RedditResearcher',
    'CaseStudyGenerator',
    'NotionManager',
    'CalculatorBuilder',
    'LeadScraper',
    'EmailSequenceBuilder'
]
