"""
Word Data Service - Abstraction for word data sources
No UI dependencies. Pure data access abstraction.
"""

import json
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class WordDataSource(ABC):
    """Base abstract class for word data sources"""
    
    @abstractmethod
    def get_all_words(self) -> List[Dict[str, Any]]:
        """Retrieve all words"""
        pass
    
    @abstractmethod
    def get_word_by_id(self, word_id: str) -> Dict[str, Any]:
        """Get a single word by text/id"""
        pass
    
    @abstractmethod
    def save_word(self, word: Dict[str, Any]) -> None:
        """Persist a word"""
        pass


class JSONWordDataSource(WordDataSource):
    """Load/save words from JSON file"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Word file not found: {file_path}")
    
    def get_all_words(self) -> List[Dict[str, Any]]:
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def get_word_by_id(self, word_id: str) -> Dict[str, Any]:
        for word in self.get_all_words():
            if word.get("text") == word_id.lower():
                return word
        return None
    
    def save_word(self, word: Dict[str, Any]) -> None:
        words = self.get_all_words()
        found = False
        
        for i, w in enumerate(words):
            if w.get("text") == word.get("text").lower():
                words[i] = word
                found = True
                break
        
        if not found:
            words.append(word)
        
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(words, f, indent=2, ensure_ascii=False)
