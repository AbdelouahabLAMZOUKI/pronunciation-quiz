"""
American Accent Feature Detection and Educational Engine
Provides detection rules, examples, and explanations for each pronunciation feature
"""

import re
from typing import Dict, List, Any, Optional


# ============================================================================
# FEATURE DEFINITIONS
# ============================================================================

FEATURE_DEFINITIONS = {
    "stress": {
        "name": "Word Stress",
        "description": "Primary and secondary stress patterns in multi-syllable words",
        "explanation": """English uses stress timing - stressed syllables are longer, louder, and higher pitch. 
        Stress changes word meaning (e.g., 'REcord' noun vs 'reCORD' verb).""",
        "rules": [
            "Primary stress (1): Longest, loudest, clearest vowel",
            "Secondary stress (2): Medium prominence",
            "Unstressed (0): Shortest, often reduced to schwa"
        ],
        "examples": [
            {"word": "photograph", "syllables": "F OW1 T AH0 G R AE2 F", "note": "Primary on 1st, secondary on 3rd"},
            {"word": "photography", "syllables": "F AH0 T AA1 G R AH0 F IY0", "note": "Stress shifts to 2nd syllable"},
            {"word": "banana", "syllables": "B AH0 N AE1 N AH0", "note": "Only middle syllable stressed"}
        ],
        "common_mistakes": [
            "Equal stress on all syllables (sounds robotic)",
            "Wrong syllable stressed (changes meaning)"
        ]
    },
    
    "rhythm": {
        "name": "Rhythm & Timing",
        "description": "English stress-timed rhythm (vs syllable-timed languages)",
        "explanation": """English rhythm is stress-timed: stressed syllables occur at regular intervals,
        while unstressed syllables are compressed. This creates a 'bouncy' rhythm.""",
        "rules": [
            "Stressed syllables: Equal time intervals",
            "Unstressed syllables: Squeezed between stresses",
            "Content words (nouns, verbs) stressed; function words (the, a, to) reduced"
        ],
        "examples": [
            {"word": "comfortable", "syllables": "K AH1 M F ER0 T AH0 B AH0 L", "note": "COMF-ta-ble (3 syllables sound like 2)"},
            {"word": "chocolate", "syllables": "CH AO1 K AH0 L AH0 T", "note": "CHOC-late (3→2 syllables)"},
            {"word": "interesting", "syllables": "IH1 N T ER0 EH0 S T IH0 NG", "note": "IN-tres-ting (compressed middle)"}
        ],
        "common_mistakes": [
            "Pronouncing every syllable equally (syllable-timed)",
            "Too slow, mechanically pronouncing all vowels"
        ]
    },
    
    "reduction": {
        "name": "Vowel Reduction",
        "description": "Unstressed vowels reduce to schwa (ə) or disappear completely",
        "explanation": """In natural American speech, unstressed vowels often reduce to schwa [ə] (the 'uh' sound).
        This is the most common vowel sound in English!""",
        "rules": [
            "Unstressed syllables: Full vowel → schwa (AH0)",
            "Function words: 'to' → tuh, 'can' → kn, 'and' → nd",
            "Helps maintain stress-timed rhythm"
        ],
        "examples": [
            {"word": "about", "syllables": "AH0 B AW1 T", "note": "'a' reduces to schwa"},
            {"word": "banana", "syllables": "B AH0 N AE1 N AH0", "note": "Both unstressed vowels = schwa"},
            {"word": "police", "syllables": "P AH0 L IY1 S", "note": "'po' reduces from 'poh' to 'puh'"},
            {"word": "photograph", "syllables": "F OW1 T AH0 G R AE2 F", "note": "Middle 'o' → schwa"}
        ],
        "common_mistakes": [
            "Pronouncing full vowels in unstressed syllables",
            "Using native language vowels instead of schwa"
        ]
    },
    
    "linking": {
        "name": "Linking & Liaison",
        "description": "Connecting words together smoothly in connected speech",
        "explanation": """Americans link words together without pauses. Consonants link to following vowels,
        and similar sounds blend together.""",
        "rules": [
            "Consonant-to-vowel: 'an apple' → 'a-napple'",
            "Vowel-to-vowel: Insert /y/ or /w/ glide ('see it' → 'see-yit')",
            "Same consonants: Hold once, not twice ('good day' → 'goo-day')"
        ],
        "examples": [
            {"word": "check_it_out", "syllables": "CH EH1 K IH0 T AW1 T", "note": "che-ki-tout (smooth connection)"},
            {"word": "turn_it_off", "syllables": "T ER1 N IH0 T AO1 F", "note": "tur-ni-toff"},
            {"word": "pick_up", "syllables": "P IH1 K AH1 P", "note": "pi-kup (k links to next syllable)"}
        ],
        "common_mistakes": [
            "Pausing between every word",
            "Pronouncing consonants twice ('good day' as 'good-d-day')"
        ]
    },
    
    "assimilation": {
        "name": "Sound Assimilation",
        "description": "Sounds change to become more like neighboring sounds",
        "explanation": """Adjacent sounds influence each other. Common assimilations include:
        /t/ + /y/ → /ch/, /d/ + /y/ → /j/, /n/ changes place before different consonants.""",
        "rules": [
            "/t/ + /y/ → 'ch': 'won't you' → 'won-choo'",
            "/d/ + /y/ → 'j': 'did you' → 'di-joo'",
            "/n/ assimilates: 'in Paris' → 'im Paris' (n→m before p)"
        ],
        "examples": [
            {"word": "won't_you", "syllables": "W OW1 N CH UW0", "note": "t+y → ch sound"},
            {"word": "did_you", "syllables": "D IH1 JH UW0", "note": "d+y → j sound"},
            {"word": "got_you", "syllables": "G AA1 CH UW0", "note": "gotcha (t+y → ch)"},
            {"word": "would_you", "syllables": "W UH1 JH UW0", "note": "wou-joo (d+y → j)"}
        ],
        "common_mistakes": [
            "Pronouncing 't' and 'y' separately",
            "Over-enunciating in fast speech"
        ]
    },
    
    "t_flap": {
        "name": "T/D Flapping",
        "description": "T and D between vowels become a quick tap (like Spanish 'r')",
        "explanation": """When T or D appears between two vowels (or before syllabic L/R),
        it becomes a flap [ɾ] - like the 'r' in Spanish 'caro'. This makes 'writer' and 'rider' sound identical!""",
        "rules": [
            "T/D between vowels → flap: 'water' → 'wader'",
            "After stressed vowel works best",
            "Sounds like quick 'd' or Spanish single 'r'"
        ],
        "examples": [
            {"word": "water", "syllables": "W AA1 DX ER0", "note": "t → flap (sounds like 'wader')"},
            {"word": "better", "syllables": "B EH1 DX ER0", "note": "tt → single flap"},
            {"word": "city", "syllables": "S IH1 DX IY0", "note": "t → flap ('siddy')"},
            {"word": "matter", "syllables": "M AE1 DX ER0", "note": "tt → flap"},
            {"word": "party", "syllables": "P AA1 R DX IY0", "note": "t → flap"}
        ],
        "common_mistakes": [
            "Pronouncing clear 't' sound",
            "Making it too strong (should be very quick)"
        ]
    },
    
    "dark_l": {
        "name": "Dark L (Velarization)",
        "description": "L at syllable end becomes 'dark' - tongue back raised",
        "explanation": """English has two L sounds: 'light L' [l] at syllable start ('like', 'love')
        and 'dark L' [ɫ] at syllable end ('feel', 'milk'). Dark L sounds deeper, like an 'oo-l' or 'w' sound.""",
        "rules": [
            "Syllable-initial: Light L (tongue tip touches)",
            "Syllable-final: Dark L (back of tongue raises toward velum)",
            "Think: 'fee-oo' instead of 'feel'"
        ],
        "examples": [
            {"word": "feel", "syllables": "F IY1 L", "note": "Dark L at end (fee-ul)"},
            {"word": "milk", "syllables": "M IH1 L K", "note": "Dark L before K"},
            {"word": "people", "syllables": "P IY1 P AH0 L", "note": "Final L is dark"},
            {"word": "bottle", "syllables": "B AA1 T AH0 L", "note": "Dark L, often syllabic"},
            {"word": "table", "syllables": "T EY1 B AH0 L", "note": "Dark L at end"}
        ],
        "common_mistakes": [
            "Using light L everywhere",
            "Not raising back of tongue for dark L"
        ]
    },
    
    "glottalization": {
        "name": "Glottal Stop (T-glottalization)",
        "description": "T becomes glottal stop [ʔ] before N or at word end",
        "explanation": """Instead of releasing 't', the airflow stops at the glottis (vocal cords).
        Common in words like 'button', 'mountain', 'important'. The T almost disappears!""",
        "rules": [
            "T + N: 'button' → 'bu'on' (glottal stop replaces t)",
            "T at syllable end: 'cat' → 'ca?' (often before pause)",
            "Very common in American casual speech"
        ],
        "examples": [
            {"word": "button", "syllables": "B AH1 T N", "note": "T → glottal stop (bu'n)"},
            {"word": "mountain", "syllables": "M AW1 N T N", "note": "T → glottal stop (moun'n)"},
            {"word": "important", "syllables": "IH0 M P AO1 R T N T", "note": "T+N → glottal stop"},
            {"word": "cotton", "syllables": "K AA1 T N", "note": "co'on (dropped T)"},
            {"word": "sentence", "syllables": "S EH1 N T N S", "note": "sen'nce"}
        ],
        "common_mistakes": [
            "Pronouncing clear 't' sound",
            "Over-enunciating in casual contexts"
        ]
    },
    
    "r_coloring": {
        "name": "R-coloring (Rhoticity)",
        "description": "American English pronounces R everywhere; vowels before R are 'r-colored'",
        "explanation": """American English is rhotic - we pronounce R in all positions.
        Vowels before R get 'r-colored' quality (tongue curls back). This is a major American accent marker!""",
        "rules": [
            "R after vowel: Always pronounced ('car', 'bird', 'hear')",
            "Vowel + R → r-colored vowel (retroflex)",
            "Tongue tip curls back toward roof of mouth"
        ],
        "examples": [
            {"word": "car", "syllables": "K AA1 R", "note": "Strong R at end"},
            {"word": "bird", "syllables": "B ER1 D", "note": "ER = r-colored vowel"},
            {"word": "butter", "syllables": "B AH1 DX ER0", "note": "Final ER is r-colored"},
            {"word": "park", "syllables": "P AA1 R K", "note": "R before K pronounced"},
            {"word": "lawyer", "syllables": "L AO1 Y ER0", "note": "Final R strong"}
        ],
        "common_mistakes": [
            "Dropping R (British style: 'cah' instead of 'car')",
            "Not curling tongue back enough",
            "German/French-style uvular R"
        ]
    },
    
    "aspiration": {
        "name": "Aspiration (P/T/K)",
        "description": "Voiceless stops P, T, K release with strong air burst at word/syllable start",
        "explanation": """At the beginning of stressed syllables, P, T, and K are pronounced with
        a strong puff of air (aspiration). Hold your hand in front of your mouth - you should feel the air!""",
        "rules": [
            "p, t, k at start of stressed syllable → aspirated [pʰ tʰ kʰ]",
            "After s: not aspirated ('spin', 'stop', 'skip')",
            "Strong air burst distinguishes from b, d, g"
        ],
        "examples": [
            {"word": "pin", "syllables": "P IH1 N", "note": "Strong aspiration on P"},
            {"word": "top", "syllables": "T AA1 P", "note": "Aspirated T at start"},
            {"word": "cat", "syllables": "K AE1 T", "note": "Aspirated K"},
            {"word": "potato", "syllables": "P AH0 T EY1 T OW0", "note": "2nd P and T aspirated"},
            {"word": "car", "syllables": "K AA1 R", "note": "Strong K aspiration"}
        ],
        "common_mistakes": [
            "No aspiration (sounds like b, d, g)",
            "Too weak - should feel air burst",
            "Aspirating after 's' (should be unaspirated)"
        ]
    },
    
    "nasal_flap": {
        "name": "Nasal Flap (/nt/ cluster)",
        "description": "NT sequence often becomes flap + nasal, especially in fast speech",
        "explanation": """The sequence /nt/ between vowels often changes: the T becomes a flap,
        and nasalization spreads. 'Winter' sounds like 'winner', 'twenty' like 'twenny'.""",
        "rules": [
            "/nt/ between vowels → flap + nasal",
            "T may delete entirely in casual speech",
            "Previous vowel becomes nasalized"
        ],
        "examples": [
            {"word": "winter", "syllables": "W IH1 N DX ER0", "note": "nt → n+flap (winner)"},
            {"word": "twenty", "syllables": "T W EH1 N DX IY0", "note": "nt → flap (twenny)"},
            {"word": "center", "syllables": "S EH1 N DX ER0", "note": "nt → n+flap"},
            {"word": "international", "syllables": "IH2 N DX ER0 N AE1 SH AH0 N AH0 L", "note": "nt → flap"},
            {"word": "advantage", "syllables": "AH0 D V AE1 N DX IH0 JH", "note": "nt → flap"}
        ],
        "common_mistakes": [
            "Clear T pronunciation in casual speech",
            "Not nasalizing the preceding vowel"
        ]
    },
    
    "intonation": {
        "name": "Intonation Patterns",
        "description": "Pitch changes that signal statement, question, emphasis, or emotion",
        "explanation": """American English uses pitch patterns (intonation) to convey meaning beyond words.
        Rising pitch = questions/uncertainty. Falling pitch = statements/certainty. High pitch = emphasis.""",
        "rules": [
            "Statements: Rise then fall (↗↘) on stressed syllable",
            "Yes/no questions: Rise at end (↗)",
            "Wh-questions: Fall at end (↘)",
            "List items: Rise (↗) until last item falls (↘)"
        ],
        "examples": [
            {"word": "statement", "syllables": "S T EY1 T M AH0 N T", "note": "Pitch: ↗ on STAY, ↘ on ment"},
            {"word": "question", "syllables": "K W EH1 S CH AH0 N", "note": "Pitch rises ↗ at end for yes/no Q"},
            {"word": "really", "syllables": "R IY1 L IY0", "note": "High pitch = surprise/emphasis"},
            {"word": "understand", "syllables": "AH2 N D ER0 S T AE1 N D", "note": "Pitch peaks on -STAND"}
        ],
        "common_mistakes": [
            "Flat/monotone speech (no pitch variation)",
            "Rising on statements (sounds uncertain)",
            "Falling on yes/no questions (sounds rude)"
        ]
    },
    
    "contractions": {
        "name": "Informal Contractions",
        "description": "Casual speech reductions: gonna, wanna, gotta, etc.",
        "explanation": """In fast, casual American English, common word combinations get reduced to 
        shorter forms. These aren't written in formal contexts but are extremely common in spoken English.
        Native speakers use these unconsciously in everyday conversation.""",
        "rules": [
            "going to → gonna (only before verbs, not locations)",
            "want to → wanna; got to → gotta; have to → hafta",
            "let me → lemme; give me → gimme",
            "out of → outta; kind of → kinda; sort of → sorta",
            "Used in casual/informal speech, not formal writing"
        ],
        "examples": [
            {"word": "going_to", "syllables": "G AH1 N AH0", "note": "gonna - 'I'm gonna go'"},
            {"word": "want_to", "syllables": "W AA1 N AH0", "note": "wanna - 'I wanna try'"},
            {"word": "got_to", "syllables": "G AA1 T AH0", "note": "gotta - 'I gotta leave'"},
            {"word": "have_to", "syllables": "HH AE1 F T AH0", "note": "hafta - 'You hafta see this'"},
            {"word": "let_me", "syllables": "L EH1 M IY0", "note": "lemme - 'Lemme help you'"},
            {"word": "give_me", "syllables": "G IH1 M IY0", "note": "gimme - 'Gimme that'"}
        ],
        "common_mistakes": [
            "Using 'gonna' before places (✗ 'gonna store' → ✓ 'going to the store')",
            "Writing these forms in formal emails or essays",
            "Over-pronouncing in casual contexts ('going to' instead of 'gonna')"
        ]
    }
}


# ============================================================================
# FEATURE DETECTION 
# ============================================================================

def detect_features(word: str, syllables: List[str]) -> List[str]:
    """
    Analyze a word's pronunciation and detect which features it demonstrates
    Returns: List of feature_ids that apply to this word
    """
    features = []
    syllable_str = " ".join(syllables)
    
    # Stress detection
    if "1" in syllable_str or "2" in syllable_str:
        if len(syllables) > 1:
            features.append("stress")
    
    # Reduction detection (schwa AH0 in unstressed syllables)
    if "AH0" in syllable_str:
        features.append("reduction")
    
    # T-flapping detection (DX or T between vowels)
    vowels = ["AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY", "IH", "IY", "OW", "OY", "UH", "UW"]
    syllable_flat = syllable_str.replace("0", "").replace("1", "").replace("2", "")
    if "DX" in syllable_str or _has_intervocalic_t(syllable_flat, vowels):
        features.append("t_flap")
    
    # Dark L detection (L at syllable end)
    if re.search(r'L\s*$|L\s+[BCDFGHJKLMNPQRSTVWXYZ]', syllable_str):
        features.append("dark_l")
    
    # Glottalization (T before N)
    if "T N" in syllable_str or "T M" in syllable_str:
        features.append("glottalization")
    
    # R-coloring (ER vowel or R after vowel)
    if "ER" in syllable_str or "R" in syllable_str:
        features.append("r_coloring")
    
    # Aspiration (word-initial P, T, K)
    if syllable_str.startswith(("P ", "T ", "K ")):
        features.append("aspiration")
    
    # Nasal flap (NT sequence)
    if "N T" in syllable_str or "N DX" in syllable_str:
        features.append("nasal_flap")
    
    # Linking (compound words or phrasal words with underscore)
    if "_" in word:
        features.append("linking")
    
    # Contractions (informal reductions)
    contraction_words = ["gonna", "wanna", "gotta", "hafta", "hasta", "lemme", "gimme", 
                         "kinda", "sorta", "outta", "dunno", "cuz", "cause"]
    if any(c in word.lower() for c in contraction_words):
        features.append("contractions")
    # Also detect by common patterns
    if "_to" in word.lower() or "_me" in word.lower() or "_of" in word.lower():
        features.append("contractions")
    
    # Rhythm (3+ syllables)
    if len(syllables) >= 3:
        features.append("rhythm")
    
    return list(set(features))  # Remove duplicates


def _has_intervocalic_t(syllables: str, vowels: List[str]) -> bool:
    """Check if T appears between two vowels"""
    for i, char in enumerate(syllables.split()):
        if char == "T":
            # Check if preceded and followed by vowels
            parts = syllables.split()
            if i > 0 and i < len(parts) - 1:
                prev_is_vowel = any(parts[i-1].startswith(v) for v in vowels)
                next_is_vowel = any(parts[i+1].startswith(v) for v in vowels)
                if prev_is_vowel and next_is_vowel:
                    return True
    return False


# ============================================================================
# FEATURE QUERIES
# ============================================================================

def get_feature_info(feature_id: str) -> Optional[Dict[str, Any]]:
    """Get detailed information about a specific feature"""
    return FEATURE_DEFINITIONS.get(feature_id)


def get_all_features() -> Dict[str, Dict[str, Any]]:
    """Get all feature definitions"""
    return FEATURE_DEFINITIONS


def get_feature_examples(feature_id: str) -> List[Dict[str, str]]:
    """Get example words for a specific feature"""
    feature = FEATURE_DEFINITIONS.get(feature_id)
    if feature:
        return feature.get("examples", [])
    return []


def get_feature_summary() -> List[Dict[str, str]]:
    """Get a simple list of all features with brief descriptions"""
    return [
        {
            "id": fid,
            "name": fdata["name"],
            "description": fdata["description"]
        }
        for fid, fdata in FEATURE_DEFINITIONS.items()
    ]
