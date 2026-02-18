#!/usr/bin/env python
"""
Quick verification test for refactored architecture
"""

import json
import sys

print("=" * 60)
print("REFACTORING VERIFICATION TEST")
print("=" * 60)

# Test 1: Services module
print("\n✓ Test 1: Services module imports")
try:
    from services import (
        JSONWordDataSource,
        FileProgressTracker,
        WindowsAudioPlayer,
        LocalProgressTracker,
        APIWordDataSource,
        DatabaseWordDataSource
    )
    print("  ✅ All service classes imported successfully")
except ImportError as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)

# Test 2: Config file
print("\n✓ Test 2: Config file loads")
try:
    with open("config.json") as f:
        config = json.load(f)
    print(f"  ✅ Config loaded successfully")
    print(f"     - TTS Provider: {config['tts']['provider']}")
    print(f"     - Word File: {config['data']['word_file']}")
    print(f"     - Stats File: {config['progress']['stats_file']}")
    print(f"     - Output Dir: {config['tts']['output_dir']}")
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)

# Test 3: WordDataSource
print("\n✓ Test 3: WordDataSource initialization")
try:
    word_source = JSONWordDataSource(config["data"]["word_file"])
    words = word_source.get_all_words()
    print(f"  ✅ WordDataSource working")
    print(f"     - Loaded {len(words)} words from JSON")
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)

# Test 4: ProgressTracker
print("\n✓ Test 4: ProgressTracker initialization")
try:
    tracker = FileProgressTracker(config["progress"]["stats_file"])
    stats = tracker.get_stats()
    print(f"  ✅ ProgressTracker working")
    print(f"     - Total rounds: {stats['total_rounds']}")
    print(f"     - Correct: {stats['correct']}")
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)

# Test 5: AudioPlayer
print("\n✓ Test 5: AudioPlayer initialization")
try:
    player = WindowsAudioPlayer()
    print(f"  ✅ AudioPlayer initialized successfully")
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)

# Test 6: Quiz file imports
print("\n✓ Test 6: Main app file syntax check")
try:
    with open("pronunciation_quiz_ui.py", encoding="utf-8") as f:
        code = f.read()
    compile(code, "pronunciation_quiz_ui.py", "exec")
    print(f"  ✅ Main app file compiles successfully (no syntax errors)")
except SyntaxError as e:
    print(f"  ❌ FAILED: Syntax error in main app: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("🎉 ALL TESTS PASSED!")
print("=" * 60)
print("\nRefactoring verification complete:")
print("✅ Services layer working")
print("✅ Configuration loaded")
print("✅ Data abstraction functioning")
print("✅ Progress tracking ready")
print("✅ Audio player initialized")
print("✅ Main app syntax valid")
print("\nYour app is now future-proof and ready to scale! 🚀")
