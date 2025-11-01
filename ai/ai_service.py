"""
AI Service for Question Analysis and Solution Generation
Lightweight implementation using Groq API + scikit-learn (Azure free tier compatible)
"""

import os
import fitz  # PyMuPDF
import numpy as np
import pickle
from typing import List, Dict, Any, Optional
from ai_helpers import (
    get_text_embedding,
    search_similar_texts,
    generate_with_groq,
    parse_questions_from_text,
    generate_solution,
    map_question_to_chapters,
    fit_vectorizer
)

# ============================================================================
# PDF PROCESSING
# ============================================================================

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file"""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"❌ Error extracting text from PDF: {e}")
        return ""

def extract_pages_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """Extract text from each page of PDF"""
    try:
        doc = fitz.open(pdf_path)
        pages = []
        for page_num, page in enumerate(doc, 1):
            text = page.get_text()
            pages.append({
                'page_number': page_num,
                'text': text
            })
        doc.close()
        return pages
    except Exception as e:
        print(f"❌ Error extracting pages from PDF: {e}")
        return []

# ============================================================================
# TEXTBOOK INDEXING
# ============================================================================

class TextbookIndex:
    """Lightweight textbook index using TF-IDF"""
    
    def __init__(self, textbook_id: str):
        self.textbook_id = textbook_id
        self.chapters = []
        self.chapter_embeddings = []
        self.vectorizer = None
        
    def add_chapter(self, chapter_name: str, chapter_text: str):
        """Add a chapter to the index"""
        self.chapters.append({
            'name': chapter_name,
            'text': chapter_text
        })
    
    def build_index(self):
        """Build TF-IDF index for all chapters"""
        if not self.chapters:
            print("⚠️ No chapters to index")
            return False
        
        try:
            # Extract chapter texts
            chapter_texts = [ch['text'] for ch in self.chapters]
            
            # Fit vectorizer on all chapters
            from sklearn.feature_extraction.text import TfidfVectorizer
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                stop_words='english'
            )
            
            # Generate embeddings
            self.chapter_embeddings = self.vectorizer.fit_transform(chapter_texts).toarray()
            
            print(f"✅ Built index for {len(self.chapters)} chapters")
            return True
        except Exception as e:
            print(f"❌ Error building index: {e}")
            return False
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for relevant chapters"""
        if not self.vectorizer or len(self.chapter_embeddings) == 0:
            print("⚠️ Index not built yet")
            return []
        
        try:
            # Get query embedding
            query_embedding = self.vectorizer.transform([query]).toarray()[0]
            
            # Calculate cosine similarity
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity(
                [query_embedding],
                self.chapter_embeddings
            )[0]
            
            # Get top-k results
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                results.append({
                    'chapter_name': self.chapters[idx]['name'],
                    'chapter_text': self.chapters[idx]['text'],
                    'similarity_score': float(similarities[idx])
                })
            
            return results
        except Exception as e:
            print(f"❌ Error searching index: {e}")
            return []
    
    def save(self, filepath: str):
        """Save index to file"""
        try:
            data = {
                'textbook_id': self.textbook_id,
                'chapters': self.chapters,
                'chapter_embeddings': self.chapter_embeddings,
                'vectorizer': self.vectorizer
            }
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
            print(f"✅ Saved index to {filepath}")
            return True
        except Exception as e:
            print(f"❌ Error saving index: {e}")
            return False
    
    @classmethod
    def load(cls, filepath: str):
        """Load index from file"""
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            index = cls(data['textbook_id'])
            index.chapters = data['chapters']
            index.chapter_embeddings = data['chapter_embeddings']
            index.vectorizer = data['vectorizer']
            
            print(f"✅ Loaded index from {filepath}")
            return index
        except Exception as e:
            print(f"❌ Error loading index: {e}")
            return None

# ============================================================================
# QUESTION ANALYSIS
# ============================================================================

def analyze_question_paper(pdf_path: str, textbook_index: Optional[TextbookIndex] = None) -> Dict[str, Any]:
    """
    Analyze a question paper and map questions to textbook chapters
    
    Args:
        pdf_path: Path to question paper PDF
        textbook_index: Optional textbook index for chapter mapping
    
    Returns:
        Dictionary with parsed questions and chapter mappings
    """
    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return {'error': 'Failed to extract text from PDF'}
    
    # Parse questions using Groq API
    questions = parse_questions_from_text(text)
    
    # Map questions to chapters if textbook index provided
    if textbook_index:
        for question in questions:
            question_text = question.get('text', '')
            chapters = textbook_index.search(question_text, top_k=3)
            question['related_chapters'] = chapters
    
    return {
        'total_questions': len(questions),
        'questions': questions
    }

def generate_question_solution(question_text: str, textbook_index: Optional[TextbookIndex] = None, subject: str = "") -> str:
    """
    Generate solution for a question
    
    Args:
        question_text: The question to solve
        textbook_index: Optional textbook index for context
        subject: Subject name
    
    Returns:
        Generated solution
    """
    context = ""
    
    # Get relevant context from textbook if available
    if textbook_index:
        chapters = textbook_index.search(question_text, top_k=1)
        if chapters:
            context = chapters[0]['chapter_text'][:1000]  # First 1000 chars
    
    # Generate solution using Groq API
    solution = generate_solution(question_text, context=context, subject=subject)
    
    return solution

# ============================================================================
# TEXTBOOK PROCESSING
# ============================================================================

def index_textbook(pdf_path: str, textbook_id: str, chapter_detection: str = 'auto') -> TextbookIndex:
    """
    Index a textbook PDF for semantic search
    
    Args:
        pdf_path: Path to textbook PDF
        textbook_id: Unique identifier for textbook
        chapter_detection: How to detect chapters ('auto', 'page', 'heading')
    
    Returns:
        TextbookIndex object
    """
    index = TextbookIndex(textbook_id)
    
    # Extract pages from PDF
    pages = extract_pages_from_pdf(pdf_path)
    
    if chapter_detection == 'page':
        # Each page is a chapter
        for page in pages:
            index.add_chapter(
                f"Page {page['page_number']}",
                page['text']
            )
    elif chapter_detection == 'auto':
        # Try to detect chapters automatically
        # For now, group every 5 pages as a chapter
        for i in range(0, len(pages), 5):
            chunk_pages = pages[i:i+5]
            chapter_text = "\n".join([p['text'] for p in chunk_pages])
            index.add_chapter(
                f"Section {i//5 + 1} (Pages {chunk_pages[0]['page_number']}-{chunk_pages[-1]['page_number']})",
                chapter_text
            )
    else:
        # heading detection - use Groq to detect chapter headings
        # For now, fallback to page-based
        for page in pages:
            index.add_chapter(
                f"Page {page['page_number']}",
                page['text']
            )
    
    # Build the index
    index.build_index()
    
    return index

# ============================================================================
# SEMANTIC SEARCH
# ============================================================================

def semantic_search_textbook(query: str, textbook_index: TextbookIndex, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Perform semantic search on textbook
    
    Args:
        query: Search query
        textbook_index: Textbook index
        top_k: Number of results
    
    Returns:
        List of relevant chapters with scores
    """
    return textbook_index.search(query, top_k=top_k)

# ============================================================================
# BATCH PROCESSING
# ============================================================================

def batch_generate_solutions(questions: List[str], textbook_index: Optional[TextbookIndex] = None, subject: str = "") -> List[Dict[str, str]]:
    """
    Generate solutions for multiple questions
    
    Args:
        questions: List of question texts
        textbook_index: Optional textbook index
        subject: Subject name
    
    Returns:
        List of dictionaries with question and solution
    """
    results = []
    
    for i, question in enumerate(questions, 1):
        print(f"Generating solution {i}/{len(questions)}...")
        solution = generate_question_solution(question, textbook_index, subject)
        results.append({
            'question': question,
            'solution': solution
        })
    
    return results

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_service_status() -> Dict[str, Any]:
    """Get AI service status"""
    from ai_helpers import check_ai_availability
    
    status = check_ai_availability()
    
    return {
        'groq_api': status['groq_api'],
        'tfidf_vectorizer': status['tfidf_vectorizer'],
        'ocr': status['ocr'],
        'ready': status['groq_api'] and status['tfidf_vectorizer']
    }

# Print status on import
print("\n" + "="*60)
print("AI Service (Lightweight) - Status:")
status = get_service_status()
print(f"  Groq API: {'✅' if status['groq_api'] else '⚠️ Not configured'}")
print(f"  TF-IDF: {'✅' if status['tfidf_vectorizer'] else '❌'}")
print(f"  OCR: {'✅' if status['ocr'] else '❌'}")
print(f"  Service Ready: {'✅' if status['ready'] else '⚠️'}")
print("="*60 + "\n")
