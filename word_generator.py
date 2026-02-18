import json
import nltk
from nltk.corpus import cmudict
import random

# Download CMU dict if not already
nltk.download('cmudict')

# Load dictionary
cmu = cmudict.dict()

# Define features and rules
def detect_feature(word, pron):
    pron_str = ' '.join(pron)
    # T-flap: 'T' or 'D' between vowels (simplified)
    if 'T' in pron_str or 'D' in pron_str:
        return 't_flap'
    # Stress: primary stress on first syllable
    if any(char == '1' for char in pron[0]):
        return 'stress'
    # Rhythm: multisyllabic words
    if len(pron) > 2:
        return 'rhythm'
    # Fallback
    return 'other'

# Generate JSON for Firestore
output = []

for word, pron_list in cmu.items():
    # Skip non-alphabetic words
    if not word.isalpha():
        continue
    
    pron = pron_list[0]  # pick first pronunciation
    feature = detect_feature(word, pron)

    # Convert CMU to simplified IPA placeholder (for demo)
    ipa = ''.join(pron).lower()

    # Break into syllables (approximate by vowel groups)
    syllables = []
    current = ''
    vowels = 'AEIOU'
    for p in pron:
        current += p
        if any(v in p for v in vowels):
            syllables.append(current)
            current = ''
    if current:
        syllables.append(current)

    output.append({
        'text': word,
        'clip_id': f'clip{random.randint(1,5)}',  # randomly assign clip for demo
        'syllables': syllables,
        'original_pronunciation': False,
        'ipa_pronunciation': ipa,
        'feature_id': feature
    })

# Save JSON
with open('words_firestore.json', 'w') as f:
    json.dump(output, f, indent=2)

print("Firestore JSON generated:", len(output), "words")
