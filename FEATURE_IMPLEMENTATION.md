# American Accent Features Implementation Guide

## Overview

This implementation provides a comprehensive system for teaching and practicing 12 American accent pronunciation features. The system includes automatic feature detection, detailed educational content, and interactive learning tools.

## Features Implemented

### 1. **Stress** (Word Stress Patterns)
- Primary stress (1): Longest, loudest, clearest vowel
- Secondary stress (2): Medium prominence  
- Unstressed (0): Shortest, often reduced to schwa
- **Examples**: photograph, photography, banana

### 2. **Rhythm** (Stress-Timed Rhythm)
- Stressed syllables occur at regular intervals
- Unstressed syllables compressed between stresses
- Creates characteristic American "bouncy" rhythm
- **Examples**: comfortable, chocolate, interesting

### 3. **Reduction** (Vowel Reduction to Schwa)
- Unstressed vowels → schwa [ə] (AH0)
- Most common vowel sound in American English
- Essential for natural sounding speech
- **Examples**: about, banana, police, potato

### 4. **Linking** (Connecting Words Smoothly)
- Consonant-to-vowel: "an apple" → "a-napple"
- Vowel-to-vowel: Insert /y/ or /w/ glide
- Same consonants: Hold once, not twice
- **Examples**: turn_it_off, pick_up, check_it_out

### 5. **Assimilation** (Sound Changes)
- /t/ + /y/ → /ch/: "won't you" → "won-choo"
- /d/ + /y/ → /j/: "did you" → "di-joo"
- Sounds become more like neighbors
- **Examples**: did_you, would_you, got_you

### 6. **T-Flapping** (T/D Between Vowels)
- T or D between vowels → flap [ɾ]
- Sounds like quick 'd' or Spanish single 'r'
- Makes "writer" and "rider" sound identical
- **Examples**: water, better, city, matter

### 7. **Dark L** (Velarized L)
- L at syllable end → "dark" quality
- Tongue back raises toward velum
- Sounds like "oo-l" or has 'w' quality
- **Examples**: feel, milk, people, bottle

### 8. **Glottalization** (Glottal Stop for T)
- T → glottal stop [ʔ] before N or at word end
- Common in casual American speech
- The T almost disappears
- **Examples**: button, mountain, important, cotton

### 9. **R-Coloring** (American Rhoticity)
- R pronounced in ALL positions
- Vowels before R get r-colored quality
- Tongue curls back (retroflex)
- **Examples**: car, bird, butter, park

### 10. **Aspiration** (Aspirated P/T/K)
- P, T, K at start of stressed syllable → puff of air
- Strong air burst distinguishes from b, d, g
- NOT aspirated after 's' (spin, stop, skip)
- **Examples**: pin, top, cat, potato

### 11. **Nasal Flap** (NT Flap Pattern)
- /nt/ between vowels → flap + nasal
- "Winter" sounds like "winner"
- T may delete entirely in casual speech
- **Examples**: winter, twenty, center, advantage

### 12. **Intonation** (Pitch Patterns)
- Statements: Rise then fall (↗↘)
- Yes/no questions: Rise at end (↗)
- Wh-questions: Fall at end (↘)
- High pitch = emphasis/surprise
- **Examples**: statement patterns, question rises

## System Architecture

### Backend Components

#### 1. Feature Engine (`web_app/backend/core/feature_engine.py`)
- **`FEATURE_DEFINITIONS`**: Complete data for all 12 features
  - Name, description, explanation
  - Rules (3-4 per feature)
  - Examples with ARPAbet + notes (3-6 per feature)
  - Common mistakes (2-3 per feature)

- **`detect_features(word, syllables)`**: Auto-detect which features a word demonstrates
  - Analyzes ARPAbet syllables
  - Returns list of applicable feature IDs
  - Uses pattern matching (stress markers, intervocalic T, etc.)

- **`get_feature_info(feature_id)`**: Get complete details for one feature
- **`get_all_features()`**: Get all feature definitions
- **`get_feature_examples(feature_id)`**: Get example words for a feature
- **`get_feature_summary()`**: Get brief list of all features

#### 2. API Endpoints (`web_app/backend/api/main.py`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/features` | GET | List all features (summary) |
| `/api/features/{feature_id}` | GET | Get detailed info for one feature |
| `/api/features/{feature_id}/examples` | GET | Get example words for one feature |
| `/api/features/detect` | POST | Detect features in a word (auto-analyze) |
| `/api/features/guide/all` | GET | Complete guide (all features with details) |

### Frontend Components

#### 1. Feature Guide UI (`web_app/frontend/templates/index.html`)
- **Feature Guide Button**: Opens modal dialog
- **Feature Selector**: Dropdown with all 12 features
- **Feature Details Display**:
  - Feature name and description
  - Detailed explanation
  - Rules list
  - Examples with pronunciations
  - Common mistakes

#### 2. JavaScript (`web_app/frontend/static/js/app.js`)
- **`openFeatureGuide()`**: Show modal
- **`closeFeatureGuide()`**: Hide modal
- **`loadFeatureInfo()`**: Fetch and display feature details from API

#### 3. Styling (`web_app/frontend/static/css/style.css`)
- Modal overlay with backdrop
- Responsive design (mobile-friendly)
- Color-coded sections (rules, examples, mistakes)
- Highlighted example words

### Data Files

#### `feature_examples.json`
Pre-curated example words organized by feature (10+ examples per feature):
```json
{
  "stress": [...],
  "rhythm": [...],
  "reduction": [...],
  ...
}
```

## How to Use

### For Students

1. **Access Feature Guide**:
   - Open the web app
   - Click "🎓 Feature Guide" button
   - Select a feature from dropdown
   - Read explanation, rules, and examples

2. **Practice Words**:
   - See which features each word demonstrates
   - Use "Get Quiz Word" to practice
   - Use "Search Word" to look up specific words

3. **Add Custom Words**:
   - Search for any word
   - System shows pronunciation
   - Select feature category (dropdown has all 12)
   - Add to quiz for practice

### For Developers

#### Adding a New Feature

1. **Add to `feature_engine.py`**:
```python
FEATURE_DEFINITIONS["new_feature"] = {
    "name": "Feature Name",
    "description": "Brief description",
    "explanation": "Detailed explanation...",
    "rules": ["Rule 1", "Rule 2"],
    "examples": [
        {"word": "example", "syllables": "IH G Z AE1 M P AH0 L", "note": "Note"}
    ],
    "common_mistakes": ["Mistake 1"]
}
```

2. **Add detection logic** to `detect_features()` function

3. **Add to dropdown** in `index.html`:
```html
<option value="new_feature">New Feature - Description</option>
```

4. **Add examples** to `feature_examples.json`

## Testing

### Test Feature Detection
```python
from core.feature_engine import detect_features

word = "water"
syllables = ["W AA1", "DX ER0"]
features = detect_features(word, syllables)
# Returns: ['t_flap', 'r_coloring', 'stress']
```

### Test API Endpoint
```bash
curl http://localhost:8000/api/features/stress
```

### Test in Browser
1. Start app: `start_app.bat`
2. Click "🎓 Feature Guide"
3. Select "Stress"
4. Verify all sections display correctly

## Educational Benefits

1. **Comprehensive Coverage**: All major American accent features
2. **Clear Explanations**: Each feature explained with linguistics terms + plain English
3. **Practical Examples**: Real words with pronunciation breakdowns
4. **Common Mistakes**: Helps students avoid typical errors
5. **Interactive Learning**: Modal interface, searchable, on-demand
6. **Auto-Detection**: System identifies which features apply to any word

## Technical Notes

- **ARPAbet Syllables**: System uses CMUdict format (e.g., "W AA1 DX ER0")
- **Stress Markers**: 0 = unstressed, 1 = primary, 2 = secondary
- **Feature Detection**: Pattern matching on ARPAbet symbols
- **Responsive Design**: Works on mobile, tablet, desktop
- **No External Dependencies**: Pure Python + vanilla JavaScript

## Future Enhancements

- [ ] Audio examples for each feature (record native speaker)
- [ ] Interactive exercises (identify the feature in a word)
- [ ] Progress tracking (which features mastered)
- [ ] Visual diagrams (mouth position, tongue placement)
- [ ] Minimal pairs (writer/rider, pin/bin)
- [ ] Feature-specific quizzes
- [ ] AI-powered pronunciation feedback

## API Response Examples

### GET `/api/features/stress`
```json
{
  "feature_id": "stress",
  "name": "Word Stress",
  "description": "Primary and secondary stress patterns",
  "explanation": "English uses stress timing...",
  "rules": [...],
  "examples": [...],
  "common_mistakes": [...]
}
```

### POST `/api/features/detect`
```json
{
  "word": "water",
  "syllables": ["W AA1", "DX ER0"],
  "features": ["t_flap", "r_coloring", "stress"],
  "count": 3
}
```

## Summary

This implementation provides a production-ready system for teaching American accent features. It combines theoretical knowledge (rules, explanations) with practical application (examples, detection) in an interactive, user-friendly interface.

**Key Files**:
- Backend: `web_app/backend/core/feature_engine.py`
- API: `web_app/backend/api/main.py` (5 new endpoints)
- Frontend: `web_app/frontend/templates/index.html` (modal UI)
- JavaScript: `web_app/frontend/static/js/app.js` (feature guide logic)
- CSS: `web_app/frontend/static/css/style.css` (modal styling)
- Data: `feature_examples.json` (100+ example words)
