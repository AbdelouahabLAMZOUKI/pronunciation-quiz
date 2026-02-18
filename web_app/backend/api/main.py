"""
FastAPI Backend - REST API Layer
Converts HTTP requests to business logic calls via core modules.
The core modules are completely independent of FastAPI.
"""

import os
import json
import random
from pathlib import Path
from typing import Optional
from urllib.parse import quote
from urllib.request import Request, urlopen

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys

# Add parent directory to path so we can import core modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import pure business logic (no web framework dependencies)
from core.word_service import JSONWordDataSource
from core.progress_service import FileProgressTracker
from core.pronunciation_engine import arpabet_to_ipa, generate_example_sentences
from core.feature_engine import (
    detect_features,
    get_feature_info,
    get_all_features,
    get_feature_examples,
    get_feature_summary
)
import wikipedia
import cmudict

# ============================================================================
# SETUP
# ============================================================================

app = FastAPI(
    title="Pronunciation Quiz API",
    version="2.0.0",
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load configuration - go up to English/ directory where config.json lives
# File is at: web_app/backend/api/main.py
# Config is at: config.json (same level as web_app/)
BASE_DIR = Path(__file__).parent.parent.parent.parent  # up 4 levels: api -> backend -> web_app -> English
CONFIG_PATH = BASE_DIR / "config.json"

if not CONFIG_PATH.exists():
    raise FileNotFoundError(f"config.json not found at {CONFIG_PATH}. Current file: {Path(__file__).absolute()}")

with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

# Initialize core services
word_file = BASE_DIR / CONFIG["data"]["word_file"]
stats_file = BASE_DIR / CONFIG["progress"]["stats_file"]

word_service = JSONWordDataSource(str(word_file))
progress_tracker = FileProgressTracker(str(stats_file))

# Session storage (maps session_id to current_word)
sessions = {}

# CMU Pronouncing Dictionary (ARPAbet lookup)
CMU_DICT = cmudict.dict()


def _fetch_dictionaryapi_ipa(word: str) -> Optional[str]:
    """Fetch IPA from dictionaryapi.dev, if available."""
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{quote(word)}"
        req = Request(url, headers={"User-Agent": "PronunciationQuiz/1.0"})
        with urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        if not isinstance(data, list):
            return None

        for entry in data:
            for phon in entry.get("phonetics", []):
                ipa = phon.get("text")
                if ipa:
                    return ipa

        return None
    except Exception:
        return None


def _fetch_dictionaryapi_definition(word: str) -> Optional[str]:
    """Fetch a short definition from dictionaryapi.dev, if available."""
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{quote(word)}"
        req = Request(url, headers={"User-Agent": "PronunciationQuiz/1.0"})
        with urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        if not isinstance(data, list):
            return None

        for entry in data:
            for meaning in entry.get("meanings", []):
                definitions = meaning.get("definitions", [])
                if definitions:
                    definition = definitions[0].get("definition")
                    if definition:
                        return definition

        return None
    except Exception:
        return None

# ============================================================================
# DATA MODELS
# ============================================================================

class SubmitAnswerRequest(BaseModel):
    session_id: str
    feature: str


class AddWordRequest(BaseModel):
    text: str
    syllables: list
    feature_id: str
    original_pronunciation: Optional[str] = None
    clip_id: Optional[str] = None


# ============================================================================
# HEALTH & CONFIG
# ============================================================================

@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok"}


@app.get("/api/config")
async def get_config():
    """Get public configuration"""
    return {
        "app_name": CONFIG.get("app_name"),
        "version": CONFIG.get("version"),
        "quiz": CONFIG.get("quiz")
    }


# ============================================================================
# WORD ENDPOINTS
# ============================================================================

@app.get("/api/words")
async def list_words():
    """Get all available words"""
    try:
        words = word_service.get_all_words()
        return {"count": len(words), "words": words}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/words/add")
async def add_word(req: AddWordRequest):
    """Add a new word to the quiz"""
    try:
        word_obj = {
            "text": req.text.lower(),
            "syllables": req.syllables,
            "feature_id": req.feature_id,
            "original_pronunciation": req.original_pronunciation or " ".join(req.syllables),
        }
        if req.clip_id:
            word_obj["clip_id"] = req.clip_id
        
        word_service.save_word(word_obj)
        return {"status": "success", "word": word_obj}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# QUIZ ENDPOINTS
# ============================================================================

@app.post("/api/quiz/new-word")
async def new_word(session_id: str = "default"):
    """
    Get a new random word
    REPLACES: Tkinter pick_random_word() function
    """
    try:
        words = word_service.get_all_words()
        if not words:
            raise HTTPException(status_code=404, detail="No words available")
        
        current_word = random.choice(words)
        sessions[session_id] = current_word
        
        # Calculate IPA
        ipa = arpabet_to_ipa(" ".join(current_word["syllables"]))
        
        return {
            "word": {
                **current_word,
                "ipa": ipa
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/quiz/submit-answer")
async def submit_answer(req: SubmitAnswerRequest):
    """
    Submit an answer for the current word
    
    REPLACES: Tkinter handle_guess(feature) button click
    
    This is the KEY endpoint that converts the button click to an HTTP request.
    """
    try:
        if req.session_id not in sessions:
            raise HTTPException(status_code=400, detail="No active word. Call /quiz/new-word first.")
        
        current_word = sessions[req.session_id]
        correct_feature = current_word["feature_id"]
        word_text = current_word["text"]
        feature = req.feature
        
        # Determine correctness
        if feature == "skip":
            correct = False
            feedback = f"⏭ Skipped! Correct: {correct_feature}"
        else:
            correct = feature == correct_feature
            feedback = "✅ Correct!" if correct else "❌ Wrong! Try again."
        
        # Save attempt to progress tracker
        progress_tracker.save_attempt(word_text, correct, feature or "skip")
        
        # Get next word
        words = word_service.get_all_words()
        next_word = random.choice(words)
        sessions[req.session_id] = next_word
        next_ipa = arpabet_to_ipa(" ".join(next_word["syllables"]))
        
        return {
            "correct": correct,
            "correct_feature": correct_feature,
            "guessed_feature": feature,
            "feedback": feedback,
            "next_word": {
                **next_word,
                "ipa": next_ipa
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PRONUNCIATION TOOLS
# ============================================================================

@app.get("/api/pronunciation/ipa/{word}")
async def get_ipa(word: str):
    """Convert ARPAbet syllables to IPA"""
    try:
        word_obj = word_service.get_word_by_id(word)
        if word_obj:
            syllables = word_obj.get("syllables", [])
            ipa = arpabet_to_ipa(" ".join(syllables))
            return {
                "word": word,
                "syllables": syllables,
                "ipa": ipa,
                "source": "local"
            }

        cmu_key = word.lower()
        cmu_arpabet = None
        if cmu_key in CMU_DICT:
            phones = CMU_DICT[cmu_key][0]
            cmu_arpabet = " ".join(phones)

        dictionary_ipa = _fetch_dictionaryapi_ipa(word)
        if dictionary_ipa:
            return {
                "word": word,
                "syllables": [cmu_arpabet] if cmu_arpabet else [],
                "ipa": dictionary_ipa,
                "source": "dictionaryapi"
            }

        if cmu_arpabet:
            ipa = arpabet_to_ipa(cmu_arpabet)
            return {
                "word": word,
                "syllables": [cmu_arpabet],
                "ipa": ipa,
                "source": "cmudict"
            }

        raise HTTPException(status_code=404, detail=f"Word '{word}' not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/pronunciation/sentences/{word}")
async def get_sentences(word: str, count: int = 5):
    """
    Generate example sentences with the word
    
    REPLACES: Tkinter generate_sentences_for_current_word()
    """
    try:
        sentences = generate_example_sentences(word, count)
        return {"word": word, "count": len(sentences), "sentences": sentences}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# STATS ENDPOINTS
# ============================================================================

@app.get("/api/stats")
async def get_stats():
    """
    Get session statistics
    
    REPLACES: Tkinter show_stats()
    """
    try:
        stats = progress_tracker.get_stats()
        
        # Calculate accuracy
        accuracy = 0
        if stats["total_rounds"] > 0:
            accuracy = round((stats["correct"] / stats["total_rounds"]) * 100, 1)
        
        return {
            "stats": stats,
            "accuracy_percent": accuracy
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/stats/reset")
async def reset_stats():
    """Reset all statistics"""
    try:
        progress_tracker.reset()
        return {"status": "success", "message": "Stats reset"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PLACEHOLDER ENDPOINTS (for future implementation)
# ============================================================================

@app.get("/api/reference/definition/{word}")
async def get_definition(word: str):
    """
    Get word definition from Wikipedia
    
    Returns first paragraph of Wikipedia article for the word.
    """
    try:
        wikipedia.set_lang("en")
        summary = wikipedia.summary(word, sentences=2)
        return {
            "word": word,
            "definition": summary,
            "source": "Wikipedia"
        }
    except wikipedia.exceptions.DisambiguationError as e:
        return {
            "word": word,
            "definition": f"Multiple meanings found: {', '.join(e.options[:5])}",
            "source": "Wikipedia"
        }
    except wikipedia.exceptions.PageError:
        fallback = _fetch_dictionaryapi_definition(word)
        if fallback:
            return {
                "word": word,
                "definition": fallback,
                "source": "DictionaryAPI"
            }
        return {
            "word": word,
            "definition": f"Definition not found for '{word}'",
            "source": "Wikipedia"
        }
    except Exception as e:
        fallback = _fetch_dictionaryapi_definition(word)
        if fallback:
            return {
                "word": word,
                "definition": fallback,
                "source": "DictionaryAPI"
            }
        return {
            "word": word,
            "definition": f"Error fetching definition: {str(e)}",
            "source": "Wikipedia"
        }


@app.get("/api/reference/etymology/{word}")
async def get_etymology(word: str):
    """
    Get word etymology from Wikipedia
    
    Searches Wikipedia for etymology information if available.
    """
    try:
        wikipedia.set_lang("en")
        page = wikipedia.page(word)
        content = page.content
        
        # Try to find etymology section
        if "Etymology" in content:
            start = content.find("Etymology")
            end = content.find("\n\n", start)
            etymology_text = content[start:end]
            return {
                "word": word,
                "etymology": etymology_text,
                "source": "Wikipedia"
            }
        else:
            # If no dedicated etymology section, return first paragraph
            return {
                "word": word,
                "etymology": wikipedia.summary(word, sentences=1),
                "source": "Wikipedia - no dedicated etymology section"
            }
    except wikipedia.exceptions.PageError:
        return {
            "word": word,
            "etymology": f"Etymology not found for '{word}'",
            "source": "Wikipedia"
        }
    except Exception as e:
        return {
            "word": word,
            "etymology": f"Error fetching etymology: {str(e)}",
            "source": "Wikipedia"
        }


@app.post("/api/audio/synthesize")
async def synthesize_audio(text: str, output_file: Optional[str] = None):
    """
    Synthesize audio using TTS
    
    Placeholder for now. In production, call Google Cloud TTS or similar.
    """
    return {
        "status": "pending",
        "message": "TTS synthesis - Google Cloud API integration pending",
        "text": text
    }


# ============================================================================
# FEATURE ENDPOINTS (American Accent Features)
# ============================================================================

@app.get("/api/features")
async def list_features():
    """
    Get a summary list of all American accent pronunciation features
    """
    try:
        return {
            "count": len(get_feature_summary()),
            "features": get_feature_summary()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/features/{feature_id}")
async def get_feature(feature_id: str):
    """
    Get detailed information about a specific pronunciation feature
    Includes: explanation, rules, examples, common mistakes
    """
    try:
        feature_info = get_feature_info(feature_id)
        if not feature_info:
            raise HTTPException(status_code=404, detail=f"Feature '{feature_id}' not found")
        
        return {
            "feature_id": feature_id,
            **feature_info
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/features/{feature_id}/examples")
async def get_feature_example_words(feature_id: str):
    """
    Get example words that demonstrate a specific pronunciation feature
    """
    try:
        examples = get_feature_examples(feature_id)
        if not examples:
            raise HTTPException(status_code=404, detail=f"Feature '{feature_id}' not found or has no examples")
        
        return {
            "feature_id": feature_id,
            "count": len(examples),
            "examples": examples
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/features/detect")
async def detect_word_features(word: str, syllables: list):
    """
    Analyze a word and detect which pronunciation features it demonstrates
    
    Args:
        word: The word text
        syllables: List of ARPAbet syllables
        
    Returns:
        List of feature IDs that apply to this word
    """
    try:
        detected = detect_features(word, syllables)
        return {
            "word": word,
            "syllables": syllables,
            "features": detected,
            "count": len(detected)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/features/guide/all")
async def get_complete_feature_guide():
    """
    Get the complete pronunciation feature guide with all details
    Perfect for generating documentation or a learning reference
    """
    try:
        all_features = get_all_features()
        return {
            "total_features": len(all_features),
            "features": all_features
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
