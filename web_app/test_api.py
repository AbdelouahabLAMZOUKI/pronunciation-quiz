"""
End-to-end test of the pronunciation quiz web app
Tests the complete flow: get word -> submit answer -> check stats
"""
import requests
import json

BASE_URL = 'http://localhost:8000/api'
SESSION_ID = 'test_e2e_' + str(int(__import__('time').time()))

print("\n" + "="*60)
print("🎯 PRONUNCIATION QUIZ - END-TO-END TEST")
print("="*60 + "\n")

try:
    # ========== TEST 1: Get New Word ==========
    print("1️⃣  GET NEW WORD")
    print("-" * 60)
    
    response = requests.post(f'{BASE_URL}/quiz/new-word', params={'session_id': SESSION_ID})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    word = data['word']
    
    print(f"   ✅ Status: {response.status_code}")
    print(f"   📝 Word: {word['text']}")
    print(f"   🎵 Feature: {word['feature_id']}")
    print(f"   🔤 Syllables: {' '.join(word['syllables'])}")
    print(f"   🗣️ IPA: {word['ipa']}")
    print()
    
    # ========== TEST 2: Submit Correct Answer ==========
    print("2️⃣  SUBMIT CORRECT ANSWER")
    print("-" * 60)
    
    payload = {
        'session_id': SESSION_ID,
        'feature': word['feature_id']  # Submit the correct answer
    }
    
    response = requests.post(f'{BASE_URL}/quiz/submit-answer', json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    result = response.json()
    
    print(f"   ✅ Status: {response.status_code}")
    print(f"   📊 Correct: {result['correct']}")
    print(f"   💬 Feedback: {result['feedback']}")
    print(f"   ✨ Got next word: {result['next_word']['text']}")
    print()
    
    assert result['correct'] == True, "Should be correct!"
    
    # ========== TEST 3: Submit Wrong Answer ==========
    print("3️⃣  SUBMIT WRONG ANSWER")
    print("-" * 60)
    
    next_word = result['next_word']
    current_feature = next_word['feature_id']
    wrong_feature = [f for f in ['stress', 'rhythm', 'assimilation', 't_flap', 'intonation'] 
                     if f != current_feature][0]
    
    payload = {
        'session_id': SESSION_ID,
        'feature': wrong_feature
    }
    
    response = requests.post(f'{BASE_URL}/quiz/submit-answer', json=payload)
    assert response.status_code == 200
    
    result2 = response.json()
    
    print(f"   ✅ Status: {response.status_code}")
    print(f"   📊 Correct: {result2['correct']}")
    print(f"   💬 Feedback: {result2['feedback']}")
    print()
    
    assert result2['correct'] == False, "Should be wrong!"
    
    # ========== TEST 4: Skip a Question ==========
    print("4️⃣  SKIP QUESTION")
    print("-" * 60)
    
    payload = {
        'session_id': SESSION_ID,
        'feature': 'skip'
    }
    
    response = requests.post(f'{BASE_URL}/quiz/submit-answer', json=payload)
    assert response.status_code == 200
    
    result3 = response.json()
    
    print(f"   ✅ Status: {response.status_code}")
    print(f"   📊 Correct: {result3['correct']}")
    print(f"   💬 Feedback: {result3['feedback']}")
    print()
    
    # ========== TEST 5: Get Statistics ==========
    print("5️⃣  GET STATISTICS")
    print("-" * 60)
    
    response = requests.get(f'{BASE_URL}/stats')
    assert response.status_code == 200
    
    stats_data = response.json()
    stats = stats_data['stats']
    accuracy = stats_data['accuracy_percent']
    
    print(f"   ✅ Status: {response.status_code}")
    print(f"   📊 Total rounds: {stats['total_rounds']}")
    print(f"   ✅ Correct: {stats['correct']}")
    print(f"   ❌ Accuracy: {accuracy}%")
    if stats['most_missed']:
        print(f"   📝 Most missed: {stats['most_missed']}")
    print()
    
    # ========== TEST 6: Get All Words ==========
    print("6️⃣  LIST ALL WORDS")
    print("-" * 60)
    
    response = requests.get(f'{BASE_URL}/words')
    assert response.status_code == 200
    
    words_data = response.json()
    word_count = words_data['count']
    
    print(f"   ✅ Status: {response.status_code}")
    print(f"   📚 Total words: {word_count}")
    print()
    
    # ========== TEST 7: Get IPA for a Word ==========
    print("7️⃣  GET IPA CONVERSION")
    print("-" * 60)
    
    test_word = word['text']
    response = requests.get(f'{BASE_URL}/pronunciation/ipa/{test_word}')
    assert response.status_code == 200
    
    ipa_data = response.json()
    
    print(f"   ✅ Status: {response.status_code}")
    print(f"   Word: {ipa_data['word']}")
    print(f"   Syllables: {' '.join(ipa_data['syllables'])}")
    print(f"   IPA: {ipa_data['ipa']}")
    print()
    
    # ========== TEST 8: Generate Sentences ==========
    print("8️⃣  GENERATE SENTENCES")
    print("-" * 60)
    
    response = requests.get(f'{BASE_URL}/pronunciation/sentences/{test_word}', params={'count': 3})
    assert response.status_code == 200
    
    sentences_data = response.json()
    
    print(f"   ✅ Status: {response.status_code}")
    print(f"   Word: {sentences_data['word']}")
    print(f"   Count: {sentences_data['count']}")
    print(f"   Examples:")
    for i, sentence in enumerate(sentences_data['sentences'][:3], 1):
        print(f"      {i}. {sentence}")
    print()
    
    # ========== SUMMARY ==========
    print("="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\n🎉 Your web application is fully functional!\n")
    print("Next steps:")
    print("   1. Open: http://localhost:8001/templates/index.html")
    print("   2. Click 'New Word' to start the quiz")
    print("   3. Select a feature and get instant feedback")
    print("   4. Watch your stats update in real-time\n")

except requests.exceptions.ConnectionError:
    print("❌ ERROR: Cannot connect to API at http://localhost:8000")
    print("   Make sure the backend is running:")
    print("   $ cd web_app/backend/api")
    print("   $ python -m uvicorn main:app --reload\n")
    
except AssertionError as e:
    print(f"❌ TEST FAILED: {e}\n")
    
except Exception as e:
    print(f"❌ ERROR: {e}\n")
    import traceback
    traceback.print_exc()
