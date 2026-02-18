"""
Pronunciation Engine - Pure business logic for pronunciation-related operations
No UI or web framework dependencies.
"""

import random
import re
from typing import List


# ARPAbet to IPA phonetic mapping
ARPABET_TO_IPA = {
    # Consonants
    'B': 'b', 'P': 'p', 'T': 't', 'D': 'd', 'K': 'k', 'G': 'ɡ',
    'CH': 'tʃ', 'JH': 'dʒ', 'F': 'f', 'V': 'v', 'TH': 'θ', 'DH': 'ð',
    'S': 's', 'Z': 'z', 'SH': 'ʃ', 'ZH': 'ʒ', 'HH': 'h',
    'M': 'm', 'N': 'n', 'NG': 'ŋ', 'L': 'l', 'R': 'ɹ', 'Y': 'j', 'W': 'w',
    # Vowels
    'AA': 'ɑ', 'AE': 'æ', 'AH': 'ʌ', 'AO': 'ɔ', 'AW': 'aʊ', 'AY': 'aɪ',
    'EH': 'ɛ', 'ER': 'ɝ', 'EY': 'eɪ', 'IH': 'ɪ', 'IY': 'i',
    'OW': 'oʊ', 'OY': 'ɔɪ', 'UH': 'ʊ', 'UW': 'u', 'AX': 'ə'
}


def arpabet_to_ipa(arpabet_str: str) -> str:
    """
    Convert ARPAbet phonemes to IPA format.
    
    Example:
        "B UH1 L AH0 K S" → "/ˈbʌləks/"
    
    Stress markers:
        1 = primary stress (ˈ)
        2 = secondary stress (ˌ)
        0 = no stress
    """
    if not arpabet_str or not arpabet_str.strip():
        return "/"
    
    phonemes = arpabet_str.split()
    ipa_result = []
    
    for phoneme in phonemes:
        stress = ''
        if phoneme and phoneme[-1].isdigit():
            stress = phoneme[-1]
            phoneme_code = phoneme[:-1]
        else:
            phoneme_code = phoneme
        
        ipa_char = ARPABET_TO_IPA.get(phoneme_code, phoneme_code.lower())
        
        if stress == '1':
            ipa_result.append('ˈ' + ipa_char)
        elif stress == '2':
            ipa_result.append('ˌ' + ipa_char)
        else:
            ipa_result.append(ipa_char)
    
    return '/' + ''.join(ipa_result) + '/'


def safe_filename(text: str) -> str:
    """Convert text to safe filename slug"""
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')


def generate_example_sentences(word: str, count: int = 5) -> List[str]:
    """
    Generate simple example sentences with the target word.
    
    This is a basic template-based generator.
    For production, you'd use:
    - A sentence corpus
    - An NLP library
    - A grammar-based generator
    - Pre-written sentences in word data
    """
    if not word or not word.strip():
        return []
    
    word_lower = word.lower()
    word_cap = word[0].upper() + word[1:] if len(word) > 1 else word.upper()
    
    templates = [
        f"The {word_lower} is important.",
        f"I enjoy the {word_lower}.",
        f"She mentioned the {word_lower}.",
        f"They saw a beautiful {word_lower}.",
        f"This {word_lower} is interesting.",
        f"He studied the {word_lower} carefully.",
        f"The {word_cap} was remarkable.",
        f"Can you explain the {word_lower}?",
        f"We discussed the {word_lower} at length.",
        f"The {word_lower} has many uses.",
    ]
    
    return random.sample(templates, min(count, len(templates)))
