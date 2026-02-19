"""
Intelligent Learning Companion System

A modular learning system with:
- Smart knowledge base with semantic deduplication
- Learning records with Ebbinghaus forgetting curve
- Multi-role coordination for structured learning
"""

from .smart_knowledge_base import SmartKnowledgeBase
from .learning_records import LearningRecords
from .coordination_manager import CoordinationManager

__version__ = "1.0.0"
__all__ = ["SmartKnowledgeBase", "LearningRecords", "CoordinationManager"]
