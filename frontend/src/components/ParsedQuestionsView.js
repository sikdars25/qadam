import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ParsedQuestionsView.css';
import API_URL from '../config/api';

const ParsedQuestionsView = ({ paperId, onClose, embedded = false }) => {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDiagram, setSelectedDiagram] = useState(null);
  const [selectedPaper, setSelectedPaper] = useState(paperId || 'all');
  const [groupByPaper, setGroupByPaper] = useState(!paperId); // Group by default when viewing all
  // eslint-disable-next-line no-unused-vars
  const [selectedReasoning, setSelectedReasoning] = useState(null);
  const [solvingQuestion, setSolvingQuestion] = useState(false);
  const [selectedSolution, setSelectedSolution] = useState(null);

  // Parse question text to extract main question, MCQ options, and instructions
  const parseQuestionContent = (text) => {
    if (!text) return { mainQuestion: '', mcqOptions: [], instructions: '' };
    
    // Extract inline instructions in format: [Instruction: ...]
    const inlineInstructionMatch = text.match(/\[Instruction:\s*([^\]]+)\]/i);
    const instructions = inlineInstructionMatch ? inlineInstructionMatch[1].trim() : '';
    
    // Remove inline instruction from text
    let remainingText = inlineInstructionMatch ? text.replace(inlineInstructionMatch[0], '').trim() : text;
    
    // Extract MCQ options: (A), (B), (C), (D) or A), B), C), D)
    // eslint-disable-next-line no-useless-escape
    const mcqPattern = /\(([A-D])\)\s*([^\(\)]+?)(?=\([A-D]\)|$)/gi;
    const mcqMatches = [...remainingText.matchAll(mcqPattern)];
    
    let mcqOptions = [];
    let mainQuestion = remainingText;
    
    if (mcqMatches.length >= 2) {
      // Extract MCQ options
      mcqOptions = mcqMatches.map(match => ({
        label: match[1],
        text: match[2].trim()
      }));
      
      // Remove MCQ options from main question
      mcqMatches.forEach(match => {
        mainQuestion = mainQuestion.replace(match[0], '');
      });
      mainQuestion = mainQuestion.trim();
    }
    
    return { mainQuestion, mcqOptions, instructions };
  };
  
  // Format question text to show sub-parts on new lines
  const formatQuestionText = (text) => {
    if (!text) return text;
    
    // Split by common sub-part patterns: (a), (b), (c) or a), b), c) or (i), (ii), i), ii)
    // Look ahead to split before these patterns
    const parts = text.split(/(?=\n?\s*\(?[a-z]\)\s)|(?=\n?\s*\(?[ivx]+\)\s)/i);
    
    return (
      <div>
        {parts.map((part, idx) => {
          const trimmedPart = part.trim();
          if (!trimmedPart) return null;
          
          // Check if this part starts with a sub-number like (a), a), (i), i), etc.
          const isSubPart = /^\(?[a-z]\)|^\(?[ivx]+\)/i.test(trimmedPart);
          
          return (
            <div key={idx} className={isSubPart ? 'sub-part-line' : 'main-question-line'}>
              {trimmedPart}
            </div>
          );
        })}
      </div>
    );
  };

  useEffect(() => {
    fetchParsedQuestions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [paperId]);

  const fetchParsedQuestions = async () => {
    try {
      const url = paperId 
        ? `${API_URL}/api/parsed-questions?paper_id=${paperId}`
        : `${API_URL}/api/parsed-questions`;
      
      const response = await axios.get(url);
      setQuestions(response.data);
    } catch (err) {
      console.error('Error fetching parsed questions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSolveQuestion = async (question) => {
    setSolvingQuestion(true);
    try {
      const response = await axios.post(`${API_URL}/api/solve-question`, {
        question_text: question.question_text,
        question_type: question.question_type,
        subject: question.subject,
        chapter_context: null
      });
      
      if (response.data.success) {
        setSelectedSolution({
          questionNumber: question.question_number,
          questionText: question.question_text,
          questionType: question.question_type,
          solution: response.data.solution,
          parsedSolution: response.data.parsed_solution
        });
        
        // Save to Question Bank
        try {
          await axios.post(`${API_URL}/api/save-solved-question`, {
            question_text: question.question_text,
            solution: response.data.solution,
            subject: question.subject,
            source: 'all_questions',
            paper_id: question.paper_id,
            textbook_id: null,
            chapter_name: null,
            timestamp: new Date().toISOString()
          });
          console.log('✅ Question saved to Question Bank with subject:', question.subject);
        } catch (saveErr) {
          console.error('Failed to save to Question Bank:', saveErr);
        }
      } else {
        alert('Failed to solve question: ' + (response.data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error solving question:', error);
      alert('Error solving question: ' + (error.response?.data?.error || error.message));
    } finally {
      setSolvingQuestion(false);
    }
  };

  const filteredQuestions = questions.filter(q => {
    const matchesFilter = filter === 'all' || q.question_type === filter;
    const matchesSearch = q.question_text.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         q.question_number.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesPaper = selectedPaper === 'all' || q.paper_id === parseInt(selectedPaper);
    return matchesFilter && matchesSearch && matchesPaper;
  });

  const questionTypes = [...new Set(questions.map(q => q.question_type))];
  
  // Get unique papers
  const papers = [...new Map(questions.map(q => [q.paper_id, { id: q.paper_id, title: q.paper_title, subject: q.subject }])).values()];
  
  // Group questions by paper
  const groupedQuestions = {};
  filteredQuestions.forEach(q => {
    const key = `${q.paper_id}_${q.paper_title}`;
    if (!groupedQuestions[key]) {
      groupedQuestions[key] = {
        paper_id: q.paper_id,
        paper_title: q.paper_title,
        subject: q.subject,
        questions: []
      };
    }
    groupedQuestions[key].questions.push(q);
  });

  const containerClass = embedded ? "parsed-questions-embedded" : "parsed-questions-modal";
  const innerClass = embedded ? "parsed-questions-content" : "parsed-questions-container";

  return (
    <div className={containerClass}>
      <div className={innerClass}>
        <div className="parsed-header">
          <div>
            <h2>📋 All Parsed Questions</h2>
            <p>{questions.length} questions from {papers.length} paper(s)</p>
          </div>
          {!embedded && <button className="close-btn" onClick={onClose}>✕</button>}
        </div>

        <div className="parsed-controls">
          <input
            type="text"
            placeholder="🔍 Search questions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />

          {!paperId && (
            <select 
              value={selectedPaper} 
              onChange={(e) => setSelectedPaper(e.target.value)}
              className="filter-select"
            >
              <option value="all">All Papers ({papers.length})</option>
              {papers.map(paper => (
                <option key={paper.id} value={paper.id}>
                  {paper.title} - {paper.subject}
                </option>
              ))}
            </select>
          )}

          <select 
            value={filter} 
            onChange={(e) => setFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Types</option>
            {questionTypes.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>

          {!paperId && !embedded && (
            <label className="group-toggle">
              <input
                type="checkbox"
                checked={groupByPaper}
                onChange={(e) => setGroupByPaper(e.target.checked)}
              />
              Group by Paper
            </label>
          )}

          <div className="results-count">
            {filteredQuestions.length} of {questions.length} questions
          </div>
        </div>

        {loading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading parsed questions...</p>
          </div>
        ) : groupByPaper && !paperId ? (
          <div className="questions-list">
            {Object.values(groupedQuestions).map((group) => (
              <div key={group.paper_id} className="paper-group">
                <div className="paper-group-header">
                  <h3>📄 {group.paper_title}</h3>
                  <span className="paper-subject">{group.subject}</span>
                  <span className="question-count-badge">{group.questions.length} questions</span>
                </div>
                {group.questions.map((q, index) => {
                  const parsedData = q.parsed_data ? JSON.parse(q.parsed_data) : {};
                  
                  let displayNumber = q.question_number;
                  // eslint-disable-next-line no-useless-escape
                  const numberMatch = q.question_text.match(/^(\d+)\s*[\.\)]/);
                  if (numberMatch) {
                    displayNumber = numberMatch[1];
                  }
                  
                  return (
                    <div key={q.id} className="parsed-question-card">
                      <div className="question-header-row">
                        <div className="question-number-badge">
                          Q{displayNumber}
                        </div>
                        
                        <div className="question-meta-tags">
                          <span className={`type-badge ${q.question_type}`}>
                            {q.question_type}
                          </span>
                          
                          {q.has_diagram && parsedData.diagram_files && parsedData.diagram_files.length > 0 && (
                            <span 
                              className="diagram-badge clickable"
                              onClick={() => {
                                console.log('Diagram badge clicked:', { paperId: q.paper_id, filename: parsedData.diagram_files[0] });
                                setSelectedDiagram({ paperId: q.paper_id, filename: parsedData.diagram_files[0] });
                              }}
                            >
                              📊 Diagram {parsedData.diagram_files.length > 1 ? `(${parsedData.diagram_files.length})` : ''}
                            </span>
                          )}
                          
                          {q.marks && (
                            <span className="marks-badge">{q.marks} marks</span>
                          )}
                          
                          <button 
                            className="solve-btn"
                            onClick={() => handleSolveQuestion(q)}
                            disabled={solvingQuestion}
                            title="Get detailed step-by-step solution"
                          >
                            {solvingQuestion ? '⏳ Solving...' : '✨ Solve Question'}
                          </button>
                        </div>
                      </div>

                      {(() => {
                        const { mainQuestion, mcqOptions, instructions } = parseQuestionContent(q.question_text);
                        
                        return (
                          <>
                            <div className="question-text-display">
                              {formatQuestionText(mainQuestion)}
                              {instructions && (
                                <span className="inline-instruction"> [Instruction: {instructions}]</span>
                              )}
                            </div>
                            
                            {mcqOptions.length > 0 && (
                              <div className="mcq-options-display">
                                {mcqOptions.map((option, idx) => (
                                  <div key={idx} className="mcq-option">
                                    <span className="mcq-option-label">({option.label})</span>
                                    <span className="mcq-option-text">{option.text}</span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </>
                        );
                      })()}

                      {parsedData.sub_parts && parsedData.sub_parts.length > 0 && (
                        <div className="sub-parts-display">
                          <strong>Sub-parts:</strong>
                          <div className="sub-parts-list">
                            {parsedData.sub_parts.map((part, idx) => (
                              <div key={idx} className="sub-part-item">{part}</div>
                            ))}
                          </div>
                        </div>
                      )}

                      {parsedData.diagram_files && parsedData.diagram_files.length > 0 && (
                        <div className="diagrams-inline-display">
                          <strong>📊 Diagram{parsedData.diagram_files.length > 1 ? 's' : ''}:</strong>
                          <div className="diagrams-inline-container">
                            {parsedData.diagram_files.map((filename, idx) => (
                              <div key={idx} className="diagram-inline-wrapper">
                                <img 
                                  src={`${API_URL}/api/diagram/${q.paper_id}/${filename}`}
                                  alt={`Diagram ${idx + 1}`}
                                  className="diagram-inline"
                                  onClick={() => {
                                    console.log('Diagram clicked:', { paperId: q.paper_id, filename });
                                    setSelectedDiagram({ paperId: q.paper_id, filename });
                                  }}
                                  onError={(e) => e.target.style.display = 'none'}
                                />
                                <span className="diagram-caption">Click to enlarge</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="question-footer">
                        <span className="created-date">
                          {new Date(q.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        ) : (
          <div className="questions-list">
            {filteredQuestions.map((q, index) => {
              const parsedData = q.parsed_data ? JSON.parse(q.parsed_data) : {};
              
              // Extract question number from question_text if it starts with a number
              let displayNumber = q.question_number;
              // eslint-disable-next-line no-useless-escape
              const numberMatch = q.question_text.match(/^(\d+)\s*[\.\)]/);
              if (numberMatch) {
                displayNumber = numberMatch[1];
              }
              
              return (
                <div key={q.id} className="parsed-question-card">
                  <div className="question-header-row">
                    <div className="question-number-badge">
                      Q{displayNumber}
                    </div>
                    
                    <div className="question-meta-tags">
                      <span className={`type-badge ${q.question_type}`}>
                        {q.question_type}
                      </span>
                      
                      {q.has_diagram && parsedData.diagram_files && parsedData.diagram_files.length > 0 && (
                        <span 
                          className="diagram-badge clickable"
                          onClick={() => {
                            console.log('Diagram badge clicked (ungrouped):', { paperId: q.paper_id, filename: parsedData.diagram_files[0] });
                            setSelectedDiagram({ paperId: q.paper_id, filename: parsedData.diagram_files[0] });
                          }}
                        >
                          📊 Diagram {parsedData.diagram_files.length > 1 ? `(${parsedData.diagram_files.length})` : ''}
                        </span>
                      )}
                      
                      {q.marks && (
                        <span className="marks-badge">{q.marks} marks</span>
                      )}
                      
                      <button 
                        className="solve-btn"
                        onClick={() => handleSolveQuestion(q)}
                        disabled={solvingQuestion}
                        title="Get detailed step-by-step solution"
                      >
                        {solvingQuestion ? '⏳ Solving...' : '✨ Solve Question'}
                      </button>
                    </div>
                  </div>

                  {(() => {
                    const { mainQuestion, mcqOptions, instructions } = parseQuestionContent(q.question_text);
                    
                    return (
                      <>
                        <div className="question-text-display">
                          {formatQuestionText(mainQuestion)}
                          {instructions && (
                            <span className="inline-instruction"> [Instruction: {instructions}]</span>
                          )}
                        </div>
                        
                        {mcqOptions.length > 0 && (
                          <div className="mcq-options-display">
                            {mcqOptions.map((option, idx) => (
                              <div key={idx} className="mcq-option">
                                <span className="mcq-option-label">({option.label})</span>
                                <span className="mcq-option-text">{option.text}</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </>
                    );
                  })()}

                  {parsedData.sub_parts && parsedData.sub_parts.length > 0 && (
                    <div className="sub-parts-display">
                      <strong>Sub-parts:</strong>
                      <div className="sub-parts-list">
                        {parsedData.sub_parts.map((part, idx) => (
                          <div key={idx} className="sub-part-item">{part}</div>
                        ))}
                      </div>
                    </div>
                  )}

                  {parsedData.diagram_files && parsedData.diagram_files.length > 0 && (
                    <div className="diagrams-inline-display">
                      <strong>📊 Diagram{parsedData.diagram_files.length > 1 ? 's' : ''}:</strong>
                      <div className="diagrams-inline-container">
                        {parsedData.diagram_files.map((filename, idx) => (
                          <div key={idx} className="diagram-inline-wrapper">
                            <img 
                              src={`${API_URL}/api/diagram/${q.paper_id}/${filename}`}
                              alt={`Diagram ${idx + 1}`}
                              className="diagram-inline"
                              onClick={() => {
                                console.log('Diagram clicked (ungrouped):', { paperId: q.paper_id, filename });
                                setSelectedDiagram({ paperId: q.paper_id, filename });
                              }}
                              onError={(e) => e.target.style.display = 'none'}
                            />
                            <span className="diagram-caption">Click to enlarge</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="question-footer">
                    <span className="paper-info">
                      📄 {q.paper_title} • {q.subject}
                    </span>
                    <span className="created-date">
                      {new Date(q.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              );
            })}

            {filteredQuestions.length === 0 && (
              <div className="no-questions">
                <p>No questions found matching your criteria</p>
              </div>
            )}
          </div>
        )}

        {/* Diagram Modal */}
        {selectedDiagram && (
          <div className="diagram-modal" onClick={() => setSelectedDiagram(null)}>
            <div className="diagram-modal-content" onClick={(e) => e.stopPropagation()}>
              <button className="close-diagram-btn" onClick={() => setSelectedDiagram(null)}>✕</button>
              <img 
                src={`${API_URL}/api/diagram/${selectedDiagram.paperId}/${selectedDiagram.filename}`}
                alt="Diagram"
                className="diagram-full"
                onLoad={() => console.log('Modal diagram loaded')}
                onError={(e) => console.error('Modal diagram failed to load', e)}
              />
            </div>
          </div>
        )}
        {selectedDiagram && console.log('Modal should be visible, selectedDiagram:', selectedDiagram)}

        {/* Solution Modal */}
        {selectedSolution && (
          <div className="solution-modal" onClick={() => setSelectedSolution(null)}>
            <div className="solution-modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="solution-modal-header">
                <div>
                  <h3>✨ Step-by-Step Solution - Q{selectedSolution.questionNumber}</h3>
                  <span className="solution-type-badge">{selectedSolution.questionType}</span>
                </div>
                <button className="close-solution-btn" onClick={() => setSelectedSolution(null)}>✕</button>
              </div>
              
              <div className="solution-modal-body">
                {/* Question Display */}
                <div className="solution-question-box">
                  <h4>📝 Question:</h4>
                  <p>{selectedSolution.questionText}</p>
                </div>

                {/* Full Solution */}
                <div className="solution-content">
                  <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
                    {selectedSolution.solution}
                  </pre>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ParsedQuestionsView;
