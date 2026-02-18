"""
Progress Tracking Service - Track user quiz performance
No UI dependencies. Pure business logic.
"""

import json
import os
from abc import ABC, abstractmethod
from typing import Dict, Any


class ProgressTracker(ABC):
    """Base abstract class for progress tracking"""
    
    @abstractmethod
    def save_attempt(self, word: str, correct: bool, feature: str) -> None:
        """Record an answer attempt"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Clear all stats"""
        pass


class FileProgressTracker(ProgressTracker):
    """Save progress to JSON file"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._load_or_init()
    
    def _init_stats(self) -> Dict[str, Any]:
        return {
            "total_rounds": 0,
            "correct": 0,
            "skipped": 0,
            "attempts_per_word": {},
            "per_feature": {},
            "most_missed": {}
        }
    
    def _load_or_init(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.stats = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.stats = self._init_stats()
        else:
            self.stats = self._init_stats()
    
    def save_attempt(self, word: str, correct: bool, feature: str) -> None:
        self.stats["total_rounds"] += 1
        
        if correct:
            self.stats["correct"] += 1
            feat_key = feature if feature != "skip" else "skip"
            self.stats["per_feature"][feat_key] = self.stats["per_feature"].get(feat_key, 0) + 1
        else:
            self.stats["most_missed"][word] = self.stats["most_missed"].get(word, 0) + 1
        
        self._save()
    
    def _save(self):
        os.makedirs(os.path.dirname(self.file_path) or ".", exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
    
    def get_stats(self) -> Dict[str, Any]:
        return self.stats.copy()
    
    def reset(self) -> None:
        self.stats = self._init_stats()
        self._save()


class LocalProgressTracker(ProgressTracker):
    """Store progress in memory (session only)"""
    
    def __init__(self):
        self.stats = self._init_stats()
    
    def _init_stats(self) -> Dict[str, Any]:
        return {
            "total_rounds": 0,
            "correct": 0,
            "skipped": 0,
            "attempts_per_word": {},
            "per_feature": {},
            "most_missed": {}
        }
    
    def save_attempt(self, word: str, correct: bool, feature: str) -> None:
        self.stats["total_rounds"] += 1
        
        if correct:
            self.stats["correct"] += 1
            feat_key = feature if feature != "skip" else "skip"
            self.stats["per_feature"][feat_key] = self.stats["per_feature"].get(feat_key, 0) + 1
        else:
            self.stats["most_missed"][word] = self.stats["most_missed"].get(word, 0) + 1
    
    def get_stats(self) -> Dict[str, Any]:
        return self.stats.copy()
    
    def reset(self) -> None:
        self.stats = self._init_stats()
