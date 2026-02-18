"""
Flask Frontend + API Server
Serves HTML/CSS/JS frontend and handles all API requests
No FastAPI/Pydantic - just pure Flask and core business logic
"""

from flask import Flask, render_template, send_from_directory, request, jsonify
import os
import sys
from pathlib import Path

# Add backend to path so we can import core modules
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

# Import core business logic (no framework dependencies)
from core.word_service import JSONWordDataSource
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

app = Flask(__name__, 
    template_folder=os.path.join(os.path.dirname(__file__), 'frontend', 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), 'frontend', 'static'))

# Enable CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

PORT = int(os.environ.get('PORT', 10000))

# Initialize data source
BASE_DIR = Path(__file__).parent.parent  # go up to web_app/..
DATA_FILE = BASE_DIR / 'words_firestore.json'
word_source = JSONWordDataSource(str(DATA_FILE))

# ============================================================================
# FRONTEND ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve the main app"""
    return render_template('index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files, fallback to index.html for SPA routing"""
    static_dir = os.path.join(os.path.dirname(__file__), 'frontend', 'static')
    file_path = os.path.join(static_dir, path)
    
    if os.path.isfile(file_path):
        return send_from_directory(static_dir, path)
    
    # SPA routing - serve index.html
    return render_template('index.html')

# ============================================================================
# API ROUTES - QUIZ
# ============================================================================

@app.route('/api/quiz/new-word', methods=['POST'])
def new_word():
    """Get a random word from quiz"""
    try:
        session_id = request.args.get('session_id', 'default')
        word_data = word_source.get_random_word()
        
        if not word_data:
            return jsonify({'error': 'No words available'}), 404
        
        return jsonify({
            'word': {
                'text': word_data.get('word'),
                'syllables': word_data.get('syllables', []),
                'ipa': word_data.get('ipa', ''),
                'original_pronunciation': ' '.join(word_data.get('syllables', []))
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# API ROUTES - PRONUNCIATION
# ============================================================================

@app.route('/api/pronunciation/ipa/<word>')
def get_ipa(word):
    """Get IPA for a word"""
    try:
        # Try to get from CMU dict
        d = cmudict.dict()
        if word.lower() in d:
            arpabet = d[word.lower()][0]
            ipa = arpabet_to_ipa(arpabet)
            return jsonify({'ipa': ipa})
        
        return jsonify({'ipa': ''}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pronunciation/sentences/<word>')
def get_sentences(word):
    """Get example sentences for a word"""
    try:
        count = request.args.get('count', 5, type=int)
        sentences = generate_example_sentences(word, count=count)
        return jsonify({'sentences': sentences})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# API ROUTES - REFERENCE
# ============================================================================

@app.route('/api/reference/definition/<word>')
def get_definition(word):
    """Get dictionary definition for a word"""
    try:
        definition = wikipedia.summary(word, sentences=2, auto_suggest=False)
        return jsonify({'definition': definition})
    except Exception as e:
        return jsonify({'definition': f'Could not find definition for "{word}"'}), 200

@app.route('/api/reference/etymology/<word>')
def get_etymology(word):
    """Get etymology for a word"""
    try:
        # Simplified: just return Wikipedia summary
        summary = wikipedia.summary(word, sentences=1, auto_suggest=False)
        return jsonify({'etymology': summary})
    except Exception as e:
        return jsonify({'etymology': 'Etymology not available'}), 200

# ============================================================================
# API ROUTES - FEATURES
# ============================================================================

@app.route('/api/features')
def list_features():
    """Get all features"""
    try:
        features = get_feature_summary()
        return jsonify({
            'count': len(features),
            'features': features
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/features/<feature_id>')
def get_feature(feature_id):
    """Get feature details"""
    try:
        feature_info = get_feature_info(feature_id)
        if not feature_info:
            return jsonify({'error': f"Feature '{feature_id}' not found"}), 404
        
        return jsonify({
            'feature_id': feature_id,
            **feature_info
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/features/<feature_id>/examples')
def get_feature_examples_route(feature_id):
    """Get examples for a feature"""
    try:
        examples = get_feature_examples(feature_id)
        if not examples:
            return jsonify({'error': f"Feature '{feature_id}' not found"}), 404
        
        return jsonify({
            'feature_id': feature_id,
            'count': len(examples),
            'examples': examples
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# API ROUTES - WORDS
# ============================================================================

@app.route('/api/words/add', methods=['POST'])
def add_word():
    """Add a new word to the quiz"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Word text required'}), 400
        
        # Add to data source
        word_source.add_word({
            'word': data['text'],
            'syllables': data.get('syllables', []),
            'ipa': data.get('ipa', ''),
            'feature_id': data.get('feature_id', 'general')
        })
        
        return jsonify({'status': 'success', 'word': data['text']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# SERVER
# ============================================================================

if __name__ == '__main__':
    print(f"✅ Starting Flask server on port {PORT}...")
    print(f"📂 Template folder: {os.path.join(os.path.dirname(__file__), 'frontend', 'templates')}")
    print(f"🌐 Open http://localhost:{PORT}/ in your browser")
    print("\nPress Ctrl+C to stop the server")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)
