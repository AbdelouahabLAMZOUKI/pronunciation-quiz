/**
 * Frontend Application Logic
 * Handles all API communication and state management
 * No business logic here - all calls go to /api endpoints
 */

// Dynamically set API base URL
const API_BASE = (() => {
    // In production (Render), use the deployed backend URL
    if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        // Extract the app name from current URL and construct backend URL
        const host = window.location.hostname;
        const backendUrl = `https://${host.replace('frontend-', '').replace('app-', '')}/api`;
        return backendUrl;
    }
    // In development, use localhost
    return 'http://localhost:8000/api';
})();

const SESSION_ID = 'user_' + Date.now(); // Simple session ID for demo

// State
let currentWord = null;
let selectedSentence = null;

// ========== DOM ELEMENTS ==========

const newWordBtn = document.getElementById('newWordBtn');
const ttsBtn = document.getElementById('ttsBtn');
const youglishBtn = document.getElementById('youglishBtn');
const generateSentencesBtn = document.getElementById('generateSentencesBtn');
const playSentenceBtn = document.getElementById('playSentenceBtn');
const sentencesList = document.getElementById('sentencesList');
const definitionBtn = document.getElementById('definitionBtn');
const etymologyBtn = document.getElementById('etymologyBtn');
const searchWordBtn = document.getElementById('searchWordBtn');
const addWordBtn = document.getElementById('addWordBtn');
const searchWordInput = document.getElementById('searchWordInput');
const clearBtn = document.getElementById('clearBtn');

// Feature guide elements
const featureGuideBtn = document.getElementById('featureGuideBtn');
const featureGuideModal = document.getElementById('featureGuideModal');
const closeGuideBtn = document.getElementById('closeGuideBtn');
const featureSelectDropdown = document.getElementById('featureSelectDropdown');

// ========== INITIALIZATION ==========

document.addEventListener('DOMContentLoaded', function() {
    console.log('Quiz app initialized');
    
    // Don't load initial word - let user choose
    // getNewWord();
    
    // Event listeners
    newWordBtn.addEventListener('click', getNewWord);
    ttsBtn.addEventListener('click', synthesizeAndPlayTTS);
    youglishBtn.addEventListener('click', openYouGlish);
    clearBtn.addEventListener('click', clearWord);
    
    generateSentencesBtn.addEventListener('click', generateSentences);
    playSentenceBtn.addEventListener('click', playSentence);
    definitionBtn.addEventListener('click', showDefinition);
    etymologyBtn.addEventListener('click', showEtymology);
    searchWordBtn.addEventListener('click', searchWord);
    addWordBtn.addEventListener('click', addSearchedWord);
    searchWordInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            searchWord();
        }
    });
    
    sentencesList.addEventListener('change', function(e) {
        if (e.target.tagName === 'INPUT') {
            selectedSentence = e.target.value;
            playSentenceBtn.disabled = false;
        }
    });
    
    // Feature guide listeners
    featureGuideBtn.addEventListener('click', openFeatureGuide);
    closeGuideBtn.addEventListener('click', closeFeatureGuide);
    featureSelectDropdown.addEventListener('change', loadFeatureInfo);
    
    // Close modal on outside click
    featureGuideModal.addEventListener('click', function(e) {
        if (e.target === featureGuideModal) {
            closeFeatureGuide();
        }
    });
});

// ========== API CALLS ==========

/**
 * Fetch new word from API
 * GET /api/quiz/new-word
 */
async function getNewWord() {
    try {
        showFeedback('Loading...', 'info');
        
        const response = await fetch(`${API_BASE}/quiz/new-word?session_id=${SESSION_ID}`, {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        currentWord = data.word;
        
        // Update UI
        document.getElementById('wordText').textContent = currentWord.text;
        document.getElementById('sentenceWordDisplay').textContent = currentWord.text;
        document.getElementById('syllablesDisplay').textContent = currentWord.syllables.join(' ');
        document.getElementById('ipaDisplay').textContent = currentWord.ipa;
        document.getElementById('originalDisplay').textContent = currentWord.original_pronunciation;
        
        // Hide add to quiz section (this is already in quiz)
        document.getElementById('addToQuizSection').classList.add('hidden');
        
        // Disable search when quiz word is active
        searchWordInput.disabled = true;
        searchWordBtn.disabled = true;
        searchWordInput.value = '';
        
        // Show clear button, hide new word button
        clearBtn.style.display = 'inline-block';
        newWordBtn.style.display = 'none';
        
        // Fetch and show definition
        try {
            const defResponse = await fetch(`${API_BASE}/reference/definition/${currentWord.text}`);
            if (defResponse.ok) {
                const defData = await defResponse.json();
                document.getElementById('definitionText').textContent = defData.definition;
            } else {
                document.getElementById('definitionText').textContent = '---';
            }
        } catch (err) {
            document.getElementById('definitionText').textContent = '---';
        }
        
        // Clear old feedback/sentences
        clearFeedback();
        clearSentences();
        
        console.log('New word loaded:', currentWord);
    } catch (error) {
        console.error('Error loading new word:', error);
        showFeedback('Failed to load word: ' + error.message, 'error');
    }
}

/**
 * Submit answer - this is the key endpoint that replaces Tkinter's handle_guess()
 * POST /api/quiz/submit-answer
 * 
 * This is where the Tkinter button click becomes an HTTP request
 */
async function submitAnswer(feature) {
    if (!currentWord) {
        showFeedback('No word loaded. Click "New Word"', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/quiz/submit-answer`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: SESSION_ID,
                feature: feature
            })
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        
        // Show feedback
        const feedbackClass = data.correct ? 'success' : (feature === 'skip' ? 'warning' : 'error');
        showFeedback(data.feedback, feedbackClass);
        
        // Update to next word
        currentWord = data.next_word;
        document.getElementById('wordText').textContent = currentWord.text;
        document.getElementById('syllablesDisplay').textContent = currentWord.syllables.join(' ');
        document.getElementById('ipaDisplay').textContent = currentWord.ipa;
        document.getElementById('originalDisplay').textContent = currentWord.original_pronunciation;
        
        // Clear sentences
        clearSentences();
        
        console.log('Answer submitted:', { feature, correct: data.correct });
    } catch (error) {
        console.error('Error submitting answer:', error);
        showFeedback('Error: ' + error.message, 'error');
    }
}

/**
 * Pick the best available English voice
 */
function getPreferredVoice(voices) {
    if (!Array.isArray(voices) || voices.length === 0) return null;
    
    const enVoices = voices.filter(v => (v.lang || '').toLowerCase().startsWith('en'));
    if (enVoices.length === 0) return voices[0];
    
    const neuralLike = enVoices.find(v => /neural|natural|premium|enhanced/i.test(v.name));
    if (neuralLike) return neuralLike;
    
    const usVoice = enVoices.find(v => /en-us/i.test(v.lang));
    return usVoice || enVoices[0];
}

/**
 * Load voices (some browsers populate asynchronously)
 */
function loadVoices() {
    return new Promise(resolve => {
        const voices = speechSynthesis.getVoices();
        if (voices.length) {
            resolve(voices);
            return;
        }
        const handler = () => {
            speechSynthesis.removeEventListener('voiceschanged', handler);
            resolve(speechSynthesis.getVoices());
        };
        speechSynthesis.addEventListener('voiceschanged', handler);
    });
}

/**
 * Synthesize and play TTS audio (browser Web Speech API)
 */
async function synthesizeAndPlayTTS() {
    if (!currentWord) return;
    
    try {
        const text = currentWord.text;
        const voices = await loadVoices();
        const voice = getPreferredVoice(voices);
        
        const utterance = new SpeechSynthesisUtterance(text);
        if (voice) utterance.voice = voice;
        
        // Configure pronunciation
        utterance.rate = 0.85;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        
        // Feedback during playback
        utterance.onstart = () => {
            const voiceLabel = voice ? ` (${voice.name})` : '';
            showFeedback('🔊 Speaking: ' + text + voiceLabel, 'success');
        };
        
        utterance.onend = () => {
            showFeedback('✅ Pronunciation played', 'success');
        };
        
        utterance.onerror = (event) => {
            showFeedback('🔊 Error: ' + event.error, 'error');
        };
        
        speechSynthesis.cancel();
        speechSynthesis.speak(utterance);
        
    } catch (error) {
        console.error('Error playing TTS:', error);
        showFeedback('TTS Error: ' + error.message, 'error');
    }
}

/**

 * Open YouGlish link in new tab
 */
function openYouGlish() {
    if (!currentWord) return;
    
    const word = currentWord.text;
    const url = `https://youglish.com/pronounce/${word}/english`;
    window.open(url, '_blank');
}

/**
 * Clear current word and reset to allow switching between quiz/search
 */
function clearWord() {
    // Reset word state
    currentWord = null;
    
    // Clear displays
    document.getElementById('wordText').textContent = '---';
    document.getElementById('sentenceWordDisplay').textContent = '---';
    document.getElementById('syllablesDisplay').textContent = '---';
    document.getElementById('ipaDisplay').textContent = '---';
    document.getElementById('originalDisplay').textContent = '---';
    document.getElementById('definitionText').textContent = '---';
    
    // Clear search input
    searchWordInput.value = '';
    
    // Enable both features
    searchWordInput.disabled = false;
    searchWordBtn.disabled = false;
    newWordBtn.disabled = false;
    
    // Show quiz word button, hide clear button
    clearBtn.style.display = 'none';
    newWordBtn.style.display = 'inline-block';
    
    // Hide add to quiz section
    document.getElementById('addToQuizSection').classList.add('hidden');
    
    // Clear feedback and sentences
    clearFeedback();
    clearSentences();
    
    console.log('Word cleared - ready for new selection');
}

/**
 * Generate sentences for current word
 * GET /api/pronunciation/sentences/{word}
 */
async function generateSentences() {
    if (!currentWord) return;
    
    try {
        showFeedback('Generating sentences...', 'info');
        
        const response = await fetch(
            `${API_BASE}/pronunciation/sentences/${currentWord.text}`
        );
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        
        // Clear and populate list
        sentencesList.innerHTML = '';
        
        const container = document.getElementById('sentencesContainer');
        container.classList.remove('hidden');
        
        data.sentences.forEach((sentence, index) => {
            const li = document.createElement('li');
            const input = document.createElement('input');
            input.type = 'radio';
            input.name = 'sentence';
            input.value = index;
            input.id = `sentence_${index}`;
            
            const label = document.createElement('label');
            label.htmlFor = `sentence_${index}`;
            label.textContent = sentence;
            
            li.appendChild(input);
            li.appendChild(label);
            li.addEventListener('click', () => input.click());
            
            sentencesList.appendChild(li);
        });
        
        clearFeedback();
        playSentenceBtn.disabled = true;
        console.log('Sentences generated:', data.count);
    } catch (error) {
        console.error('Error generating sentences:', error);
        showFeedback('Error: ' + error.message, 'error');
    }
}

/**
 * Play selected sentence (synthesize TTS)
 */
async function playSentence() {
    const selected = document.querySelector('input[name="sentence"]:checked');
    if (!selected) {
        showFeedback('Select a sentence first', 'warning');
        return;
    }
    
    // Get the sentence text from the label
    const label = document.querySelector(`label[for="${selected.id}"]`);
    if (!label) {
        showFeedback('Error: Could not find sentence text', 'error');
        return;
    }
    
    const sentenceText = label.textContent;
    
    try {
        const voices = await loadVoices();
        const voice = getPreferredVoice(voices);
        
        const utterance = new SpeechSynthesisUtterance(sentenceText);
        if (voice) utterance.voice = voice;
        
        // Configure pronunciation
        utterance.rate = 0.85;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        
        // Feedback during playback
        utterance.onstart = () => {
            const voiceLabel = voice ? ` (${voice.name})` : '';
            showFeedback('🔊 Speaking sentence' + voiceLabel, 'success');
        };
        
        utterance.onend = () => {
            showFeedback('✅ Sentence played', 'success');
        };
        
        utterance.onerror = (event) => {
            console.error('TTS error:', event);
            showFeedback('❌ TTS playback failed: ' + event.error, 'error');
        };
        
        speechSynthesis.cancel();
        speechSynthesis.speak(utterance);
        
        console.log('TTS started for sentence:', sentenceText);
    } catch (error) {
        console.error('Error in TTS:', error);
        showFeedback('❌ TTS error: ' + error.message, 'error');
    }
}

/**
 * Fetch and display word definition
 * GET /api/reference/definition/{word}
 */
async function showDefinition() {
    if (!currentWord) return;
    
    try {
        showFeedback('Loading definition...', 'info');
        
        const response = await fetch(
            `${API_BASE}/reference/definition/${currentWord.text}`
        );
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        
        showReferenceContent(data.definition);
        console.log('Definition loaded');
    } catch (error) {
        console.error('Error loading definition:', error);
        showFeedback('Error: ' + error.message, 'error');
    }
}

/**
 * Fetch and display word etymology
 * GET /api/reference/etymology/{word}
 */
async function showEtymology() {
    if (!currentWord) return;
    
    try {
        showFeedback('Loading etymology...', 'info');
        
        const response = await fetch(
            `${API_BASE}/reference/etymology/${currentWord.text}`
        );
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        
        showReferenceContent(data.etymology);
        console.log('Etymology loaded');
    } catch (error) {
        console.error('Error loading etymology:', error);
        showFeedback('Error: ' + error.message, 'error');
    }
}

// ========== UI HELPERS ==========

/**
 * Show feedback message with color coding
 */
function showFeedback(message, type = 'info') {
    const box = document.getElementById('feedbackBox');
    const text = document.getElementById('feedbackText');
    
    text.textContent = message;
    box.className = `feedback-box ${type}`;
    box.classList.remove('hidden');
}

function clearFeedback() {
    document.getElementById('feedbackBox').classList.add('hidden');
}

/**
 * Clear sentences list
 */
function clearSentences() {
    const container = document.getElementById('sentencesContainer');
    container.classList.add('hidden');
    sentencesList.innerHTML = '';
    playSentenceBtn.disabled = true;
    selectedSentence = null;
}

/**
 * Show reference content (definition/etymology)
 */
function showReferenceContent(content) {
    const box = document.getElementById('referenceContent');
    const text = document.getElementById('referenceText');
    
    text.textContent = content;
    box.classList.remove('hidden');
    clearFeedback();
}

/**
 * Search for any word and show definition, IPA, sentences, etymology
 */
async function searchWord() {
    const word = searchWordInput.value.trim();
    const addSection = document.getElementById('addToQuizSection');
    const syllablesInput = document.getElementById('addSyllablesInput');
    
    if (!word) {
        showFeedback('Please enter a word to search', 'warning');
        return;
    }
    
    try {
        // Clear previous word state
        currentWord = null;
        
        // Hide add section initially
        addSection.classList.add('hidden');
        syllablesInput.value = '';
        
        // Disable quiz word button when search is active
        newWordBtn.disabled = true;
        
        // Show clear button
        clearBtn.style.display = 'inline-block';
        
        // Update displays
        document.getElementById('wordText').textContent = word;
        document.getElementById('sentenceWordDisplay').textContent = word;
        showFeedback('Searching...', 'info');
        
        // Fetch all information in parallel (allow partial results)
        const [defResult, ipaResult, sentencesResult] = await Promise.allSettled([
            fetch(`${API_BASE}/reference/definition/${encodeURIComponent(word)}`),
            fetch(`${API_BASE}/pronunciation/ipa/${encodeURIComponent(word)}`),
            fetch(`${API_BASE}/pronunciation/sentences/${encodeURIComponent(word)}?count=5`)
        ]);
        
        const defOk = defResult.status === 'fulfilled' && defResult.value.ok;
        const ipaOk = ipaResult.status === 'fulfilled' && ipaResult.value.ok;
        const sentencesOk = sentencesResult.status === 'fulfilled' && sentencesResult.value.ok;
        
        const anySuccess = defOk || ipaOk || sentencesOk;
        
        // Definition
        if (defOk) {
            const defData = await defResult.value.json();
            document.getElementById('definitionText').textContent = defData.definition;
        } else {
            document.getElementById('definitionText').textContent = 'Definition not found.';
        }
        
        // IPA and Syllables
        if (ipaOk) {
            const ipaData = await ipaResult.value.json();
            document.getElementById('ipaDisplay').textContent = ipaData.ipa;
            document.getElementById('originalDisplay').textContent = ipaData.ipa;
            
            if (Array.isArray(ipaData.syllables) && ipaData.syllables.length > 0) {
                document.getElementById('syllablesDisplay').textContent = ipaData.syllables.join(' ');
                syllablesInput.value = ipaData.syllables.join(' ');
            } else {
                document.getElementById('syllablesDisplay').textContent = '---';
            }
            
            // Show add section if word not in local quiz
            if (ipaData.source !== 'local') {
                addSection.classList.remove('hidden');
            }
        } else {
            document.getElementById('ipaDisplay').textContent = 'Not found';
            document.getElementById('syllablesDisplay').textContent = '---';
            document.getElementById('originalDisplay').textContent = '---';
            addSection.classList.remove('hidden');
        }
        
        // Auto-populate sentences
        if (sentencesOk) {
            const sentencesData = await sentencesResult.value.json();
            sentencesList.innerHTML = '';
            const container = document.getElementById('sentencesContainer');
            container.classList.remove('hidden');
            
            sentencesData.sentences.forEach((sentence, index) => {
                const li = document.createElement('li');
                const input = document.createElement('input');
                input.type = 'radio';
                input.name = 'sentence';
                input.value = index;
                input.id = `sentence_${index}`;
                
                const label = document.createElement('label');
                label.htmlFor = `sentence_${index}`;
                label.textContent = sentence;
                
                li.appendChild(input);
                li.appendChild(label);
                li.addEventListener('click', () => input.click());
                
                sentencesList.appendChild(li);
            });
            
            playSentenceBtn.disabled = true;
        } else {
            clearSentences();
        }
        
        // Create a temporary word object for TTS
        currentWord = { text: word };
        
        // Show results
        showFeedback(anySuccess ? '✅ Word found!' : '❌ Word not found', anySuccess ? 'success' : 'error');
        
    } catch (error) {
        console.error('Error searching word:', error);
        document.getElementById('definitionText').textContent = 'Error loading data';
        document.getElementById('ipaDisplay').textContent = '---';
        document.getElementById('syllablesDisplay').textContent = '---';
        document.getElementById('originalDisplay').textContent = '---';
        syllablesInput.value = '';
        showFeedback('❌ Error fetching data', 'error');
        addSection.classList.remove('hidden');
    }
}

/**
 * Add searched word to quiz when not found
 */
async function addSearchedWord() {
    const word = searchWordInput.value.trim();
    const syllablesStr = document.getElementById('addSyllablesInput').value.trim();
    const feature = document.getElementById('addFeatureSelect').value;
    
    if (!word) {
        showFeedback('Please enter a word first', 'warning');
        return;
    }
    if (!syllablesStr) {
        showFeedback('Please enter syllables (ARPAbet)', 'warning');
        return;
    }
    
    try {
        showFeedback('Adding word...', 'info');
        const syllables = syllablesStr.split(/\s+/);
        
        const response = await fetch(`${API_BASE}/words/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: word,
                syllables: syllables,
                feature_id: feature,
                original_pronunciation: syllables.join(' ')
            })
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        showFeedback(`✅ "${word}" added to quiz!`, 'success');
        document.getElementById('addToQuizSection').classList.add('hidden');
        document.getElementById('addSyllablesInput').value = '';
    } catch (error) {
        console.error('Error adding searched word:', error);
        showFeedback('❌ Failed to add word: ' + error.message, 'error');
    }
}

// ========== FEATURE GUIDE FUNCTIONS ==========

/**
 * Open the feature guide modal
 */
function openFeatureGuide() {
    featureGuideModal.classList.remove('hidden');
}

/**
 * Close the feature guide modal
 */
function closeFeatureGuide() {
    featureGuideModal.classList.add('hidden');
    featureSelectDropdown.value = '';
    document.getElementById('featureDetails').classList.add('hidden');
}

/**
 * Load and display information for selected feature
 */
async function loadFeatureInfo() {
    const featureId = featureSelectDropdown.value;
    
    if (!featureId) {
        document.getElementById('featureDetails').classList.add('hidden');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/features/${featureId}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        
        // Populate feature details
        document.getElementById('featureName').textContent = data.name;
        document.getElementById('featureDescription').textContent = data.description;
        document.getElementById('featureExplanation').textContent = data.explanation;
        
        // Populate rules
        const rulesList = document.getElementById('featureRulesList');
        rulesList.innerHTML = '';
        data.rules.forEach(rule => {
            const li = document.createElement('li');
            li.textContent = rule;
            rulesList.appendChild(li);
        });
        
        // Populate examples
        const examplesList = document.getElementById('featureExamplesList');
        examplesList.innerHTML = '';
        data.examples.forEach(example => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>${example.word}</strong>: [${example.syllables}]<br><em>${example.note}</em>`;
            examplesList.appendChild(li);
        });
        
        // Populate common mistakes
        const mistakesList = document.getElementById('featureMistakesList');
        mistakesList.innerHTML = '';
        data.common_mistakes.forEach(mistake => {
            const li = document.createElement('li');
            li.textContent = mistake;
            mistakesList.appendChild(li);
        });
        
        // Show the details section
        document.getElementById('featureDetails').classList.remove('hidden');
        
    } catch (error) {
        console.error('Error loading feature info:', error);
        showFeedback('❌ Failed to load feature information', 'error');
    }
}