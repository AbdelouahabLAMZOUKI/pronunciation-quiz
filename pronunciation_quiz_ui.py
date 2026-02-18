import json
import random
import tkinter as tk
from tkinter import messagebox
import threading
import os
import winsound
import webbrowser
import wikipedia

try:
    from google.cloud import texttospeech
except Exception:
    texttospeech = None

try:
    import pyttsx3
except Exception:
    pyttsx3 = None

# NEW: Import services from abstraction layer
from services import JSONWordDataSource, FileProgressTracker, WindowsAudioPlayer

# NEW: Load configuration from external file
with open("config.json") as f:
    CONFIG = json.load(f)

# NEW: Initialize service layer for future-proof architecture
word_service = JSONWordDataSource(CONFIG["data"]["word_file"])
progress_tracker = FileProgressTracker(CONFIG["progress"]["stats_file"])
audio_player = WindowsAudioPlayer()

# ARPAbet to IPA conversion mapping
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


def arpabet_to_ipa(arpabet_str):
    """
    Convert ARPAbet phonemes to proper IPA format.

    Input: "B UH1 L AH0 K S" (ARPAbet with stress markers)
    Output: "/ˈbʌləks/" (proper IPA with Unicode stress marks)

    Stress markers:
    - 1 = primary stress (ˈ before vowel)
    - 2 = secondary stress (ˌ before vowel)
    - 0 = no stress (ignored)
    """
    if not arpabet_str or arpabet_str.strip() == "":
        return "/"

    phonemes = arpabet_str.split()
    ipa_result = []

    i = 0
    while i < len(phonemes):
        phoneme = phonemes[i]

        # Extract stress marker (last character if it's a digit)
        stress = ''
        if phoneme and phoneme[-1].isdigit():
            stress = phoneme[-1]
            phoneme_code = phoneme[:-1]
        else:
            phoneme_code = phoneme

        # Convert to IPA
        ipa_char = ARPABET_TO_IPA.get(phoneme_code, phoneme_code.lower())

        # Add stress mark before the vowel (primary or secondary)
        if stress == '1':
            ipa_result.append('ˈ' + ipa_char)
        elif stress == '2':
            ipa_result.append('ˌ' + ipa_char)
        else:
            ipa_result.append(ipa_char)

        i += 1

    return '/' + ''.join(ipa_result) + '/'


# Sentence generation logic
def generate_sentences(target_word, min_count, max_count):
    word = (target_word or "").strip()
    if not word:
        return []

    word_lower = word.lower()
    word_cap = word[:1].upper() + word[1:]

    templates = [
        "I keep thinking about the word '{word}' after that conversation.",
        "Do you remember the last time we used the word '{word}' in class?",
        "Let's practice saying '{word}' slowly and then faster.",
        "Could you put '{word}' into a sentence that sounds natural?",
        "I heard '{word}' on a podcast this morning.",
        "That story really needed the word '{word}' to make sense.",
        "If you say '{word}' confidently, it sounds much more natural.",
        "I always pause before I say '{word}', but I'm getting better.",
        "We should write a short note using '{word}'.",
        "I texted my friend and used '{word}' without thinking.",
        "When you stress the right syllable in '{word}', it clicks.",
        "The word '{word}' feels easier when you connect it to the next word.",
        "Let's say '{word}' in a casual, everyday tone.",
        "I like how '{word}' sounds in that sentence you made.",
        "Try saying '{word}' as if you're in a hurry.",
        "I wrote '{word}' on a sticky note to remember it.",
        "My favorite example with '{word}' is still the one from yesterday.",
        "I almost skipped '{word}', but then it showed up again.",
        "That was a smooth way to fit '{word}' into the conversation.",
        "We can practice '{word}' with a question and an answer.",
        "{word_cap} sounds different when you say it with a smile.",
        "I use '{word}' when I'm explaining something quickly.",
        "The phrase with '{word}' felt more natural the second time.",
        "Let's record ourselves saying '{word}' and compare.",
        "I tried '{word}' in a new sentence, and it worked.",
        "Hearing '{word}' out loud helps me remember it.",
        "Can you repeat '{word}' like you're telling a friend?",
        "I never noticed how often I hear '{word}' until now.",
        "We should keep '{word}' in our daily practice list.",
        "Saying '{word}' clearly makes the rest of the sentence smoother."
    ]

    count = random.randint(min_count, max_count)
    random.shuffle(templates)
    selected = templates[:count]

    return [t.format(word=word_lower, word_cap=word_cap) for t in selected]


# TTS integration
def ensure_output_dir():
    """Create output directory if it doesn't exist"""
    output_dir = CONFIG["tts"]["output_dir"]
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


def safe_slug(text):
    cleaned = []
    for ch in text:
        if ch.isalnum():
            cleaned.append(ch.lower())
        else:
            cleaned.append('_')
    return ''.join(cleaned).strip('_') or "audio"


def synthesize_to_file(text, output_path):
    """Generate audio file using TTS provider"""
    # Get provider config
    tts_provider = CONFIG["tts"]["provider"]
    
    # Try Google Cloud TTS first
    if tts_provider == "google" and texttospeech is not None:
        try:
            client = texttospeech.TextToSpeechClient()
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code=CONFIG["tts"]["language_code"],
                name=CONFIG["tts"]["voice_name"]
            )

            if CONFIG["tts"]["audio_encoding"].upper() == "MP3":
                audio_encoding = texttospeech.AudioEncoding.MP3
            else:
                audio_encoding = texttospeech.AudioEncoding.LINEAR16

            audio_config = texttospeech.AudioConfig(
                audio_encoding=audio_encoding,
                speaking_rate=CONFIG["tts"]["speaking_rate"]
            )

            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )

            with open(output_path, "wb") as out:
                out.write(response.audio_content)
            return  # Success
        except Exception:
            # Fall through to pyttsx3 fallback
            pass
    
    # Fallback to pyttsx3 (Windows built-in TTS)
    if pyttsx3 is not None:
        engine = pyttsx3.init()
        engine.setProperty('rate', int(CONFIG["tts"]["speaking_rate"] * 150))  # Adjust rate
        engine.save_to_file(text, output_path)
        engine.runAndWait()
    else:
        raise RuntimeError("No TTS provider available. Install pyttsx3 or configure Google Cloud credentials.")


def play_audio_file(path):
    """Play audio file using abstracted audio player"""
    try:
        audio_player.play(path)
    except Exception as e:
        messagebox.showerror("Playback Error", f"Could not play audio:\n{str(e)[:200]}")


# External link handling
def open_youglish_link():
    if not current_word:
        return
    word = current_word["text"].strip()
    if not word:
        return
    url = f"https://youglish.com/pronounce/{word}/english"
    webbrowser.open(url)


# Pronunciation audio (word + sentences)
def play_word_tts():
    if not current_word:
        return

    word = current_word["text"].strip()
    if not word:
        return

    ensure_output_dir()
    filename = f"word_{safe_slug(word)}.mp3"
    path = os.path.abspath(os.path.join(CONFIG["tts"]["output_dir"], filename))

    def run():
        try:
            if not os.path.exists(path):
                synthesize_to_file(word, path)
            play_audio_file(path)
        except Exception as e:
            messagebox.showerror(
                "TTS Error",
                "Neural TTS failed. Ensure credentials are configured for Google Cloud.\n\n"
                f"Details: {str(e)[:250]}"
            )

    thread = threading.Thread(target=run, daemon=True)
    thread.start()


def generate_sentences_for_current_word():
    if not current_word:
        return
    sentences = generate_sentences(
        current_word["text"],
        CONFIG["quiz"]["sentence_min"],
        CONFIG["quiz"]["sentence_max"]
    )
    sentences_listbox.delete(0, tk.END)
    for sentence in sentences:
        sentences_listbox.insert(tk.END, sentence)


def play_selected_sentence():
    if not current_word:
        return
    selection = sentences_listbox.curselection()
    if not selection:
        messagebox.showwarning("No Sentence", "Pick a sentence to play.")
        return
    sentence = sentences_listbox.get(selection[0])

    ensure_output_dir()
    filename = f"sentence_{safe_slug(current_word['text'])}_{selection[0] + 1}.mp3"
    path = os.path.abspath(os.path.join(CONFIG["tts"]["output_dir"], filename))

    def run():
        try:
            if not os.path.exists(path):
                synthesize_to_file(sentence, path)
            play_audio_file(path)
        except Exception as e:
            messagebox.showerror(
                "TTS Error",
                "Neural TTS failed. Ensure credentials are configured for Google Cloud.\n\n"
                f"Details: {str(e)[:250]}"
            )

    thread = threading.Thread(target=run, daemon=True)
    thread.start()


# Clip playback (local wav)
def play_clip():
    """Play the audio clip for the current word (Windows .wav files)."""
    if not current_word:
        return

    clip_id = current_word.get("clip_id")
    if not clip_id:
        messagebox.showwarning("No Clip", "No audio clip available for this word.")
        return

    possible_paths = [
        f"clips/{clip_id}.wav",
        f"audio/{clip_id}.wav",
        f"{clip_id}.wav"
    ]

    clip_path = None
    for path in possible_paths:
        if os.path.exists(path):
            clip_path = path
            break

    if not clip_path:
        messagebox.showwarning(
            "Clip Not Found",
            f"Audio clip '{clip_id}' not found.\n\n"
            "Place .wav audio clips in a 'clips/' folder:\n"
            f"clips/{clip_id}.wav"
        )
        return

    def play_audio():
        try:
            winsound.PlaySound(clip_path, winsound.SND_FILENAME)
        except Exception as e:
            print(f"Error playing clip: {e}")

    thread = threading.Thread(target=play_audio, daemon=True)
    thread.start()


# Wikipedia helpers
def show_explanation():
    """Fetch and display word meaning/explanation from Wikipedia."""
    if not current_word:
        return

    word = current_word["text"]

    def fetch_explanation():
        try:
            summary = wikipedia.summary(word, sentences=3, auto_suggest=False)
            messagebox.showinfo(f"Definition: {word}", summary)
        except wikipedia.exceptions.DisambiguationError as e:
            best_option = None
            if e.options:
                for option in e.options:
                    if option.lower() == word.lower():
                        best_option = option
                        break
                if not best_option:
                    for option in e.options:
                        if option.lower().startswith(word.lower()):
                            best_option = option
                            break
                if not best_option:
                    best_option = e.options[0]

                try:
                    summary = wikipedia.summary(best_option, sentences=3, auto_suggest=False)
                    messagebox.showinfo(f"Definition: {best_option}", summary)
                except Exception:
                    messagebox.showinfo("Explanation", "Multiple pages found:\n\n" + ", ".join(e.options[:5]))
            else:
                messagebox.showinfo("Not Found", f"No valid page found for '{word}'.")
        except wikipedia.exceptions.PageError:
            messagebox.showinfo("Not Found", f"No Wikipedia entry found for '{word}'.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch explanation:\n{str(e)[:200]}")

    thread = threading.Thread(target=fetch_explanation, daemon=True)
    thread.start()


def show_etymology():
    """Fetch and display word etymology."""
    if not current_word:
        return

    word = current_word["text"]

    def fetch_etymology():
        try:
            page = wikipedia.page(word, auto_suggest=False)
            full_text = page.content

            if "etymology" in full_text.lower():
                idx = full_text.lower().find("etymology")
                etymology_text = full_text[max(0, idx - 50):min(len(full_text), idx + 600)]
                messagebox.showinfo(f"Etymology: {word}", etymology_text.strip())
            else:
                messagebox.showinfo("Etymology", f"Word: {page.title}\n\nOpening:\n{full_text[:300]}...")

        except wikipedia.exceptions.DisambiguationError as e:
            best_option = None
            if e.options:
                for option in e.options:
                    if option.lower() == word.lower():
                        best_option = option
                        break
                if not best_option:
                    for option in e.options:
                        if option.lower().startswith(word.lower()):
                            best_option = option
                            break
                if not best_option:
                    best_option = e.options[0]

                try:
                    page = wikipedia.page(best_option, auto_suggest=False)
                    full_text = page.content
                    if "etymology" in full_text.lower():
                        idx = full_text.lower().find("etymology")
                        etymology_text = full_text[max(0, idx - 50):min(len(full_text), idx + 600)]
                        messagebox.showinfo(f"Etymology: {best_option}", etymology_text.strip())
                    else:
                        messagebox.showinfo("Etymology", f"Word: {page.title}\n\n{full_text[:300]}...")
                except Exception:
                    messagebox.showinfo("Etymology", "Multiple pages found:\n\n" + ", ".join(e.options[:5]))
            else:
                messagebox.showinfo("Not Found", f"No valid page found for '{word}'.")
        except wikipedia.exceptions.PageError:
            messagebox.showinfo("Not Found", f"No Wikipedia page found for '{word}'.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch etymology:\n{str(e)[:200]}")

    thread = threading.Thread(target=fetch_etymology, daemon=True)
    thread.start()


# Load words using service layer (easy to switch to API/database later)
words = word_service.get_all_words()

# NEW: Quiz state with service-based progress tracking
current_word = None
attempts = 0


# Functions
def pick_random_word():
    global current_word, attempts
    current_word = random.choice(words)
    attempts = 0
    update_ui_for_word()


def update_ui_for_word():
    word_label.config(text=current_word["text"])
    syllables_var.set(" | ".join(current_word["syllables"]))
    arpabet_str = " ".join(current_word["syllables"])
    ipa_display = arpabet_to_ipa(arpabet_str)
    ipa_var.set(ipa_display)
    original_var.set(str(current_word["original_pronunciation"]))
    feedback_label.config(text="")
    sentences_listbox.delete(0, tk.END)


def handle_guess(feature):
    global attempts
    attempts += 1
    correct_feature = current_word["feature_id"]

    word_text = current_word["text"]

    if feature == correct_feature:
        feedback_label.config(text="✅ Correct!", fg="green")
        progress_tracker.save_attempt(word_text, True, feature)
        pick_random_word()
    elif feature == "skip":
        feedback_label.config(text=f"⏭ Skipped! Correct: {correct_feature}", fg="orange")
        progress_tracker.save_attempt(word_text, False, feature)
        pick_random_word()
    else:
        feedback_label.config(text="❌ Wrong! Try again.", fg="red")
        progress_tracker.save_attempt(word_text, False, feature)


def show_stats():
    """Display stats from progress tracker"""
    stats = progress_tracker.get_stats()
    summary = (
        f"Total Rounds: {stats['total_rounds']}\n"
        f"Correct: {stats['correct']}\n"
        f"Skipped: {stats['skipped']}\n"
        f"Attempts per Word: {stats['attempts_per_word']}\n"
        f"Per Feature Accuracy: {stats['per_feature']}\n"
        f"Most Missed Words: {stats['most_missed']}"
    )
    messagebox.showinfo("Session Stats", summary)


# Tkinter UI
root = tk.Tk()
root.title("American Pronunciation Quiz")

word_label = tk.Label(root, text="", font=("Arial", 24))
word_label.pack(pady=10)

syllables_var = tk.StringVar()
syllables_label = tk.Label(root, textvariable=syllables_var, font=("Arial", 14))
syllables_label.pack()

ipa_var = tk.StringVar()
ipa_label = tk.Label(root, textvariable=ipa_var, font=("Arial", 12))
ipa_label.pack()

original_var = tk.StringVar()
original_label = tk.Label(root, textvariable=original_var, font=("Arial", 12))
original_label.pack()

feedback_label = tk.Label(root, text="", font=("Arial", 14))
feedback_label.pack(pady=10)

# Pronounce button (Neural TTS)
pronounce_btn = tk.Button(root, text="🔊 Neural TTS", command=play_word_tts, font=("Arial", 12))
pronounce_btn.pack(pady=5)

# Clip button
clip_btn = tk.Button(root, text="🎵 Listen to Clip", command=play_clip, font=("Arial", 12))
clip_btn.pack(pady=5)

# Sentence generation UI
sentences_frame = tk.Frame(root)
sentences_frame.pack(pady=8)

sentences_label = tk.Label(sentences_frame, text="Sentence Practice", font=("Arial", 12, "bold"))
sentences_label.pack()

sentences_listbox = tk.Listbox(sentences_frame, width=80, height=8)
sentences_listbox.pack(pady=4)

sentences_buttons = tk.Frame(sentences_frame)
sentences_buttons.pack(pady=4)

generate_sentences_btn = tk.Button(
    sentences_buttons,
    text="Generate Sentences",
    command=generate_sentences_for_current_word
)
generate_sentences_btn.pack(side=tk.LEFT, padx=6)

play_sentence_btn = tk.Button(
    sentences_buttons,
    text="Play Selected Sentence",
    command=play_selected_sentence
)
play_sentence_btn.pack(side=tk.LEFT, padx=6)

# YouGlish button (external link)
youglish_btn = tk.Button(root, text="Open YouGlish", command=open_youglish_link, font=("Arial", 12))
youglish_btn.pack(pady=5)

# Explanation button
explain_btn = tk.Button(root, text="📖 Explanation", command=show_explanation, font=("Arial", 12))
explain_btn.pack(pady=5)

# Etymology button
etymology_btn = tk.Button(root, text="🌳 Etymology", command=show_etymology, font=("Arial", 12))
etymology_btn.pack(pady=5)

# ============================================================================
# ADD WORDS SECTION
# ============================================================================

add_word_frame = tk.LabelFrame(root, text="➕ Add New Word", padx=10, pady=10, font=("Arial", 11, "bold"))
add_word_frame.pack(pady=10, padx=10, fill=tk.X)

# Word input
word_input_frame = tk.Frame(add_word_frame)
word_input_frame.pack(fill=tk.X, pady=5)
tk.Label(word_input_frame, text="Word:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
word_entry = tk.Entry(word_input_frame, font=("Arial", 10), width=20)
word_entry.pack(side=tk.LEFT, padx=5)

# Syllables input
syllables_input_frame = tk.Frame(add_word_frame)
syllables_input_frame.pack(fill=tk.X, pady=5)
tk.Label(syllables_input_frame, text="Syllables (space-separated):", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
syllables_entry = tk.Entry(syllables_input_frame, font=("Arial", 10), width=30)
syllables_entry.pack(side=tk.LEFT, padx=5)

# Feature ID input
feature_input_frame = tk.Frame(add_word_frame)
feature_input_frame.pack(fill=tk.X, pady=5)
tk.Label(feature_input_frame, text="Feature ID:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
feature_entry = tk.Entry(feature_input_frame, font=("Arial", 10), width=20)
feature_entry.pack(side=tk.LEFT, padx=5)
feature_entry.insert(0, "vowel_sound")  # Default value

# Pronunciation input (optional)
pronunciation_input_frame = tk.Frame(add_word_frame)
pronunciation_input_frame.pack(fill=tk.X, pady=5)
tk.Label(pronunciation_input_frame, text="Pronunciation (optional):", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
pronunciation_entry = tk.Entry(pronunciation_input_frame, font=("Arial", 10), width=30)
pronunciation_entry.pack(side=tk.LEFT, padx=5)

# Save word button
def add_new_word():
    """Add a new word to the word list"""
    word_text = word_entry.get().strip()
    syllables_text = syllables_entry.get().strip()
    feature_id = feature_entry.get().strip()
    pronunciation = pronunciation_entry.get().strip()
    
    # Validation
    if not word_text:
        messagebox.showwarning("Missing Word", "Please enter a word.")
        return
    
    if not syllables_text:
        messagebox.showwarning("Missing Syllables", "Please enter syllables (space-separated).")
        return
    
    if not feature_id:
        messagebox.showwarning("Missing Feature", "Please enter a feature ID.")
        return
    
    # Create word object
    new_word = {
        "text": word_text.lower(),
        "syllables": syllables_text.split(),
        "feature_id": feature_id,
        "original_pronunciation": pronunciation or syllables_text,
    }
    
    try:
        # Add to word service
        word_service.save_word(new_word)
        
        # Reload words
        global words
        words = word_service.get_all_words()
        
        # Clear inputs
        word_entry.delete(0, tk.END)
        syllables_entry.delete(0, tk.END)
        feature_entry.delete(0, tk.END)
        feature_entry.insert(0, "vowel_sound")
        pronunciation_entry.delete(0, tk.END)
        
        messagebox.showinfo("Success", f"Word '{word_text}' added successfully!\n\nTotal words: {len(words)}")
        
        # Pick a random word to show the new one might appear
        pick_random_word()
    except Exception as e:
        messagebox.showerror("Error", f"Could not save word:\n{str(e)[:200]}")

add_word_btn = tk.Button(add_word_frame, text="💾 Save New Word", command=add_new_word, font=("Arial", 11, "bold"))
add_word_btn.pack(pady=10)

# Attribution
attribution_label = tk.Label(
    root,
    text="Audio generated using licensed neural TTS (US English voice).",
    font=("Arial", 9)
)
attribution_label.pack(pady=2)

youglish_label = tk.Label(
    root,
    text="External pronunciation examples available via YouGlish.com.",
    font=("Arial", 9)
)
youglish_label.pack(pady=2)

# Feature buttons
features = ["stress", "rhythm", "assimilation", "t_flap", "intonation", "skip"]
for feat in features:
    btn = tk.Button(root, text=feat.capitalize(), width=12, command=lambda f=feat: handle_guess(f))
    btn.pack(side=tk.LEFT, padx=5, pady=5)

# Stats button
stats_btn = tk.Button(root, text="Show Stats", command=show_stats)
stats_btn.pack(pady=10)

pick_random_word()
root.mainloop()
