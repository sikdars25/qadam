import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ChapterQuestions.css';

const ChapterQuestions = () => {
  const [papers, setPapers] = useState([]);
  const [textbooks, setTextbooks] = useState([]);
  const [selectedPaper, setSelectedPaper] = useState(null);
  const [selectedTextbook, setSelectedTextbook] = useState(null);
  // eslint-disable-next-line no-unused-vars
  const [chapters, setChapters] = useState([]);
  // eslint-disable-next-line no-unused-vars
  const [chapterStats, setChapterStats] = useState([]);
  const [selectedChapter, setSelectedChapter] = useState(null);
  const [questions, setQuestions] = useState([]);
  // eslint-disable-next-line no-unused-vars
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [showTextbookModal, setShowTextbookModal] = useState(false);
  const [textbookPageToShow, setTextbookPageToShow] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [semanticSearchResults, setSemanticSearchResults] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedReasoning, setSelectedReasoning] = useState(null);
  const [selectedSolution, setSelectedSolution] = useState(null);
  const [solvingQuestion, setSolvingQuestion] = useState(false);
  const [selectedDiagram, setSelectedDiagram] = useState(null);

  // Predefined textbooks with chapters and page numbers
  const defaultTextbooks = {
    'Physics': [
      {
        name: 'NCERT Physics Class 10',
        pdfUrl: 'https://ncert.nic.in/textbook/pdf/keph101.pdf',
        externalUrl: 'https://ncert.nic.in/textbook.php?keph1=0-8',
        imageBasePath: '/textbooks/physics-class10/pages/',
        chapters: [
          { name: 'Electricity', pages: '1-20' },
          { name: 'Magnetic Effects of Current', pages: '21-40' },
          { name: 'Light - Reflection and Refraction', pages: '41-65' },
          { name: 'Human Eye and Colourful World', pages: '66-85' },
          { name: 'Sources of Energy', pages: '86-105' }
        ]
      }
    ],
    'Chemistry': [
      {
        name: 'NCERT Chemistry Class 10',
        pdfUrl: 'https://ncert.nic.in/textbook/pdf/kesc101.pdf',
        externalUrl: 'https://ncert.nic.in/textbook.php?kesc1=0-8',
        imageBasePath: '/textbooks/chemistry-class10/pages/',
        chapters: [
          { name: 'Chemical Reactions and Equations', pages: '1-18' },
          { name: 'Acids, Bases and Salts', pages: '19-35' },
          { name: 'Metals and Non-metals', pages: '36-55' },
          { name: 'Carbon and its Compounds', pages: '56-80' },
          { name: 'Periodic Classification of Elements', pages: '81-95' }
        ]
      }
    ],
    'Biology': [
      {
        name: 'NCERT Biology Class 10',
        pdfUrl: 'https://ncert.nic.in/textbook/pdf/kebo101.pdf',
        externalUrl: 'https://ncert.nic.in/textbook.php?kebo1=0-8',
        imageBasePath: '/textbooks/biology-class10/pages/',
        chapters: [
          { name: 'Life Processes', pages: '1-25' },
          { name: 'Control and Coordination', pages: '26-45' },
          { name: 'How do Organisms Reproduce', pages: '46-70' },
          { name: 'Heredity and Evolution', pages: '71-90' },
          { name: 'Our Environment', pages: '91-110' }
        ]
      }
    ],
    'Mathematics': [
      {
        name: 'NCERT Mathematics Class 10',
        pdfUrl: 'https://ncert.nic.in/textbook/pdf/kemh101.pdf',
        externalUrl: 'https://ncert.nic.in/textbook.php?kemh1=0-16',
        imageBasePath: '/textbooks/mathematics-class10/pages/',
        chapters: [
          { name: 'Real Numbers', pages: '1-15' },
          { name: 'Polynomials', pages: '16-30' },
          { name: 'Pair of Linear Equations in Two Variables', pages: '31-50' },
          { name: 'Quadratic Equations', pages: '51-70' },
          { name: 'Arithmetic Progressions', pages: '71-85' },
          { name: 'Triangles', pages: '86-110' },
          { name: 'Coordinate Geometry', pages: '111-130' },
          { name: 'Introduction to Trigonometry', pages: '131-150' },
          { name: 'Some Applications of Trigonometry', pages: '151-165' },
          { name: 'Circles', pages: '166-185' },
          { name: 'Areas Related to Circles', pages: '186-200' },
          { name: 'Surface Areas and Volumes', pages: '201-225' },
          { name: 'Statistics', pages: '226-245' },
          { name: 'Probability', pages: '246-260' }
        ]
      }
    ]
  };

  useEffect(() => {
    fetchPapers();
    fetchAllTextbooks();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (selectedPaper && selectedTextbook) {
      calculateChapterStats();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedPaper, selectedTextbook]);

  const fetchPapers = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/uploaded-papers');
      setPapers(response.data);
    } catch (err) {
      console.error('Error fetching papers:', err);
      setMessage({ type: 'error', text: 'Failed to load papers' });
    }
  };

  const fetchAllTextbooks = async () => {
    try {
      // Fetch all uploaded textbooks
      const response = await axios.get('http://localhost:5000/api/textbooks');
      const uploadedTextbooks = response.data || [];
      
      // Use uploaded textbooks directly, with default chapter structure as fallback
      const textbooksToDisplay = uploadedTextbooks.map(uploaded => {
        // Get default chapters for this subject if available
        const defaultForSubject = defaultTextbooks[uploaded.subject]?.[0];
        
        return {
          name: uploaded.title,  // Use actual uploaded title
          subject: uploaded.subject,
          uploadedFile: uploaded.file_path,
          uploadedId: uploaded.id,
          uploadedTitle: uploaded.title,
          chapters: defaultForSubject?.chapters || [],  // Use default chapters as template
          pdfUrl: '',
          externalUrl: '',
          imageBasePath: ''
        };
      });
      
      setTextbooks(textbooksToDisplay);
      
      // If no textbooks uploaded, show message
      if (textbooksToDisplay.length === 0) {
        setMessage({ 
          type: 'info', 
          text: 'No textbooks uploaded yet. Please upload a textbook first.' 
        });
      }
    } catch (err) {
      console.error('Error fetching textbooks:', err);
      setMessage({ 
        type: 'error', 
        text: 'Failed to load textbooks. Please try again.' 
      });
      setTextbooks([]);
    }
  };

  const handlePaperSelect = (paper) => {
    setSelectedPaper(paper);
    setSelectedTextbook(null);
    setSelectedChapter(null);
    setQuestions([]);
    setChapters([]);
    setChapterStats([]);
    setSemanticSearchResults(null);  // Clear previous search results
    
    // Don't reload textbooks - they're already loaded with correct names
    // Just clear the selection and let user select from existing list
  };

  const handleTextbookSelect = (textbook) => {
    setSelectedTextbook(textbook);
    setSelectedChapter(null);
    setQuestions([]);
    setChapters(textbook.chapters);
    setSemanticSearchResults(null);  // Clear previous search results when textbook changes
    
    // Log textbook info for debugging
    console.log('Selected textbook:', textbook.name);
    console.log('Has uploaded file:', !!textbook.uploadedId);
    
    // Don't show selection message - table selection is clear enough
  };

  const calculateChapterStats = async () => {
    if (!selectedPaper || !selectedTextbook) return;

    try {
      // Fetch all questions from the selected paper
      const response = await axios.get(
        `http://localhost:5000/api/parsed-questions?paper_id=${selectedPaper.id}`
      );
      
      const allQuestions = response.data;
      
      // Calculate question count for each chapter
      const stats = selectedTextbook.chapters.map(chapter => {
        const chapterQuestions = filterQuestionsByChapter(allQuestions, chapter.name);
        return {
          ...chapter,
          questionCount: chapterQuestions.length
        };
      });
      
      setChapterStats(stats);
    } catch (err) {
      console.error('Error calculating chapter stats:', err);
    }
  };

  // Removed unused function handleClearResults

  const handleIndexAndMatch = async () => {
    // Unified workflow: Index textbook (if needed) + Run AI Search
    if (!selectedPaper || !selectedTextbook) {
      setMessage({ type: 'warning', text: 'Please select both a question paper and textbook first' });
      return;
    }

    if (!selectedTextbook.uploadedId) {
      setMessage({ type: 'warning', text: 'Please upload the textbook first' });
      return;
    }

    setIsSearching(true);

    try {
      // Step 1: Check if textbook is already indexed by trying to run search
      console.log('🚀 Starting Index & Match workflow...');
      setMessage({ type: 'info', text: '🔍 Checking if textbook is indexed...' });

      let needsIndexing = false;

      // Try to get chapters to see if indexed
      try {
        await axios.get(`http://localhost:5000/api/textbook-chapters/${selectedTextbook.uploadedId}`);
        console.log('✓ Textbook already indexed');
        setMessage({ type: 'info', text: '✓ Textbook already indexed. Running AI search...' });
      } catch (err) {
        if (err.response?.status === 404 || err.response?.data?.error?.includes('No vector index')) {
          needsIndexing = true;
          console.log('⚠ Textbook not indexed, will index now');
        } else {
          throw err;
        }
      }

      // Step 2: Index if needed
      if (needsIndexing) {
        setMessage({ type: 'info', text: '📚 Indexing textbook... This may take a few minutes.' });
        
        const indexResponse = await axios.post(
          `http://localhost:5000/api/index-textbook/${selectedTextbook.uploadedId}`
        );

        if (!indexResponse.data.success) {
          throw new Error(indexResponse.data.error || 'Indexing failed');
        }

        console.log(`✓ Indexed ${indexResponse.data.chapters_count} chapters`);
        setMessage({ 
          type: 'info', 
          text: `✅ Indexed ${indexResponse.data.chapters_count} chapters. Now matching questions...` 
        });
      }

      // Step 3: Run AI Search
      setMessage({ type: 'info', text: '🤖 Running AI Search with LLM analysis...' });

      // Fetch all questions from the selected paper
      const questionsResponse = await axios.get(
        `http://localhost:5000/api/parsed-questions?paper_id=${selectedPaper.id}`
      );
      
      const allQuestions = questionsResponse.data;

      // Use semantic search to map questions to chapters
      const mappingResponse = await axios.post(
        'http://localhost:5000/api/map-questions-to-chapters',
        {
          questions: allQuestions,
          textbook_id: selectedTextbook.uploadedId
        }
      );
      
      if (mappingResponse.data.success) {
        const mappedQuestions = mappingResponse.data.mapped_questions;
        
        // Group questions by chapter
        const chapterGroups = {};
        const unmatchedQuestions = [];
        
        mappedQuestions.forEach(q => {
          if (q.chapters && q.chapters.length > 0) {
            const topChapter = q.chapters[0];
            const chapterKey = topChapter.chapter_title;
            
            if (!chapterGroups[chapterKey]) {
              chapterGroups[chapterKey] = {
                chapter: topChapter,
                questions: []
              };
            }
            chapterGroups[chapterKey].questions.push(q);
          } else {
            unmatchedQuestions.push(q);
          }
        });
        
        // Add unmatched questions if any
        if (unmatchedQuestions.length > 0) {
          chapterGroups['Unmatched Questions'] = {
            chapter: {
              chapter_number: 0,
              chapter_title: 'Unmatched Questions',
              page_start: 'N/A',
              page_end: 'N/A',
              similarity_score: 0
            },
            questions: unmatchedQuestions
          };
        }
        
        const totalQuestions = Object.values(chapterGroups).reduce((sum, data) => sum + data.questions.length, 0);
        
        // Clear old chapter stats
        setChapterStats([]);
        
        setSemanticSearchResults(chapterGroups);
        setMessage({
          type: 'success',
          text: `🎉 Complete! Found ${Object.keys(chapterGroups).length} chapters with ${totalQuestions} questions (${unmatchedQuestions.length} unmatched). Click a chapter below.`
        });
        
        // Save results to database
        await saveSearchResults(chapterGroups);
      } else {
        throw new Error('AI search failed');
      }
    } catch (err) {
      console.error('Error in Index & Match workflow:', err);
      const errorMsg = err.response?.data?.error || err.message;
      
      setMessage({ 
        type: 'error', 
        text: `Failed: ${errorMsg}` 
      });
    } finally {
      setIsSearching(false);
    }
  };

  // Removed unused functions: handleIndexTextbook, handleRunSemanticSearch, handleClearResults
  // Their functionality has been merged into handleIndexAndMatch

  const saveSearchResults = async (chapterGroups) => {
    try {
      console.log('💾 Saving search results to database...');
      console.log('  Paper ID:', selectedPaper.id);
      console.log('  Textbook ID:', selectedTextbook.uploadedId);
      console.log('  Chapters:', Object.keys(chapterGroups).length);
      
      const response = await axios.post('http://localhost:5000/api/save-ai-search-results', {
        paper_id: selectedPaper.id,
        textbook_id: selectedTextbook.uploadedId,
        search_results: chapterGroups
      });
      
      console.log('✓ Search results saved to database:', response.data);
    } catch (error) {
      console.error('❌ Failed to save search results:', error);
      console.error('  Error details:', error.response?.data);
      // Don't show error to user - this is a background operation
    }
  };

  const handleLoadLastMatch = async () => {
    if (!selectedPaper || !selectedTextbook || !selectedTextbook.uploadedId) {
      setMessage({ type: 'warning', text: 'Please select both a question paper and textbook first' });
      return;
    }

    setIsSearching(true);
    setMessage({ type: 'info', text: '📋 Loading last AI search results...' });

    console.log('📋 Loading last match...');
    console.log('  Paper ID:', selectedPaper.id);
    console.log('  Textbook ID:', selectedTextbook.uploadedId);

    try {
      const response = await axios.get(
        `http://localhost:5000/api/get-last-ai-search?paper_id=${selectedPaper.id}&textbook_id=${selectedTextbook.uploadedId}`
      );
      
      console.log('  Response:', response.data);

      if (response.data.success) {
        const { search_results, total_chapters, total_questions, unmatched_count, created_at } = response.data;
        
        // Clear old chapter stats
        setChapterStats([]);
        
        setSemanticSearchResults(search_results);
        
        // Format the date
        const date = new Date(created_at);
        const timeAgo = getTimeAgo(date);
        
        setMessage({
          type: 'success',
          text: `📋 Loaded previous results (${timeAgo}): ${total_chapters} chapters with ${total_questions} questions (${unmatched_count} unmatched)`
        });
      }
    } catch (err) {
      console.error('Error loading last match:', err);
      if (err.response?.status === 404) {
        // Clear any existing results since no match found for this combination
        setSemanticSearchResults(null);
        setChapterStats([]);
        
        setMessage({ 
          type: 'info', 
          text: `No previous results found for "${selectedPaper.title}" with "${selectedTextbook.name}". Please run "Index & Match Questions" first.` 
        });
      } else {
        setMessage({ 
          type: 'error', 
          text: `Failed to load previous results: ${err.response?.data?.error || err.message}` 
        });
      }
    } finally {
      setIsSearching(false);
    }
  };

  const getTimeAgo = (date) => {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)} days ago`;
    return date.toLocaleDateString();
  };

  const handleChapterSelect = (chapterData) => {
    console.log('Selected chapter:', chapterData);
    console.log('Available chapters in semanticSearchResults:', semanticSearchResults ? Object.keys(semanticSearchResults) : 'None');
    
    setSelectedChapter(chapterData);
    
    if (semanticSearchResults && semanticSearchResults[chapterData.name]) {
      // Use semantic search results
      const chapterQuestions = semanticSearchResults[chapterData.name].questions;
      const chapterInfo = semanticSearchResults[chapterData.name].chapter;
      
      console.log('Found chapter questions:', chapterQuestions.length);
      console.log('Chapter info:', chapterInfo);
      
      setQuestions(chapterQuestions);
      setMessage({
        type: 'success',
        text: `Showing ${chapterQuestions.length} questions for: ${chapterData.name} (AI matched)`
      });
    } else {
      console.warn('Chapter not found in semantic search results:', chapterData.name);
      setMessage({
        type: 'info',
        text: 'Run AI Search to find questions for this chapter'
      });
      setQuestions([]);
    }
  };

  const handleSolveQuestion = async (question) => {
    setSolvingQuestion(true);
    try {
      const chapterContext = question.chapters && question.chapters.length > 0 
        ? question.chapters[0].chapter_title 
        : selectedChapter?.name;
      
      const response = await axios.post('http://localhost:5000/api/solve-question', {
        question_text: question.question_text,
        question_type: question.question_type,
        subject: selectedPaper?.subject,
        chapter_context: chapterContext
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
          await axios.post('http://localhost:5000/api/save-solved-question', {
            question_text: question.question_text,
            solution: response.data.solution,
            subject: selectedPaper?.subject,
            source: 'answer_chapterwise',
            paper_id: selectedPaper?.id,
            textbook_id: selectedTextbook?.uploadedId || selectedTextbook?.id,
            chapter_name: chapterContext,
            timestamp: new Date().toISOString()
          });
          console.log('✅ Question saved to Question Bank with subject:', selectedPaper?.subject);
        } catch (saveErr) {
          console.error('Failed to save to Question Bank:', saveErr);
          // Don't show error to user, just log it
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

  const estimateQuestionPageNumber = (questionText, chapterData) => {
    // Estimate specific page range within chapter based on question content
    if (!chapterData || !chapterData.pages) {
      return 'N/A'; // Return default if no page data
    }
    
    const { pages } = chapterData;
    const [startPage, endPage] = pages.split('-').map(p => parseInt(p.trim()));
    const totalPages = endPage - startPage + 1;
    
    // Define sub-topics with their relative position in chapter (0-1)
    const subTopicPositions = {
      // Electricity sub-topics
      'electric current': 0.1,
      'potential difference': 0.2,
      'ohm law': 0.3,
      'resistance': 0.3,
      'series circuit': 0.5,
      'parallel circuit': 0.6,
      'heating effect': 0.7,
      'electric power': 0.8,
      'joule law': 0.9,
      
      // Magnetic Effects
      'magnetic field': 0.1,
      'right hand rule': 0.2,
      'electromagnet': 0.3,
      'solenoid': 0.4,
      'force on conductor': 0.5,
      'electric motor': 0.6,
      'electromagnetic induction': 0.7,
      'generator': 0.8,
      'fleming': 0.8,
      
      // Light - Reflection and Refraction
      'law of reflection': 0.1,
      'plane mirror': 0.15,
      'spherical mirror': 0.2,
      'concave mirror': 0.3,
      'convex mirror': 0.4,
      'mirror formula': 0.45,
      'refraction': 0.5,
      'refractive index': 0.55,
      'snell law': 0.6,
      'lens': 0.65,
      'concave lens': 0.7,
      'convex lens': 0.75,
      'lens formula': 0.8,
      'power of lens': 0.9,
      
      // Quadratic Equations
      'standard form': 0.1,
      'factorization': 0.2,
      'completing square': 0.4,
      'quadratic formula': 0.6,
      'discriminant': 0.7,
      'nature of roots': 0.8,
      'word problem': 0.9,
      
      // Triangles
      'similar triangle': 0.2,
      'basic proportionality': 0.3,
      'criteria for similarity': 0.4,
      'area of similar': 0.5,
      'pythagoras theorem': 0.6,
      'converse of pythagoras': 0.7,
      'triangle inequality': 0.8,
      
      // Coordinate Geometry
      'distance formula': 0.2,
      'section formula': 0.4,
      'midpoint': 0.5,
      'area of triangle': 0.6,
      'collinear': 0.7,
      'slope': 0.8,
      
      // Trigonometry
      'trigonometric ratio': 0.1,
      'sine': 0.2,
      'cosine': 0.3,
      'tangent': 0.4,
      'complementary angle': 0.5,
      'trigonometric identity': 0.6,
      'angle of elevation': 0.7,
      'angle of depression': 0.8,
      'height and distance': 0.9,
      
      // Statistics
      'mean': 0.2,
      'median': 0.4,
      'mode': 0.6,
      'cumulative frequency': 0.7,
      'ogive': 0.8,
      
      // Probability
      'theoretical probability': 0.3,
      'experimental probability': 0.5,
      'sample space': 0.6,
      'mutually exclusive': 0.8,
      
      // Chemistry - Acids, Bases and Salts
      'acid': 0.1,
      'base': 0.2,
      'indicator': 0.3,
      'ph scale': 0.4,
      'neutralization': 0.5,
      'salt': 0.6,
      'water of crystallization': 0.8,
      
      // Biology - Life Processes
      'nutrition': 0.1,
      'autotrophic': 0.15,
      'heterotrophic': 0.2,
      'photosynthesis': 0.25,
      'digestion': 0.3,
      'respiration': 0.5,
      'aerobic': 0.55,
      'anaerobic': 0.6,
      'transportation': 0.7,
      'excretion': 0.85
    };
    
    const lowerText = questionText.toLowerCase();
    let estimatedPosition = 0.5; // Default to middle
    let matchFound = false;
    
    // Find the most specific sub-topic match
    for (const [subTopic, position] of Object.entries(subTopicPositions)) {
      if (lowerText.includes(subTopic)) {
        estimatedPosition = position;
        matchFound = true;
        break; // Use first match (most specific)
      }
    }
    
    // Calculate estimated page range (±2 pages from estimated position)
    const estimatedPage = Math.round(startPage + (totalPages * estimatedPosition));
    const rangeStart = Math.max(startPage, estimatedPage - 2);
    const rangeEnd = Math.min(endPage, estimatedPage + 2);
    
    return matchFound ? `${rangeStart}-${rangeEnd}` : pages;
  };

  const handlePageClick = (pageRange) => {
    const [startPage, endPage] = pageRange.split('-').map(p => parseInt(p.trim()));
    setCurrentPage(startPage);
    setTextbookPageToShow({
      textbook: selectedTextbook,
      chapter: selectedChapter.name,
      pageRange: pageRange,
      startPage: startPage,
      endPage: endPage || startPage
    });
    setShowTextbookModal(true);
  };

  const handleNextPage = () => {
    if (currentPage < textbookPageToShow.endPage) {
      const nextPage = currentPage + 1;
      console.log('Next page:', nextPage);
      setPdfLoading(true);
      setCurrentPage(nextPage);
      setTimeout(() => setPdfLoading(false), 1000);
    }
  };

  const handlePrevPage = () => {
    if (currentPage > textbookPageToShow.startPage) {
      const prevPage = currentPage - 1;
      console.log('Previous page:', prevPage);
      setPdfLoading(true);
      setCurrentPage(prevPage);
      setTimeout(() => setPdfLoading(false), 1000);
    }
  };

  const handleCloseModal = () => {
    setShowTextbookModal(false);
    setTextbookPageToShow(null);
    setCurrentPage(1);
  };

  const filterQuestionsByChapter = (questions, chapter) => {
    // Enhanced keyword matching with scoring system for more focused results
    const chapterKeywords = {
      'Electricity': {
        primary: ['current', 'voltage', 'resistance', 'ohm', 'circuit', 'electric power', 'electrical energy'],
        secondary: ['joule', 'watt', 'ampere', 'volt', 'resistor', 'conductor', 'insulator']
      },
      'Magnetic Effects of Current': {
        primary: ['magnetic field', 'electromagnet', 'solenoid', 'motor', 'generator', 'fleming'],
        secondary: ['magnet', 'electromagnetic induction', 'armature', 'commutator']
      },
      'Light - Reflection and Refraction': {
        primary: ['reflection', 'refraction', 'mirror', 'lens', 'focal length', 'image formation'],
        secondary: ['concave', 'convex', 'ray diagram', 'optical', 'refractive index']
      },
      'Human Eye and Colourful World': {
        primary: ['eye', 'retina', 'cornea', 'spectrum', 'dispersion', 'rainbow', 'prism'],
        secondary: ['vision', 'myopia', 'hypermetropia', 'presbyopia', 'cataract']
      },
      'Sources of Energy': {
        primary: ['renewable energy', 'solar energy', 'wind energy', 'fossil fuel', 'nuclear energy'],
        secondary: ['biogas', 'hydroelectric', 'geothermal', 'tidal energy']
      },
      'Chemical Reactions and Equations': {
        primary: ['chemical reaction', 'chemical equation', 'reactant', 'product', 'balanced equation'],
        secondary: ['oxidation', 'reduction', 'decomposition', 'combination', 'displacement']
      },
      'Acids, Bases and Salts': {
        primary: ['acid', 'base', 'salt', 'ph scale', 'neutralization'],
        secondary: ['alkali', 'indicator', 'litmus', 'acidic', 'basic']
      },
      'Metals and Non-metals': {
        primary: ['metal', 'non-metal', 'metalloid', 'reactivity series', 'corrosion'],
        secondary: ['alloy', 'ore', 'extraction', 'metallic', 'ionic bond']
      },
      'Carbon and its Compounds': {
        primary: ['carbon compound', 'organic compound', 'hydrocarbon', 'functional group'],
        secondary: ['alkane', 'alkene', 'alkyne', 'alcohol', 'carboxylic acid', 'ester']
      },
      'Life Processes': {
        primary: ['nutrition', 'respiration', 'transportation', 'excretion', 'photosynthesis'],
        secondary: ['digestion', 'cellular respiration', 'transpiration', 'kidney']
      },
      'Control and Coordination': {
        primary: ['nervous system', 'hormone', 'endocrine', 'reflex action', 'neuron'],
        secondary: ['brain', 'spinal cord', 'synapse', 'receptor', 'effector']
      },
      'How do Organisms Reproduce': {
        primary: ['reproduction', 'sexual reproduction', 'asexual reproduction', 'fertilization'],
        secondary: ['gamete', 'zygote', 'fission', 'budding', 'vegetative propagation']
      },
      'Heredity and Evolution': {
        primary: ['heredity', 'inheritance', 'gene', 'chromosome', 'evolution', 'natural selection'],
        secondary: ['dna', 'darwin', 'variation', 'speciation', 'fossil']
      },
      'Our Environment': {
        primary: ['ecosystem', 'food chain', 'food web', 'biodegradable', 'ozone layer'],
        secondary: ['environment', 'pollution', 'greenhouse effect', 'decomposer']
      },
      'Real Numbers': {
        primary: ['real number', 'rational number', 'irrational number', 'euclid', 'hcf', 'lcm'],
        secondary: ['prime', 'composite', 'fundamental theorem']
      },
      'Polynomials': {
        primary: ['polynomial', 'degree of polynomial', 'zero of polynomial', 'coefficient'],
        secondary: ['quadratic polynomial', 'cubic polynomial', 'factorization']
      },
      'Pair of Linear Equations in Two Variables': {
        primary: ['linear equation', 'simultaneous equation', 'substitution method', 'elimination method'],
        secondary: ['cross multiplication', 'graphical method', 'consistent', 'inconsistent']
      },
      'Quadratic Equations': {
        primary: ['quadratic equation', 'discriminant', 'roots of equation', 'quadratic formula'],
        secondary: ['x²', 'x^2', 'factorization', 'completing square']
      },
      'Arithmetic Progressions': {
        primary: ['arithmetic progression', 'common difference', 'nth term', 'sum of ap'],
        secondary: ['ap', 'arithmetic sequence', 'series']
      },
      'Triangles': {
        primary: ['similar triangle', 'congruent triangle', 'pythagoras theorem', 'triangle theorem'],
        secondary: ['area of triangle', 'perimeter', 'altitude', 'median']
      },
      'Coordinate Geometry': {
        primary: ['coordinate', 'distance formula', 'section formula', 'midpoint formula'],
        secondary: ['slope', 'x-axis', 'y-axis', 'cartesian plane']
      },
      'Introduction to Trigonometry': {
        primary: ['trigonometry', 'trigonometric ratio', 'sine', 'cosine', 'tangent'],
        secondary: ['sin', 'cos', 'tan', 'angle', 'θ', 'theta']
      },
      'Some Applications of Trigonometry': {
        primary: ['height and distance', 'angle of elevation', 'angle of depression', 'line of sight'],
        secondary: ['trigonometric application', 'tower', 'building height']
      },
      'Circles': {
        primary: ['circle', 'tangent to circle', 'chord', 'secant', 'circle theorem'],
        secondary: ['radius', 'diameter', 'arc', 'segment']
      },
      'Areas Related to Circles': {
        primary: ['area of circle', 'sector', 'segment of circle', 'circumference'],
        secondary: ['π', 'pi', 'circular region', 'annulus']
      },
      'Surface Areas and Volumes': {
        primary: ['surface area', 'volume', 'total surface area', 'curved surface area'],
        secondary: ['cube', 'cuboid', 'cylinder', 'cone', 'sphere', 'hemisphere']
      },
      'Statistics': {
        primary: ['mean', 'median', 'mode', 'frequency distribution', 'cumulative frequency'],
        secondary: ['data', 'class interval', 'grouped data', 'ogive']
      },
      'Probability': {
        primary: ['probability', 'theoretical probability', 'experimental probability', 'random experiment'],
        secondary: ['event', 'outcome', 'sample space', 'certain', 'impossible']
      }
    };

    const chapterData = chapterKeywords[chapter];
    if (!chapterData) {
      // Fallback to simple keyword matching
      const keywords = chapter.toLowerCase().split(' ');
      return questions.filter(q => {
        const questionText = q.question_text.toLowerCase();
        return keywords.some(keyword => questionText.includes(keyword));
      });
    }

    // Score-based filtering for more focused results
    return questions.filter(q => {
      const questionText = q.question_text.toLowerCase();
      let score = 0;

      // Primary keywords are worth 3 points
      chapterData.primary.forEach(keyword => {
        if (questionText.includes(keyword.toLowerCase())) {
          score += 3;
        }
      });

      // Secondary keywords are worth 1 point
      chapterData.secondary.forEach(keyword => {
        if (questionText.includes(keyword.toLowerCase())) {
          score += 1;
        }
      });

      // Require minimum score of 2 for more focused results
      return score >= 2;
    });
  };

  return (
    <div className="chapter-questions">
      <div className="chapter-header">
        <h2>📖 Answer Chapterwise</h2>
        <p>Select a question paper, textbook, and chapter to view related questions</p>
      </div>

      {message.text && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="chapter-content">
        {/* Side by Side Selection Tables */}
        <div className="selection-grid">
          {/* Textbook Selection - Left Side */}
          <div className="selection-section textbook-selection-table">
            <h3>📚 Step 1: Select Textbook</h3>
            {textbooks.length === 0 ? (
              <p className="no-data">No textbooks available. Please upload a textbook first.</p>
            ) : (
              <div className="selection-table-container">
                <table className="selection-table">
                  <thead>
                    <tr>
                      <th style={{width: '50px'}}>Select</th>
                      <th>Textbook Name</th>
                      <th>Subject</th>
                    </tr>
                  </thead>
                  <tbody>
                    {textbooks.map((textbook, index) => (
                      <tr
                        key={index}
                        className={`selection-row ${selectedTextbook?.name === textbook.name ? 'selected' : ''} ${!textbook.uploadedId ? 'disabled' : ''}`}
                        onClick={() => textbook.uploadedId && handleTextbookSelect(textbook)}
                      >
                        <td className="checkbox-cell">
                          <input
                            type="checkbox"
                            checked={selectedTextbook?.name === textbook.name}
                            onChange={() => textbook.uploadedId && handleTextbookSelect(textbook)}
                            disabled={!textbook.uploadedId}
                            onClick={(e) => e.stopPropagation()}
                          />
                        </td>
                        <td className="name-cell">
                          <div className="cell-content">
                            <span className="icon">{textbook.uploadedId ? '📕' : '📘'}</span>
                            <span className="text">{textbook.name}</span>
                          </div>
                        </td>
                        <td className="subject-cell">
                          <span className="subject-badge">{textbook.subject}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Paper Selection - Right Side */}
          <div className="selection-section paper-selection-table">
            <h3>📄 Step 2: Select Question Paper</h3>
            {papers.length === 0 ? (
              <p className="no-data">No question papers uploaded yet</p>
            ) : (
              <div className="selection-table-container">
                <table className="selection-table">
                  <thead>
                    <tr>
                      <th style={{width: '50px'}}>Select</th>
                      <th>Paper Title</th>
                      <th>Subject</th>
                    </tr>
                  </thead>
                  <tbody>
                    {papers.map(paper => (
                      <tr
                        key={paper.id}
                        className={`selection-row ${selectedPaper?.id === paper.id ? 'selected' : ''}`}
                        onClick={() => handlePaperSelect(paper)}
                      >
                        <td className="checkbox-cell">
                          <input
                            type="checkbox"
                            checked={selectedPaper?.id === paper.id}
                            onChange={() => handlePaperSelect(paper)}
                            onClick={(e) => e.stopPropagation()}
                          />
                        </td>
                        <td className="name-cell">
                          <div className="cell-content">
                            <span className="icon">📝</span>
                            <span className="text">{paper.title}</span>
                          </div>
                        </td>
                        <td className="subject-cell">
                          <span className="subject-badge">{paper.subject}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* AI Semantic Search Section */}
        {selectedPaper && selectedTextbook && (
          <div className="semantic-search-section">
            <div className="search-buttons">
              <button 
                className="load-last-btn"
                onClick={handleLoadLastMatch}
                disabled={isSearching || !selectedTextbook.uploadedId}
                title="Load previously saved AI search results (instant)"
              >
                {isSearching ? (
                  <>
                    <span className="spinner-small"></span>
                    Loading...
                  </>
                ) : (
                  <>
                    📋 Show Last Match
                  </>
                )}
              </button>
              <button 
                className="index-and-match-btn"
                onClick={handleIndexAndMatch}
                disabled={isSearching || !selectedTextbook.uploadedId || !selectedPaper}
                title="Index textbook (if needed) and match questions with AI"
              >
                {isSearching ? (
                  <>
                    <span className="spinner-small"></span>
                    Processing...
                  </>
                ) : (
                  <>
                    🚀 Index & Match Questions
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* AI Search Results - Chapter List */}
        {semanticSearchResults && Object.keys(semanticSearchResults).length > 0 && (
          <div className="chapter-table-section ai-results">
            <h3>🤖 AI Search Results - Chapters with Questions</h3>
            <div className="chapter-table-container">
              <table className="chapter-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Chapter Name</th>
                    <th>Pages</th>
                    <th>Questions</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(semanticSearchResults).map(([chapterName, data], index) => {
                    const avgConfidence = data.questions.reduce((sum, q) => {
                      return sum + (q.chapters && q.chapters[0] ? q.chapters[0].similarity_score : 0);
                    }, 0) / data.questions.length;
                    
                    const isUnmatched = chapterName === 'Unmatched Questions';
                    
                    return (
                    <tr 
                      key={index}
                      className={`${selectedChapter?.name === chapterName ? 'selected-row' : ''} ${isUnmatched ? 'unmatched-row' : ''}`}
                    >
                      <td className="chapter-num">
                        {isUnmatched ? '⚠️' : (data.chapter.chapter_number || (index + 1))}
                      </td>
                      <td className="chapter-name-cell">
                        <strong>{chapterName}</strong>
                        {avgConfidence > 0 && !isUnmatched && (
                          <div className="confidence-badge" title={`Average AI confidence: ${avgConfidence.toFixed(1)}%`}>
                            🎯 {avgConfidence.toFixed(0)}%
                          </div>
                        )}
                        {isUnmatched && (
                          <div className="unmatched-badge" title="Questions that could not be matched to any chapter">
                            ⚠️ Needs Review
                          </div>
                        )}
                      </td>
                      <td className="pages-cell">
                        {isUnmatched ? 'N/A' : `${data.chapter.page_start}-${data.chapter.page_end}`}
                      </td>
                      <td className="count-cell">
                        <span className={`question-count ${isUnmatched ? 'unmatched-count' : 'has-questions'}`}>
                          {data.questions.length}
                        </span>
                      </td>
                      <td className="action-cell">
                        <button
                          className={`view-btn ${isUnmatched ? 'unmatched-btn' : ''}`}
                          onClick={() => handleChapterSelect({ name: chapterName })}
                        >
                          View Questions
                        </button>
                      </td>
                    </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            <div className="table-summary">
              <p>
                <strong>Total Chapters:</strong> {Object.keys(semanticSearchResults).length} | 
                <strong> Total Questions:</strong> {Object.values(semanticSearchResults).reduce((sum, data) => sum + data.questions.length, 0)}
              </p>
            </div>
          </div>
        )}

        {/* Questions Display */}
        {selectedChapter && (
          <div className="questions-display">
            <div className="questions-header-info">
              <h3>❓ Questions from: {selectedChapter.name}</h3>
              <div className="chapter-meta">
                <span className="meta-item">📖 <strong>Textbook:</strong> {selectedTextbook.name}</span>
                <span className="meta-item">📄 <strong>Pages:</strong> {selectedChapter.pages}</span>
                <span className="meta-item">📝 <strong>Paper:</strong> {selectedPaper.title}</span>
              </div>
            </div>
            
            {loading ? (
              <div className="loading">
                <div className="spinner"></div>
                <p>Loading questions...</p>
              </div>
            ) : questions.length === 0 ? (
              <div className="no-questions">
                <p>No questions found for this chapter</p>
                <p className="hint">Try selecting a different chapter</p>
              </div>
            ) : (
              <div className="questions-list">
                {questions.map((q, index) => {
                  // Use AI chapter data if available, otherwise use selected chapter
                  let pageInfo = 'N/A';
                  if (q.chapters && q.chapters.length > 0) {
                    // AI search result - use first matched chapter
                    const aiChapter = q.chapters[0];
                    pageInfo = `${aiChapter.page_start}-${aiChapter.page_end}`;
                  } else if (selectedChapter && selectedChapter.pages) {
                    // Regular chapter selection - estimate pages
                    pageInfo = estimateQuestionPageNumber(q.question_text, selectedChapter);
                  }
                  
                  return (
                  <div key={q.id} className="question-item">
                    <div className="question-header">
                      <span className="question-number">Q{q.question_number}</span>
                      <span 
                        className="chapter-page-badge clickable"
                        onClick={() => handlePageClick(pageInfo)}
                        title="Click to view textbook pages"
                      >
                        📖 Pages: {pageInfo}
                      </span>
                      {q.question_type && (
                        <span className={`question-type ${q.question_type}`}>
                          {q.question_type.toUpperCase()}
                        </span>
                      )}
                      {q.marks && (
                        <span className="question-marks">{q.marks} marks</span>
                      )}
                      {q.has_math && (
                        <span className="math-badge">📐 Math</span>
                      )}
                      {(() => {
                        // Always show debug info for has_diagram
                        if (q.has_diagram) {
                          console.log('Question has diagram:', {
                            questionNumber: q.question_number,
                            has_diagram: q.has_diagram,
                            diagram_files: q.diagram_files,
                            diagram_files_type: typeof q.diagram_files
                          });
                        }
                        
                        if (!q.has_diagram) return null;
                        
                        // Parse diagram_files if it's a string
                        let diagramFiles = q.diagram_files;
                        if (typeof diagramFiles === 'string') {
                          try {
                            diagramFiles = JSON.parse(diagramFiles);
                          } catch (e) {
                            console.error('Failed to parse diagram_files:', e);
                            diagramFiles = [];
                          }
                        }
                        
                        // Ensure it's an array
                        if (!Array.isArray(diagramFiles)) {
                          diagramFiles = diagramFiles ? [diagramFiles] : [];
                        }
                        
                        console.log('Processed diagram files:', diagramFiles);
                        
                        if (diagramFiles && diagramFiles.length > 0) {
                          console.log('Rendering CLICKABLE diagram badge');
                          return (
                            <button 
                              type="button"
                              className="diagram-badge clickable"
                              onClick={(e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                console.log('🎯 DIAGRAM BUTTON CLICKED!', diagramFiles);
                                setSelectedDiagram({
                                  questionNumber: q.question_number,
                                  diagrams: diagramFiles
                                });
                              }}
                              title="Click to view diagram"
                              style={{
                                cursor: 'pointer',
                                pointerEvents: 'auto'
                              }}
                            >
                              📊 Diagram
                            </button>
                          );
                        } else {
                          console.log('Rendering STATIC diagram badge (no files)');
                          return <span className="diagram-badge">📊 Diagram</span>;
                        }
                      })()}
                      {(() => {
                        // Check if question has chapter match reasoning
                        const hasChapterReasoning = q.chapters && q.chapters.length > 0 && q.chapters[0].llm_reasoning;
                        
                        if (hasChapterReasoning) {
                          return (
                            <button 
                              className="reasoning-btn"
                              onClick={() => setSelectedReasoning({
                                questionNumber: q.question_number,
                                reasoning: q.chapters[0].llm_reasoning,
                                chapterTitle: q.chapters[0].chapter_title,
                                confidence: q.chapters[0].similarity_score,
                                pageRange: `${q.chapters[0].page_start}-${q.chapters[0].page_end}`
                              })}
                              title="View AI chapter matching reasoning"
                            >
                              🧠 Why This Chapter?
                            </button>
                          );
                        }
                        
                        // Fallback: show parsed data if available
                        let parsedData = q.parsed_data;
                        if (typeof parsedData === 'string') {
                          try {
                            parsedData = JSON.parse(parsedData);
                          } catch (e) {
                            parsedData = {};
                          }
                        }
                        return parsedData && Object.keys(parsedData).length > 0 && (
                          <button 
                            className="reasoning-btn"
                            onClick={() => setSelectedReasoning({
                              questionNumber: q.question_number,
                              reasoning: 'No chapter matching reasoning available',
                              llmResponse: JSON.stringify(parsedData, null, 2)
                            })}
                            title="View AI parsed data"
                          >
                            🧠 AI Data
                          </button>
                        );
                      })()}
                      <button 
                        className="solve-btn"
                        onClick={() => handleSolveQuestion(q)}
                        disabled={solvingQuestion}
                        title="Get detailed step-by-step solution"
                      >
                        {solvingQuestion ? '⏳ Solving...' : '✨ Solve Question'}
                      </button>
                    </div>
                    <div className="question-text">
                      {q.question_text}
                    </div>
                    {(() => {
                      // Parse sub_parts if it's a string
                      let subParts = q.sub_parts;
                      if (typeof subParts === 'string') {
                        try {
                          subParts = JSON.parse(subParts);
                        } catch (e) {
                          subParts = [];
                        }
                      }
                      return subParts && Array.isArray(subParts) && subParts.length > 0 && (
                        <div className="sub-parts">
                          <strong>Sub-parts:</strong> {subParts.join(', ')}
                        </div>
                      );
                    })()}
                  </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Textbook Page Modal */}
      {showTextbookModal && textbookPageToShow && (
        <div className="textbook-modal-overlay" onClick={handleCloseModal}>
          <div className="textbook-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="textbook-modal-header">
              <div className="modal-title-section">
                <h2>📖 {textbookPageToShow.textbook.name}</h2>
                <p className="modal-subtitle">
                  Chapter: {textbookPageToShow.chapter} | Pages: {textbookPageToShow.pageRange}
                </p>
              </div>
              <button 
                className="modal-close-btn"
                onClick={handleCloseModal}
              >
                ✕
              </button>
            </div>
            
            <div className="textbook-modal-body">
              <div className="textbook-viewer">
                <div className="page-info">
                  <span className="current-page-indicator">
                    📄 Page {currentPage} of {textbookPageToShow.pageRange}
                  </span>
                </div>
                
                {/* PDF Viewer - Using uploaded textbook */}
                {textbookPageToShow.textbook.uploadedFile ? (
                  <div className="pdf-embed-container">
                    {pdfLoading && (
                      <div className="pdf-loading-overlay">
                        <div className="spinner"></div>
                        <p>Loading page {currentPage}...</p>
                      </div>
                    )}
                    <iframe
                      key={`pdf-${currentPage}`}
                      src={`http://localhost:5000/api/textbook-pdf/${textbookPageToShow.textbook.uploadedId}#page=${currentPage}&zoom=page-fit`}
                      title={`Textbook Page ${currentPage}`}
                      className="textbook-pdf-iframe"
                      frameBorder="0"
                      allow="fullscreen"
                      onLoad={() => setPdfLoading(false)}
                    />
                  </div>
                ) : (
                  <div className="no-textbook-message">
                    <div className="external-icon">📚</div>
                    <h3>No Textbook Uploaded</h3>
                    <p className="viewer-description">
                      Please upload a textbook file for {textbookPageToShow.textbook.name} to view pages.
                    </p>
                    <div className="link-info">
                      <p><strong>Textbook:</strong> {textbookPageToShow.textbook.name}</p>
                      <p><strong>Chapter:</strong> {textbookPageToShow.chapter}</p>
                      <p><strong>Pages:</strong> {textbookPageToShow.pageRange}</p>
                      <p className="upload-hint">Go to "Upload Papers" menu to upload textbook PDFs</p>
                    </div>
                  </div>
                )}

                {/* Page Navigation */}
                <div className="page-navigation">
                  <button 
                    className="nav-btn"
                    onClick={handlePrevPage}
                    disabled={currentPage <= textbookPageToShow.startPage}
                  >
                    ← Previous
                  </button>
                  <span className="page-display">
                    Page {currentPage}
                  </span>
                  <button 
                    className="nav-btn"
                    onClick={handleNextPage}
                    disabled={currentPage >= textbookPageToShow.endPage}
                  >
                    Next →
                  </button>
                </div>
              </div>
            </div>
            
            <div className="textbook-modal-footer">
              <div className="footer-info">
                <span className="page-count">
                  {textbookPageToShow.endPage - textbookPageToShow.startPage + 1} pages in range
                </span>
              </div>
              <button 
                className="close-modal-btn"
                onClick={handleCloseModal}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reasoning Modal */}
      {selectedReasoning && (
        <div className="reasoning-modal" onClick={() => setSelectedReasoning(null)}>
          <div className="reasoning-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="reasoning-modal-header">
              <h3>🧠 Chapter Matching Analysis - Q{selectedReasoning.questionNumber}</h3>
              <button className="close-reasoning-btn" onClick={() => setSelectedReasoning(null)}>✕</button>
            </div>
            
            <div className="reasoning-modal-body">
              {selectedReasoning.chapterTitle && (
                <div className="chapter-match-info">
                  <div className="match-detail">
                    <span className="match-label">📚 Matched Chapter:</span>
                    <span className="match-value">{selectedReasoning.chapterTitle}</span>
                  </div>
                  <div className="match-detail">
                    <span className="match-label">📄 Pages:</span>
                    <span className="match-value">{selectedReasoning.pageRange}</span>
                  </div>
                  {selectedReasoning.confidence && (
                    <div className="match-detail">
                      <span className="match-label">🎯 Confidence:</span>
                      <span className="match-value">{selectedReasoning.confidence}%</span>
                    </div>
                  )}
                </div>
              )}
              
              <div className="reasoning-section">
                <h4>💭 AI Reasoning:</h4>
                <div className="reasoning-content">
                  {selectedReasoning.reasoning}
                </div>
              </div>
              
              {selectedReasoning.llmResponse && (
                <div className="llm-response-section">
                  <h4>🤖 Technical Details (JSON):</h4>
                  <div className="llm-response-content">
                    <pre>{selectedReasoning.llmResponse}</pre>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

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
                {(() => {
                  const lines = selectedSolution.solution.split('\n');
                  let inDiagram = false;
                  let diagramLines = [];
                  let lastWasEmpty = false;
                  let lastWasSection = false;
                  let currentSection = null;
                  const elements = [];
                  
                  lines.forEach((line, idx) => {
                    // Detect ASCII art diagram patterns (box drawing characters)
                    /* eslint-disable no-useless-escape */
                    const isAsciiArt = line.match(/^[\s]*[+\-|/\\<>]+[\s+\-|/\\<>]*$/) || 
                                      line.match(/^[\s]*[+\-|]{3,}/) ||
                                      line.match(/[+\-]{5,}/) ||
                                      (line.includes('|') && line.includes('+'));
                    /* eslint-enable no-useless-escape */
                    
                    // Detect diagram start/end
                    if (line.match(/^\*\*Diagram/i) || line.includes('```') || (!inDiagram && isAsciiArt)) {
                      if (!inDiagram) {
                        // Starting a diagram
                        inDiagram = true;
                        if (isAsciiArt) {
                          diagramLines.push(line);
                        }
                      } else {
                        // Ending a diagram
                        if (line.includes('```') || line.match(/^\*\*Diagram/i)) {
                          inDiagram = false;
                        } else if (isAsciiArt) {
                          diagramLines.push(line);
                        } else {
                          // End of ASCII art
                          inDiagram = false;
                        }
                        
                        if (!inDiagram && diagramLines.length > 0) {
                          const diagram = diagramLines.join('\n');
                          diagramLines = [];
                          elements.push(<pre key={idx} className="solution-diagram">{diagram}</pre>);
                          lastWasEmpty = false;
                          lastWasSection = true;
                        }
                      }
                      return;
                    }
                    
                    // Collect diagram lines
                    if (inDiagram) {
                      diagramLines.push(line);
                      return;
                    }
                    
                    // Highlight section headers (bold text with **)
                    if (line.match(/^\*\*.*\*\*:?$/)) {
                      const sectionName = line.replace(/\*\*/g, '').replace(/:/g, '').trim().toLowerCase();
                      currentSection = sectionName;
                      elements.push(<h4 key={idx} className="solution-section-header">{line.replace(/\*\*/g, '').replace(/:/g, '')}</h4>);
                      lastWasEmpty = false;
                      lastWasSection = true;
                      return;
                    }
                    
                    // Highlight final answer
                    if (line.match(/FINAL ANSWER:/i)) {
                      elements.push(
                        <div key={idx} className="final-answer-box">
                          <div className="final-answer-icon">🎯</div>
                          <div className="final-answer-text" dangerouslySetInnerHTML={{
                            __html: line.replace(/FINAL ANSWER:/i, '').trim()
                          }}></div>
                        </div>
                      );
                      lastWasEmpty = false;
                      lastWasSection = true;
                      return;
                    }
                    
                    // Highlight step numbers
                    if (line.match(/^(Step \d+:|^\d+\.)/)) {
                      elements.push(
                        <div key={idx} className="solution-step" dangerouslySetInnerHTML={{
                          __html: line
                        }}></div>
                      );
                      lastWasEmpty = false;
                      lastWasSection = false;
                      return;
                    }
                    
                    // Handle empty lines - only add one between sections
                    if (!line.trim()) {
                      // Don't add spacers within compact sections (given, find, formula)
                      const compactSections = ['given', 'find', 'formula', 'concept', 'formula/concept'];
                      const isCompactSection = compactSections.some(s => currentSection && currentSection.includes(s));
                      
                      if (!lastWasEmpty && lastWasSection && !isCompactSection) {
                        elements.push(<div key={idx} className="section-spacer"></div>);
                        lastWasEmpty = true;
                      }
                      return;
                    }
                    
                    // Format mathematical/scientific expressions
                    const formatExpression = (text) => {
                      return text
                        // Preserve existing HTML entities
                        .replace(/&/g, '&amp;')
                        .replace(/</g, '&lt;')
                        .replace(/>/g, '&gt;')
                        // Keep special characters as-is (they're already Unicode)
                        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>') // Bold
                        .replace(/\*(.+?)\*/g, '<em>$1</em>'); // Italic
                    };
                    
                    // Regular text with formatting
                    const compactSections = ['given', 'find', 'formula', 'concept', 'formula/concept'];
                    const isCompactSection = compactSections.some(s => currentSection && currentSection.includes(s));
                    const textClass = isCompactSection ? 'solution-text compact' : 'solution-text';
                    
                    elements.push(
                      <p key={idx} className={textClass} dangerouslySetInnerHTML={{
                        __html: formatExpression(line)
                      }}></p>
                    );
                    lastWasEmpty = false;
                    lastWasSection = false;
                  });
                  
                  return elements;
                })()}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Diagram Modal */}
      {selectedDiagram && (
        <div className="diagram-modal-overlay" onClick={() => setSelectedDiagram(null)}>
          <div className="diagram-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="diagram-modal-header">
              <h3>📊 Diagram - Q{selectedDiagram.questionNumber}</h3>
              <button className="close-diagram-btn" onClick={() => setSelectedDiagram(null)}>✕</button>
            </div>
            <div className="diagram-modal-body">
              {selectedDiagram.diagrams.map((diagram, idx) => (
                <div key={idx} className="diagram-container">
                  <img 
                    src={`http://localhost:5000${diagram}`} 
                    alt={`Diagram ${idx + 1}`}
                    className="diagram-image"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'block';
                    }}
                  />
                  <div className="diagram-error" style={{display: 'none'}}>
                    ⚠️ Failed to load diagram
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChapterQuestions;
