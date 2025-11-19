# Frontend Restructure Guide: Modal to Main Page

## Objective
Convert the single question solving modal into the main landing page after login, with all current modal features (paste image, image area, text input tabs).

---

## Current Architecture (Assumed)

```
Login → Dashboard → [Question Modal Button] → Modal with tabs
                                              ├─ Paste Image
                                              ├─ Image Area
                                              └─ Text Input
```

## New Architecture

```
Login → Question Solver Page (Main) → Tabs directly visible
                                      ├─ Paste Image
                                      ├─ Image Area
                                      └─ Text Input
        
        [Navigation Menu]
        ├─ Solve Question (default/home)
        ├─ Question Banks
        ├─ Textbooks
        ├─ Papers
        └─ Profile
```

---

## Implementation Steps

### Step 1: Create New Main Question Solver Page

**File: `src/pages/QuestionSolver.jsx` or `question-solver.html`**

```jsx
import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import PasteImageTab from '@/components/question-solver/PasteImageTab';
import ImageAreaTab from '@/components/question-solver/ImageAreaTab';
import TextInputTab from '@/components/question-solver/TextInputTab';
import SolutionDisplay from '@/components/question-solver/SolutionDisplay';

export default function QuestionSolver() {
  const [solution, setSolution] = useState(null);
  const [loading, setLoading] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">
              AI Question Solver
            </h1>
            <nav className="flex space-x-4">
              <a href="/question-banks" className="text-gray-600 hover:text-gray-900">
                Question Banks
              </a>
              <a href="/textbooks" className="text-gray-600 hover:text-gray-900">
                Textbooks
              </a>
              <a href="/papers" className="text-gray-600 hover:text-gray-900">
                Papers
              </a>
              <a href="/profile" className="text-gray-600 hover:text-gray-900">
                Profile
              </a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column: Input Section */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">
              Submit Your Question
            </h2>
            
            <Tabs defaultValue="paste-image" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="paste-image">Paste Image</TabsTrigger>
                <TabsTrigger value="image-area">Image Area</TabsTrigger>
                <TabsTrigger value="text-input">Text Input</TabsTrigger>
              </TabsList>

              <TabsContent value="paste-image">
                <PasteImageTab 
                  onSubmit={handleSubmit}
                  loading={loading}
                />
              </TabsContent>

              <TabsContent value="image-area">
                <ImageAreaTab 
                  onSubmit={handleSubmit}
                  loading={loading}
                />
              </TabsContent>

              <TabsContent value="text-input">
                <TextInputTab 
                  onSubmit={handleSubmit}
                  loading={loading}
                />
              </TabsContent>
            </Tabs>
          </div>

          {/* Right Column: Solution Display */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">
              Solution
            </h2>
            
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              </div>
            ) : solution ? (
              <SolutionDisplay solution={solution} />
            ) : (
              <div className="flex items-center justify-center h-64 text-gray-400">
                <p>Submit a question to see the solution here</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );

  async function handleSubmit(data) {
    setLoading(true);
    try {
      const response = await fetch('/api/solve-question', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(data)
      });
      
      const result = await response.json();
      setSolution(result);
    } catch (error) {
      console.error('Error solving question:', error);
    } finally {
      setLoading(false);
    }
  }
}
```

---

### Step 2: Create Component Files

#### **PasteImageTab.jsx**

```jsx
import React, { useState, useEffect } from 'react';
import { Upload, Clipboard } from 'lucide-react';

export default function PasteImageTab({ onSubmit, loading }) {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);

  useEffect(() => {
    // Listen for paste events
    const handlePaste = (e) => {
      const items = e.clipboardData?.items;
      if (!items) return;

      for (let item of items) {
        if (item.type.indexOf('image') !== -1) {
          const file = item.getAsFile();
          handleImageFile(file);
        }
      }
    };

    document.addEventListener('paste', handlePaste);
    return () => document.removeEventListener('paste', handlePaste);
  }, []);

  const handleImageFile = (file) => {
    setImage(file);
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result);
    };
    reader.readAsDataURL(file);
  };

  const handleSubmit = async () => {
    if (!image) return;

    const formData = new FormData();
    formData.append('image', image);

    // Convert to base64 or send as FormData
    const reader = new FileReader();
    reader.onloadend = () => {
      onSubmit({
        image: reader.result,
        type: 'image'
      });
    };
    reader.readAsDataURL(image);
  };

  return (
    <div className="space-y-4 mt-4">
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
        {preview ? (
          <div className="space-y-4">
            <img 
              src={preview} 
              alt="Pasted" 
              className="max-h-64 mx-auto rounded"
            />
            <button
              onClick={() => {
                setImage(null);
                setPreview(null);
              }}
              className="text-sm text-red-600 hover:text-red-700"
            >
              Clear Image
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            <Clipboard className="mx-auto h-12 w-12 text-gray-400" />
            <p className="text-gray-600">
              Press <kbd className="px-2 py-1 bg-gray-100 rounded">Ctrl+V</kbd> to paste an image
            </p>
            <p className="text-sm text-gray-500">
              Or use the Image Area tab to select from screen
            </p>
          </div>
        )}
      </div>

      <button
        onClick={handleSubmit}
        disabled={!image || loading}
        className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
      >
        {loading ? 'Solving...' : 'Solve Question'}
      </button>
    </div>
  );
}
```

#### **ImageAreaTab.jsx**

```jsx
import React, { useState } from 'react';
import { Camera, Upload } from 'lucide-react';

export default function ImageAreaTab({ onSubmit, loading }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedFile(file);
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result);
    };
    reader.readAsDataURL(file);
  };

  const handleSubmit = () => {
    if (!selectedFile) return;

    const reader = new FileReader();
    reader.onloadend = () => {
      onSubmit({
        image: reader.result,
        type: 'image'
      });
    };
    reader.readAsDataURL(selectedFile);
  };

  return (
    <div className="space-y-4 mt-4">
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8">
        {preview ? (
          <div className="space-y-4">
            <img 
              src={preview} 
              alt="Selected" 
              className="max-h-64 mx-auto rounded"
            />
            <div className="text-center">
              <button
                onClick={() => {
                  setSelectedFile(null);
                  setPreview(null);
                }}
                className="text-sm text-red-600 hover:text-red-700"
              >
                Clear Image
              </button>
            </div>
          </div>
        ) : (
          <label className="cursor-pointer block">
            <input
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />
            <div className="text-center space-y-2">
              <Upload className="mx-auto h-12 w-12 text-gray-400" />
              <p className="text-gray-600">
                Click to upload an image
              </p>
              <p className="text-sm text-gray-500">
                PNG, JPG, GIF up to 10MB
              </p>
            </div>
          </label>
        )}
      </div>

      <button
        onClick={handleSubmit}
        disabled={!selectedFile || loading}
        className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
      >
        {loading ? 'Solving...' : 'Solve Question'}
      </button>
    </div>
  );
}
```

#### **TextInputTab.jsx**

```jsx
import React, { useState } from 'react';
import { Type } from 'lucide-react';

export default function TextInputTab({ onSubmit, loading }) {
  const [text, setText] = useState('');
  const [subject, setSubject] = useState('');

  const handleSubmit = () => {
    if (!text.trim()) return;

    onSubmit({
      question_text: text,
      subject: subject,
      type: 'text'
    });
  };

  return (
    <div className="space-y-4 mt-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Subject (Optional)
        </label>
        <select
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">Select subject...</option>
          <option value="Mathematics">Mathematics</option>
          <option value="Physics">Physics</option>
          <option value="Chemistry">Chemistry</option>
          <option value="Biology">Biology</option>
          <option value="English">English</option>
          <option value="History">History</option>
          <option value="Geography">Geography</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Question Text
        </label>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type or paste your question here..."
          rows={8}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
        />
        <p className="mt-1 text-sm text-gray-500">
          {text.length} characters
        </p>
      </div>

      <button
        onClick={handleSubmit}
        disabled={!text.trim() || loading}
        className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
      >
        {loading ? 'Solving...' : 'Solve Question'}
      </button>
    </div>
  );
}
```

#### **SolutionDisplay.jsx**

```jsx
import React from 'react';
import { CheckCircle, Clock, Lightbulb } from 'lucide-react';

export default function SolutionDisplay({ solution }) {
  if (!solution) return null;

  return (
    <div className="space-y-6">
      {/* Metadata */}
      <div className="flex items-center justify-between text-sm text-gray-600">
        <div className="flex items-center space-x-2">
          <Clock className="h-4 w-4" />
          <span>
            Solved in {solution.processing_time_seconds?.toFixed(2)}s
          </span>
        </div>
        <div className="flex items-center space-x-2">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <span className="text-green-600">
            {solution.solver_type === 'intelligent' ? 'AI Solver' : 'Basic Solver'}
          </span>
        </div>
      </div>

      {/* Solution Content */}
      <div className="prose prose-blue max-w-none">
        <div 
          className="whitespace-pre-wrap text-gray-800"
          dangerouslySetInnerHTML={{ __html: formatSolution(solution.solution) }}
        />
      </div>

      {/* Extracted Expressions (if intelligent solver) */}
      {solution.extracted_expressions && solution.extracted_expressions.length > 0 && (
        <div className="border-t pt-4">
          <h3 className="text-lg font-semibold mb-3 flex items-center">
            <Lightbulb className="h-5 w-5 mr-2 text-yellow-500" />
            Key Expressions
          </h3>
          <div className="space-y-2">
            {solution.extracted_expressions.map((expr, idx) => (
              <div key={idx} className="bg-gray-50 p-3 rounded">
                <p className="font-mono text-sm">{expr.expression}</p>
                {expr.type && (
                  <p className="text-xs text-gray-600 mt-1">
                    Type: {expr.type}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex space-x-3 pt-4 border-t">
        <button className="flex-1 bg-gray-100 text-gray-700 py-2 rounded-lg hover:bg-gray-200">
          Save Solution
        </button>
        <button className="flex-1 bg-gray-100 text-gray-700 py-2 rounded-lg hover:bg-gray-200">
          Share
        </button>
        <button className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">
          New Question
        </button>
      </div>
    </div>
  );
}

function formatSolution(text) {
  if (!text) return '';
  
  // Convert markdown-style headers
  text = text.replace(/^## (.+)$/gm, '<h3 class="text-lg font-semibold mt-4 mb-2">$1</h3>');
  text = text.replace(/^### (.+)$/gm, '<h4 class="text-base font-semibold mt-3 mb-2">$1</h4>');
  
  // Convert bold
  text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  
  // Convert line breaks
  text = text.replace(/\n\n/g, '</p><p class="mb-4">');
  
  return '<p class="mb-4">' + text + '</p>';
}
```

---

### Step 3: Update Routing

**File: `src/App.jsx` or routing configuration**

```jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import QuestionSolver from './pages/QuestionSolver';
import QuestionBanks from './pages/QuestionBanks';
import Textbooks from './pages/Textbooks';
import Papers from './pages/Papers';
import Profile from './pages/Profile';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        {/* Protected Routes */}
        <Route element={<ProtectedRoute />}>
          {/* Default route after login */}
          <Route path="/" element={<QuestionSolver />} />
          <Route path="/solve" element={<QuestionSolver />} />
          <Route path="/question-banks" element={<QuestionBanks />} />
          <Route path="/textbooks" element={<Textbooks />} />
          <Route path="/papers" element={<Papers />} />
          <Route path="/profile" element={<Profile />} />
        </Route>

        {/* Redirect unknown routes */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

---

### Step 4: Update Login Redirect

**File: `src/pages/Login.jsx`**

```jsx
// After successful login
const handleLogin = async (credentials) => {
  try {
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    });
    
    const data = await response.json();
    
    if (data.success) {
      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));
      
      // Redirect to question solver (main page)
      navigate('/');  // Changed from '/dashboard'
    }
  } catch (error) {
    console.error('Login error:', error);
  }
};
```

---

### Step 5: Add Navigation Component

**File: `src/components/Navigation.jsx`**

```jsx
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, BookOpen, FileText, Library, User, LogOut } from 'lucide-react';

export default function Navigation() {
  const location = useLocation();
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  const navItems = [
    { path: '/', label: 'Solve Question', icon: Home },
    { path: '/question-banks', label: 'Question Banks', icon: Library },
    { path: '/textbooks', label: 'Textbooks', icon: BookOpen },
    { path: '/papers', label: 'Papers', icon: FileText },
    { path: '/profile', label: 'Profile', icon: User },
  ];

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  };

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <h1 className="text-xl font-bold text-blue-600">
              QADAM AI
            </h1>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">
              {user.username || user.email}
            </span>
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 text-gray-600 hover:text-red-600"
            >
              <LogOut className="h-4 w-4" />
              <span className="text-sm">Logout</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
```

---

### Step 6: Update CSS/Styling

**File: `src/styles/globals.css` or `tailwind.config.js`**

```css
/* Add custom styles for the question solver page */

.question-solver-container {
  min-height: calc(100vh - 64px); /* Full height minus header */
}

.solution-content {
  max-height: calc(100vh - 300px);
  overflow-y: auto;
}

/* Custom scrollbar */
.solution-content::-webkit-scrollbar {
  width: 8px;
}

.solution-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.solution-content::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.solution-content::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Responsive adjustments */
@media (max-width: 1024px) {
  .question-solver-container {
    grid-template-columns: 1fr;
  }
}
```

---

## Migration Checklist

- [ ] Create new `QuestionSolver.jsx` main page
- [ ] Create component files:
  - [ ] `PasteImageTab.jsx`
  - [ ] `ImageAreaTab.jsx`
  - [ ] `TextInputTab.jsx`
  - [ ] `SolutionDisplay.jsx`
- [ ] Update routing to make `/` point to QuestionSolver
- [ ] Update login redirect to `/` instead of `/dashboard`
- [ ] Add navigation component
- [ ] Update CSS/styling
- [ ] Remove old modal component
- [ ] Test all three input methods
- [ ] Test solution display
- [ ] Test navigation between pages
- [ ] Test responsive design (mobile/tablet)

---

## Testing Steps

1. **Login Flow**
   ```
   Login → Should land on Question Solver page
   ```

2. **Paste Image Tab**
   - Press Ctrl+V with image in clipboard
   - Verify image preview appears
   - Click "Solve Question"
   - Verify solution displays

3. **Image Area Tab**
   - Click to upload image
   - Select image file
   - Verify preview
   - Submit and verify solution

4. **Text Input Tab**
   - Select subject
   - Type question
   - Submit and verify solution

5. **Navigation**
   - Click each nav item
   - Verify correct page loads
   - Return to Solve Question
   - Verify state is preserved

6. **Responsive Design**
   - Test on mobile (< 768px)
   - Test on tablet (768px - 1024px)
   - Test on desktop (> 1024px)

---

## Deployment Notes

### For Azure Static Web Apps:

1. **Build the updated frontend:**
   ```bash
   npm run build
   ```

2. **Deploy to Azure:**
   ```bash
   az staticwebapp deploy \
     --name qadam-frontend \
     --resource-group qadam-rg \
     --source ./build
   ```

3. **Update environment variables if needed:**
   - API endpoint URLs
   - Authentication settings

### For Local Development:

```bash
npm install
npm run dev
```

---

## Benefits of New Layout

✅ **Immediate Access** - Users can start solving questions right after login  
✅ **Better UX** - No need to open modal, everything is visible  
✅ **More Space** - Full page layout allows better organization  
✅ **Side-by-Side** - Input and solution visible simultaneously  
✅ **Cleaner Navigation** - Top nav bar for easy access to other features  
✅ **Mobile Friendly** - Responsive design works on all devices  

---

## Summary

This restructure converts the modal-based question solver into a full-page main interface that users see immediately after login. All existing features (paste image, image area, text input) are preserved as tabs, and the solution displays alongside the input for better visibility.
