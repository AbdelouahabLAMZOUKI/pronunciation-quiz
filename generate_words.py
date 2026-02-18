import json
import nltk
from nltk.corpus import cmudict
import random

# Download CMU dictionary (only first time)
nltk.download('cmudict')

cmu = cmudict.dict()

def detect_feature(word, pron):
    pron_str = ' '.join(pron)

    if 'T' in pron_str or 'D' in pron_str:
        return 't_flap'

    if any('1' in p for p in pron):
        return 'stress'

    if len(pron) > 2:
        return 'rhythm'

    if len(word) > 6:
        return 'intonation'

    return 'assimilation'


def get_syllables(pron):
    syllables = []
    current = ''
    vowels = ['A', 'E', 'I', 'O', 'U']

    for p in pron:
        current += p + ' '
        if any(v in p for v in vowels):
            syllables.append(current.strip())
            current = ''

    if current:
        syllables.append(current.strip())

    return syllables


all_words = []

for word, pron_list in cmu.items():
    if not word.isalpha():
        continue

    pron = pron_list[0]
    feature = detect_feature(word, pron)

    ipa = ''.join(pron).lower()
    syllables = get_syllables(pron)

    all_words.append({
        "text": word,
        "clip_id": f"clip{random.randint(1,10)}",
        "syllables": syllables,
        "original_pronunciation": False,
        "ipa_pronunciation": ipa,
        "feature_id": feature
    })

# Create test batch
test_batch = random.sample(all_words, 300)

with open("test_words.json", "w") as f:
    json.dump(test_batch, f, indent=2)

with open("all_words_firestore.json", "w") as f:
    json.dump(all_words, f, indent=2)

print("Files generated successfully.")
