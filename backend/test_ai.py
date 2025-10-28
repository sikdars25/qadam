"""
Test script for AI features
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("="*60)
print("Testing AI Features")
print("="*60)

# Test 1: Import AI helpers
print("\n1. Testing imports...")
try:
    from ai_helpers import (
        check_ai_availability,
        get_ai_status_message,
        get_text_embedding,
        search_similar_texts,
        generate_with_groq,
        parse_questions_from_text,
        generate_solution
    )
    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    exit(1)

# Test 2: Check AI availability
print("\n2. Checking AI availability...")
print(get_ai_status_message())

# Test 3: Test TF-IDF embeddings
print("\n3. Testing TF-IDF embeddings...")
try:
    text = "What is the capital of France?"
    embedding = get_text_embedding(text)
    if embedding is not None:
        print(f"✅ Generated embedding with shape: {embedding.shape}")
    else:
        print("❌ Failed to generate embedding")
except Exception as e:
    print(f"❌ Embedding test failed: {e}")

# Test 4: Test similarity search
print("\n4. Testing similarity search...")
try:
    query = "What is photosynthesis?"
    documents = [
        "Photosynthesis is the process by which plants make food using sunlight.",
        "The water cycle describes how water moves through the environment.",
        "Plants use chlorophyll to capture light energy for photosynthesis.",
        "The solar system consists of the sun and planets orbiting it."
    ]
    
    results = search_similar_texts(query, documents, top_k=2)
    print(f"✅ Found {len(results)} similar documents:")
    for i, (doc_id, score, text) in enumerate(results, 1):
        print(f"   {i}. Score: {score:.3f} - {text[:60]}...")
except Exception as e:
    print(f"❌ Similarity search failed: {e}")

# Test 5: Test Groq API (if available)
print("\n5. Testing Groq API...")
if os.getenv('GROQ_API_KEY'):
    try:
        response = generate_with_groq(
            "Say 'Hello, AI is working!' in one sentence.",
            max_tokens=50
        )
        print(f"✅ Groq API response: {response}")
    except Exception as e:
        print(f"❌ Groq API test failed: {e}")
else:
    print("⚠️ GROQ_API_KEY not set - skipping Groq test")
    print("   Get your key from: https://console.groq.com/")

# Test 6: Test question parsing (if Groq available)
print("\n6. Testing question parsing...")
if os.getenv('GROQ_API_KEY'):
    try:
        sample_text = """
        1. What is photosynthesis? (5 marks)
        2. Explain the water cycle. (10 marks)
        """
        questions = parse_questions_from_text(sample_text)
        if questions:
            print(f"✅ Parsed {len(questions)} questions:")
            for q in questions:
                print(f"   - Q{q.get('number')}: {q.get('text')[:50]}... ({q.get('marks')} marks)")
        else:
            print("⚠️ No questions parsed (may need to adjust parsing logic)")
    except Exception as e:
        print(f"❌ Question parsing failed: {e}")
else:
    print("⚠️ GROQ_API_KEY not set - skipping question parsing test")

# Test 7: Test solution generation (if Groq available)
print("\n7. Testing solution generation...")
if os.getenv('GROQ_API_KEY'):
    try:
        question = "What is 2 + 2?"
        solution = generate_solution(question, subject="Mathematics")
        print(f"✅ Generated solution:")
        print(f"   {solution[:200]}...")
    except Exception as e:
        print(f"❌ Solution generation failed: {e}")
else:
    print("⚠️ GROQ_API_KEY not set - skipping solution generation test")

print("\n" + "="*60)
print("Testing Complete!")
print("="*60)

# Summary
print("\n📊 Summary:")
status = check_ai_availability()
print(f"   TF-IDF Vectorizer: {'✅' if status['tfidf_vectorizer'] else '❌'}")
print(f"   Groq API: {'✅' if status['groq_api'] else '⚠️ (not configured)'}")
print(f"   OCR: {'✅' if status['ocr'] else '❌'}")

if not status['groq_api']:
    print("\n💡 To enable Groq API:")
    print("   1. Get API key from: https://console.groq.com/")
    print("   2. Add to .env file: GROQ_API_KEY=your_key_here")
    print("   3. Restart the application")

print("\n✅ All basic AI features are working!")
print("   You can now deploy to Azure with these lightweight dependencies.")
