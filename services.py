"""
Data Service Layer - Abstraction for data sources
This allows easy switching between JSON, database, API, etc. without changing main app
"""

import json
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any


# ============================================================================
# WORD DATA SERVICE - Abstract interface for word data
# ============================================================================

class WordDataSource(ABC):
    """Base class for word data sources - easily swap implementations"""
    
    @abstractmethod
    def get_all_words(self) -> List[Dict[str, Any]]:
        """Get all words"""
        pass
    
    @abstractmethod
    def get_word_by_id(self, word_id: str) -> Dict[str, Any]:
        """Get a specific word"""
        pass
    
    @abstractmethod
    def save_word(self, word: Dict[str, Any]) -> None:
        """Save/update a word"""
        pass


class JSONWordDataSource(WordDataSource):
    """Load words from JSON file - current implementation"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create file if it doesn't exist"""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Word file not found: {self.file_path}")
    
    def get_all_words(self) -> List[Dict[str, Any]]:
        """Load words from JSON file"""
        with open(self.file_path, "r") as f:
            return json.load(f)
    
    def get_word_by_id(self, word_id: str) -> Dict[str, Any]:
        """Find word by text/id"""
        for word in self.get_all_words():
            if word.get("text") == word_id:
                return word
        return None
    
    def save_word(self, word: Dict[str, Any]) -> None:
        """Update word in JSON file"""
        words = self.get_all_words()
        for i, w in enumerate(words):
            if w.get("text") == word.get("text"):
                words[i] = word
                break
        
        with open(self.file_path, "w") as f:
            json.dump(words, f, indent=2)


# Future implementations (just templates):

class APIWordDataSource(WordDataSource):
    """Load words from remote API - for web version"""
    def __init__(self, api_url: str):
        self.api_url = api_url
    
    def get_all_words(self) -> List[Dict[str, Any]]:
        # import requests
        # response = requests.get(f"{self.api_url}/words")
        # return response.json()
        raise NotImplementedError("API implementation pending")


class DatabaseWordDataSource(WordDataSource):
    """Load words from database - for commercialized version"""
    def __init__(self, db_connection_string: str):
        self.db_connection = db_connection_string
    
    def get_all_words(self) -> List[Dict[str, Any]]:
        # cursor.execute("SELECT * FROM words")
        # return cursor.fetchall()
        raise NotImplementedError("Database implementation pending")


# ============================================================================
# PROGRESS/STATS SERVICE - Track user progress
# ============================================================================

class ProgressTracker(ABC):
    """Base class for tracking user progress and stats"""
    
    @abstractmethod
    def save_attempt(self, word: str, correct: bool, feature: str) -> None:
        """Record an attempt"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get current stats"""
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset stats"""
        pass


class LocalProgressTracker(ProgressTracker):
    """Store progress in memory (session only) - current behavior"""
    
    def __init__(self):
        self.stats = {
            "total_rounds": 0,
            "correct": 0,
            "skipped": 0,
            "attempts_per_word": {},
            "per_feature": {},
            "most_missed": {}
        }
    
    def save_attempt(self, word: str, correct: bool, feature: str) -> None:
        """Record an attempt in memory"""
        self.stats["total_rounds"] += 1
        if correct:
            self.stats["correct"] += 1
            self.stats["per_feature"][feature] = self.stats["per_feature"].get(feature, 0) + 1
        else:
            self.stats["most_missed"][word] = self.stats["most_missed"].get(word, 0) + 1
    
    def get_stats(self) -> Dict[str, Any]:
        return self.stats
    
    def reset(self) -> None:
        self.stats = {
            "total_rounds": 0,
            "correct": 0,
            "skipped": 0,
            "attempts_per_word": {},
            "per_feature": {},
            "most_missed": {}
        }


class FileProgressTracker(ProgressTracker):
    """Save progress to JSON file - persists between sessions"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._load_or_init()
    
    def _load_or_init(self):
        """Load existing stats or create new"""
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                self.stats = json.load(f)
        else:
            self.stats = {
                "total_rounds": 0,
                "correct": 0,
                "skipped": 0,
                "attempts_per_word": {},
                "per_feature": {},
                "most_missed": {}
            }
    
    def save_attempt(self, word: str, correct: bool, feature: str) -> None:
        """Record and persist attempt"""
        self.stats["total_rounds"] += 1
        if correct:
            self.stats["correct"] += 1
            self.stats["per_feature"][feature] = self.stats["per_feature"].get(feature, 0) + 1
        else:
            self.stats["most_missed"][word] = self.stats["most_missed"].get(word, 0) + 1
        self._save()
    
    def _save(self):
        """Write stats to file"""
        with open(self.file_path, "w") as f:
            json.dump(self.stats, f, indent=2)
    
    def get_stats(self) -> Dict[str, Any]:
        return self.stats
    
    def reset(self) -> None:
        self.stats = {
            "total_rounds": 0,
            "correct": 0,
            "skipped": 0,
            "attempts_per_word": {},
            "per_feature": {},
            "most_missed": {}
        }
        self._save()


# Future implementations (templates):

class CloudProgressTracker(ProgressTracker):
    """Save to cloud backend - for multi-device sync"""
    def __init__(self, api_url: str, user_id: str):
        self.api_url = api_url
        self.user_id = user_id
    
    def save_attempt(self, word: str, correct: bool, feature: str) -> None:
        # POST to cloud API
        raise NotImplementedError("Cloud backend pending")


# ============================================================================
# AUDIO SERVICE - Abstraction for audio playback
# ============================================================================

class AudioPlayer(ABC):
    """Base class for audio playback - support different formats/methods"""
    
    @abstractmethod
    def play(self, file_path: str) -> None:
        """Play audio file"""
        pass


class WindowsAudioPlayer(AudioPlayer):
    """Windows native audio using os.startfile"""
    
    def play(self, file_path: str) -> None:
        import os
        try:
            os.startfile(file_path)
        except Exception as e:
            raise RuntimeError(f"Could not play audio: {str(e)}")


class WavAudioPlayer(AudioPlayer):
    """Windows WAV files using winsound (synchronous)"""
    
    def play(self, file_path: str) -> None:
        import winsound
        try:
            winsound.PlaySound(file_path, winsound.SND_FILENAME)
        except Exception as e:
            raise RuntimeError(f"Could not play audio: {str(e)}")


# Future implementations (templates):

class WebAudioPlayer(AudioPlayer):
    """Web audio using pygame or similar"""
    def play(self, file_path: str) -> None:
        # import pygame
        # pygame.mixer.music.load(file_path)
        # pygame.mixer.music.play()
        raise NotImplementedError("Web audio pending")
