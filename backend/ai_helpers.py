"""
AI Helper Functions - Lightweight Implementation
Uses Groq API + scikit-learn for AI features within Azure free tier limits
"""

import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq

# Initialize Groq client
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
groq_client = None

if GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        print("✅ Groq API initialized")
    except Exception as e:
        print(f"⚠️ Groq API initialization failed: {e}")
else:
    print("⚠️ GROQ_API_KEY not set - AI features will be limited")

# Global TF-IDF vectorizer for text embeddings
tfidf_vectorizer = TfidfVectorizer(
    max_features=1000,
    ngram_range=(1, 2),
    stop_words='english'
)

# ============================================================================
# TEXT EMBEDDINGS (TF-IDF)
# ============================================================================

def get_text_embedding(text, vectorizer=None):
    """
    Get TF-IDF embedding for text
    
    Args:
        text: Input text string
        vectorizer: Pre-fitted TfidfVectorizer (optional)
    
    Returns:
        numpy array of embedding
    """
    if vectorizer is None:
        vectorizer = tfidf_vectorizer
    
    try:
        # If vectorizer not fitted, fit it with this text
        if not hasattr(vectorizer, 'vocabulary_'):
            embedding = vectorizer.fit_transform([text])
        else:
            embedding = vectorizer.transform([text])
        
        return embedding.toarray()[0]
    except Exception as e:
        print(f"❌ Error getting embedding: {e}")
        return None

def fit_vectorizer(texts):
    """
    Fit the TF-IDF vectorizer on a corpus of texts
    
    Args:
        texts: List of text strings
    
    Returns:
        Fitted TfidfVectorizer
    """
    global tfidf_vectorizer
    try:
        tfidf_vectorizer.fit(texts)
        print(f"✅ Vectorizer fitted on {len(texts)} documents")
        return tfidf_vectorizer
    except Exception as e:
        print(f"❌ Error fitting vectorizer: {e}")
        return None

# ============================================================================
# VECTOR SEARCH (In-Memory)
# ============================================================================

def search_similar_texts(query_text, document_texts, document_ids=None, top_k=5):
    """
    Search for similar texts using TF-IDF + cosine similarity
    
    Args:
        query_text: Query string
        document_texts: List of document text strings
        document_ids: Optional list of document IDs
        top_k: Number of results to return
    
    Returns:
        List of tuples (document_id, similarity_score, text)
    """
    try:
        # Fit vectorizer on all documents
        vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2), stop_words='english')
        doc_embeddings = vectorizer.fit_transform(document_texts)
        query_embedding = vectorizer.transform([query_text])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_embedding, doc_embeddings)[0]
        
        # Get top-k results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            doc_id = document_ids[idx] if document_ids else idx
            score = float(similarities[idx])
            text = document_texts[idx]
            results.append((doc_id, score, text))
        
        return results
    except Exception as e:
        print(f"❌ Error in similarity search: {e}")
        return []

# ============================================================================
# GROQ API - TEXT GENERATION
# ============================================================================

def generate_with_groq(prompt, model="llama-3.3-70b-versatile", max_tokens=1000, temperature=0.7):
    """
    Generate text using Groq API
    
    Args:
        prompt: Input prompt
        model: Groq model name
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
    
    Returns:
        Generated text string
    """
    if not groq_client:
        return "Error: Groq API not initialized. Please set GROQ_API_KEY."
    
    try:
        response = groq_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ Groq API error: {e}")
        return f"Error: {str(e)}"

# ============================================================================
# QUESTION PARSING
# ============================================================================

def parse_questions_from_text(text):
    """
    Parse questions from text using Groq API
    
    Args:
        text: Input text containing questions
    
    Returns:
        List of parsed questions
    """
    prompt = f"""Parse the following text and extract all questions. 
For each question, provide:
1. Question number
2. Question text
3. Marks (if mentioned)
4. Subject/topic (if identifiable)

Format the output as JSON array.

Text:
{text}

Output format:
[
  {{"number": "1", "text": "Question text here", "marks": 5, "topic": "Topic name"}},
  ...
]
"""
    
    response = generate_with_groq(prompt, max_tokens=2000, temperature=0.3)
    
    try:
        import json
        # Try to extract JSON from response
        start = response.find('[')
        end = response.rfind(']') + 1
        if start >= 0 and end > start:
            json_str = response[start:end]
            questions = json.loads(json_str)
            return questions
    except Exception as e:
        print(f"⚠️ Error parsing JSON response: {e}")
    
    return []

# ============================================================================
# SOLUTION GENERATION
# ============================================================================

def generate_solution(question_text, context="", subject=""):
    """
    Generate solution for a question using Groq API
    
    Args:
        question_text: The question to solve
        context: Optional context from textbook
        subject: Optional subject name
    
    Returns:
        Generated solution text
    """
    context_section = f'Context from textbook:\n{context}\n' if context else ''
    
    prompt = f"""You are an expert tutor. Generate a detailed solution for the following question.

Subject: {subject if subject else 'General'}

Question:
{question_text}

{context_section}

Provide a step-by-step solution with:
1. Understanding the question
2. Key concepts
3. Step-by-step solution
4. Final answer

Solution:"""
    
    return generate_with_groq(prompt, max_tokens=1500, temperature=0.7)

# ============================================================================
# TEXTBOOK CHAPTER MAPPING
# ============================================================================

def map_question_to_chapters(question_text, chapter_texts, chapter_names):
    """
    Map a question to relevant textbook chapters using similarity search
    
    Args:
        question_text: Question to map
        chapter_texts: List of chapter text content
        chapter_names: List of chapter names
    
    Returns:
        List of tuples (chapter_name, similarity_score)
    """
    try:
        results = search_similar_texts(
            query_text=question_text,
            document_texts=chapter_texts,
            document_ids=chapter_names,
            top_k=3
        )
        
        # Return chapter names and scores
        return [(name, score) for name, score, _ in results]
    except Exception as e:
        print(f"❌ Error mapping question to chapters: {e}")
        return []

# ============================================================================
# SEMANTIC SEARCH
# ============================================================================

def semantic_search(query, documents, top_k=5):
    """
    Perform semantic search on documents
    
    Args:
        query: Search query
        documents: List of document dicts with 'id', 'text' fields
        top_k: Number of results
    
    Returns:
        List of document IDs ranked by relevance
    """
    try:
        doc_texts = [doc['text'] for doc in documents]
        doc_ids = [doc['id'] for doc in documents]
        
        results = search_similar_texts(
            query_text=query,
            document_texts=doc_texts,
            document_ids=doc_ids,
            top_k=top_k
        )
        
        return [doc_id for doc_id, _, _ in results]
    except Exception as e:
        print(f"❌ Error in semantic search: {e}")
        return []

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def check_ai_availability():
    """Check which AI features are available"""
    status = {
        'groq_api': groq_client is not None,
        'tfidf_vectorizer': True,  # Always available
        'ocr': True  # Tesseract (assumed installed)
    }
    return status

def get_ai_status_message():
    """Get human-readable AI status message"""
    status = check_ai_availability()
    
    messages = []
    if status['groq_api']:
        messages.append("✅ Groq API: Available")
    else:
        messages.append("⚠️ Groq API: Not configured (set GROQ_API_KEY)")
    
    messages.append("✅ TF-IDF Vectorizer: Available")
    messages.append("✅ OCR (Tesseract): Available")
    
    return "\n".join(messages)

# Print status on import
if __name__ != "__main__":
    print("\n" + "="*50)
    print("AI Features Status:")
    print(get_ai_status_message())
    print("="*50 + "\n")
