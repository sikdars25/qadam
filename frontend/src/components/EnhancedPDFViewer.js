import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './EnhancedPDFViewer.css';

const EnhancedPDFViewer = ({ paperId, textbookId, onClose }) => {
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [solution, setSolution] = useState(null);
  const [loadingSolution, setLoadingSolution] = useState(false);
  const [showSolutionModal, setShowSolutionModal] = useState(false);
  const [showChapterPreview, setShowChapterPreview] = useState(false);
  const [selectedChapter, setSelectedChapter] = useState(null);
  const [expandedQuestions, setExpandedQuestions] = useState(new Set());
  const [error, setError] = useState('');

  useEffect(() => {
    if (paperId && textbookId) {
      analyzeQuestionPaper();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [paperId, textbookId]);

  const analyzeQuestionPaper = async () => {
    setAnalyzing(true);
    setError('');
    
    try {
      const response = await axios.post('http://localhost:5000/api/analyze-paper', {
        paper_id: paperId,
        textbook_id: textbookId
      });

      if (response.data.success) {
        setAnalysis(response.data);
      } else {
        setError(response.data.error || 'Analysis failed');
      }
    } catch (err) {
      const errorMsg = err.response?.data?.error || err.message;
      
      // Check if it's a missing dependencies error
      if (errorMsg.includes('AI features not available') || errorMsg.includes('dependencies')) {
        setError(
          '🤖 AI Features Not Installed\n\n' +
          'To enable AI-powered analysis:\n\n' +
          '1. Open terminal in backend folder\n' +
          '2. Run: pip install -r requirements-ai.txt\n' +
          '   OR run: install_ai.bat\n\n' +
          '3. Restart backend: python app.py\n\n' +
          'This will download ~500MB on first install.'
        );
      } else {
        setError('Failed to analyze question paper. ' + errorMsg);
      }
    } finally {
      setAnalyzing(false);
    }
  };

  const handleGetSolution = async (question) => {
    setSelectedQuestion(question);
    setShowSolutionModal(true);
    setLoadingSolution(true);
    setSolution(null);

    try {
      // Get context from best matching chapter
      const context = question.chapters && question.chapters.length > 0
        ? `Chapter ${question.chapters[0].chapter_number}: ${question.chapters[0].chapter_title}`
        : '';

      const response = await axios.post('http://localhost:5000/api/generate-solution', {
        question_text: question.question_text,
        context: context
      });

      if (response.data.success) {
        setSolution(response.data.solution);
      } else {
        setSolution('Failed to generate solution: ' + response.data.solution);
      }
    } catch (err) {
      setSolution('Error generating solution: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoadingSolution(false);
    }
  };

  const closeSolutionModal = () => {
    setShowSolutionModal(false);
    setSelectedQuestion(null);
    setSolution(null);
  };

  const toggleQuestion = (questionNumber) => {
    setExpandedQuestions(prev => {
      const newSet = new Set(prev);
      if (newSet.has(questionNumber)) {
        newSet.delete(questionNumber);
      } else {
        newSet.add(questionNumber);
      }
      return newSet;
    });
  };

  const formatSolution = (text) => {
    if (!text) return '';
    
    // Escape HTML first
    let formatted = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
    
    // Bold patterns for important content
    formatted = formatted
      // Final Answer / Answer / Solution patterns
      .replace(/\b(Final Answer|Answer|Solution|Result|Conclusion):\s*/gi, '<strong class="highlight-answer">$1:</strong> ')
      .replace(/\b(Final Answer|Answer|Solution|Result|Conclusion)\b/gi, '<strong class="highlight-answer">$1</strong>')
      
      // Step numbers and headings
      .replace(/^(\d+\.|Step \d+:?)\s*/gm, '<strong class="highlight-step">$1</strong> ')
      .replace(/^([A-Z][^:\n]{0,50}:)\s*/gm, '<strong class="highlight-heading">$1</strong> ')
      
      // Mathematical equations and formulas (with = sign)
      /* eslint-disable no-useless-escape */
      .replace(/([A-Za-z0-9₀-₉]+\s*[\+\-\×\÷\*\/]\s*[A-Za-z0-9₀-₉]+\s*=\s*[A-Za-z0-9₀-₉\+\-\×\÷\*\/\(\)\[\]\{\}\^\s\.]+)/g, '<strong class="highlight-formula">$1</strong>')
      .replace(/([A-Za-z0-9₀-₉]+\s*=\s*[A-Za-z0-9₀-₉\+\-\×\÷\*\/\(\)\[\]\{\}\^\s\.]+)/g, '<strong class="highlight-formula">$1</strong>')
      /* eslint-enable no-useless-escape */
      
      // Chemical formulas (H₂O, CO₂, NaCl, etc.) - only when subscripts present
      .replace(/\b([A-Z][a-z]?[₀-₉]+[A-Za-z₀-₉]*)\b/g, '<strong class="highlight-chemical">$&</strong>')
      
      // Theorem names (Pythagoras' Theorem, Newton's Law, etc.)
      .replace(/\b([A-Z][a-z]+(?:'s)?\s+(?:Theorem|Law|Principle|Rule|Formula|Equation))\b/g, '<strong class="highlight-theorem">$&</strong>')
      
      // Important keywords (but NOT "Formula", "Equation", "Theorem" alone)
      .replace(/\b(Therefore|Hence|Thus|Important|Note|Remember|Key Point|Concept|Definition)\b/gi, '<strong class="highlight-keyword">$&</strong>')
      
      // Numbers with units
      .replace(/\b(\d+\.?\d*)\s*(m|cm|mm|km|kg|g|mg|L|mL|°C|°F|K|mol|J|W|V|A|Ω|Hz|N|Pa|s|min|h|day|year)s?\b/g, '<strong class="highlight-unit">$1 $2</strong>')
      
      // Preserve line breaks
      .replace(/\n/g, '<br/>');
    
    return formatted;
  };

  return (
    <div className="enhanced-pdf-viewer">
      <div className="viewer-header">
        <h3>📊 AI-Powered Question Analysis</h3>
        <button className="close-btn" onClick={onClose}>✕</button>
      </div>

      <div className="viewer-content">
        {/* Left Panel - PDF Viewer */}
        <div className="pdf-panel">
          <div className="pdf-container">
            <iframe
              src={`http://localhost:5000/api/download-paper/${paperId}`}
              style={{ width: '100%', height: '100%', border: 'none' }}
              title="Question Paper"
            />
          </div>
        </div>

        {/* Right Panel - Analysis Results */}
        <div className="analysis-panel">
          {analyzing ? (
            <div className="analyzing-state">
              <div className="spinner"></div>
              <p>🔍 Analyzing question paper...</p>
              <p className="sub-text">Extracting questions and mapping to chapters</p>
            </div>
          ) : error ? (
            <div className="error-state">
              <p>❌ {error}</p>
              <button onClick={analyzeQuestionPaper} className="retry-btn">
                🔄 Retry Analysis
              </button>
            </div>
          ) : analysis ? (
            <div className="analysis-results">
              <div className="analysis-header">
                <h4>📝 Analysis Complete</h4>
                <div className="stats">
                  <span className="stat-badge">
                    {analysis.total_questions} Questions
                  </span>
                  <span className="stat-badge">
                    {analysis.chapters_indexed} Chapters
                  </span>
                </div>
              </div>

              <div className="questions-list">
                {analysis.questions.map((question, index) => {
                  const isExpanded = expandedQuestions.has(question.question_number);
                  return (
                    <div key={index} className={`question-accordion ${isExpanded ? 'expanded' : ''}`}>
                      <div 
                        className="accordion-header"
                        onClick={() => toggleQuestion(question.question_number)}
                      >
                        <div className="accordion-title">
                          <span className="q-number">Q{question.question_number}</span>
                          <span className="question-preview">
                            {question.question_text.substring(0, 80)}
                            {question.question_text.length > 80 ? '...' : ''}
                          </span>
                        </div>
                        <div className="accordion-actions">
                          {question.chapters && question.chapters.length > 0 && (
                            <span className="chapter-count">
                              {question.chapters.length} chapter{question.chapters.length > 1 ? 's' : ''}
                            </span>
                          )}
                          <span className="accordion-icon">{isExpanded ? '▼' : '▶'}</span>
                        </div>
                      </div>
                      
                      {isExpanded && (
                        <div className="accordion-content">
                          <div className="question-text">
                            {question.question_text}
                          </div>

                          <button
                            className="solution-btn"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleGetSolution(question);
                            }}
                          >
                            💡 Get Solution
                          </button>

                          {question.chapters && question.chapters.length > 0 && (
                            <div className="chapter-mapping">
                              <div className="mapping-label">📖 Related Chapters:</div>
                              {question.chapters.map((chapter, idx) => (
                                <div key={idx} className="chapter-card">
                                  <div className="chapter-header">
                                    <span className="chapter-info">
                                      Ch {chapter.chapter_number}: {chapter.chapter_title}
                                    </span>
                                    <span className="similarity-score">
                                      {chapter.similarity_score}% match
                                    </span>
                                  </div>
                                  <div className="chapter-meta">
                                    <span className="page-info">
                                      📄 {chapter.page_range || `Pages ${chapter.page_start}-${chapter.page_end}`}
                                    </span>
                                  </div>
                                  {chapter.preview && (
                                    <div className="chapter-preview">
                                      <div className="preview-label">Preview:</div>
                                      <div className="preview-text">{chapter.preview}</div>
                                    </div>
                                  )}
                                  <button 
                                    className="preview-chapter-btn"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      setSelectedChapter(chapter);
                                      setShowChapterPreview(true);
                                    }}
                                  >
                                    📖 View Chapter Pages
                                  </button>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            <div className="no-analysis">
              <p>Select a textbook to analyze this question paper</p>
            </div>
          )}
        </div>
      </div>

      {/* Solution Modal */}
      {showSolutionModal && (
        <div className="solution-modal-overlay" onClick={closeSolutionModal}>
          <div className="solution-modal draggable" onClick={(e) => e.stopPropagation()}>
            <div className="solution-header">
              <div className="solution-title-section">
                <h3>💡 AI-Generated Solution</h3>
                <span className="powered-by">Powered by Groq Llama 3.3</span>
              </div>
              <button className="close-btn" onClick={closeSolutionModal}>✕</button>
            </div>
            
            <div className="solution-content">
              {selectedQuestion && (
                <div className="question-display">
                  <div className="question-label">Question {selectedQuestion.question_number}</div>
                  <p className="question-text-modal">{selectedQuestion.question_text}</p>
                </div>
              )}

              {loadingSolution ? (
                <div className="loading-solution">
                  <div className="spinner"></div>
                  <p>Generating solution with AI...</p>
                </div>
              ) : solution ? (
                <div className="solution-text" dangerouslySetInnerHTML={{ __html: formatSolution(solution) }} />
              ) : null}
            </div>
          </div>
        </div>
      )}

      {/* Chapter Preview Modal */}
      {showChapterPreview && selectedChapter && (
        <div className="chapter-preview-modal-overlay" onClick={() => setShowChapterPreview(false)}>
          <div className="chapter-preview-modal" onClick={(e) => e.stopPropagation()}>
            <div className="chapter-preview-header">
              <div className="chapter-preview-title">
                <h3>📖 Chapter {selectedChapter.chapter_number}: {selectedChapter.chapter_title}</h3>
                <p className="chapter-preview-subtitle">
                  Pages {selectedChapter.page_start}-{selectedChapter.page_end} • {selectedChapter.similarity_score}% match
                </p>
              </div>
              <button className="close-btn" onClick={() => setShowChapterPreview(false)}>✕</button>
            </div>
            
            <div className="chapter-preview-content">
              <iframe
                src={`http://localhost:5000/api/textbooks/${textbookId}#page=${selectedChapter.page_start}`}
                title="Chapter Preview"
                className="pdf-preview-iframe"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedPDFViewer;
