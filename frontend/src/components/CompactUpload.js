import React, { useState } from 'react';
import axios from 'axios';
import './CompactUpload.css';

const CompactUpload = ({ type, user, onSuccess }) => {
  const [formData, setFormData] = useState({
    title: '',
    subject: '',
    author: '',
    file: null
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    setFormData(prev => ({ ...prev, file: e.target.files[0] }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.title || !formData.subject || !formData.file) {
      setMessage({ type: 'error', text: 'Please fill all required fields' });
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    const data = new FormData();
    data.append('file', formData.file);
    data.append('title', formData.title);
    data.append('subject', formData.subject);
    if (formData.author) data.append('author', formData.author);
    data.append('user_id', user.id);

    try {
      const endpoint = type === 'textbook' ? '/api/upload-textbook' : '/api/upload-paper';
      const response = await axios.post(`http://localhost:5000${endpoint}`, data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      if (response.data.success) {
        setMessage({ type: 'success', text: `${type === 'textbook' ? 'Textbook' : 'Paper'} uploaded successfully!` });
        setFormData({ title: '', subject: '', author: '', file: null });
        if (onSuccess) onSuccess();
      }
    } catch (err) {
      setMessage({ 
        type: 'error', 
        text: err.response?.data?.error || 'Upload failed' 
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="compact-upload-form">
      <div className="compact-form-grid">
        <input
          type="text"
          name="title"
          value={formData.title}
          onChange={handleChange}
          placeholder={`${type === 'textbook' ? 'Textbook' : 'Paper'} Title *`}
          required
        />
        
        <select
          name="subject"
          value={formData.subject}
          onChange={handleChange}
          required
        >
          <option value="">Subject *</option>
          <option value="Mathematics">Mathematics</option>
          <option value="Physics">Physics</option>
          <option value="Chemistry">Chemistry</option>
          <option value="Biology">Biology</option>
          <option value="English">English</option>
          <option value="Computer Science">Computer Science</option>
          <option value="Social Science">Social Science</option>
        </select>

        {type === 'textbook' && (
          <input
            type="text"
            name="author"
            value={formData.author}
            onChange={handleChange}
            placeholder="Author (Optional)"
          />
        )}

        <div className="file-input-compact">
          <input
            type="file"
            id={`file-${type}`}
            onChange={handleFileChange}
            accept=".pdf,.doc,.docx,.txt"
            required
            style={{ display: 'none' }}
          />
          <label htmlFor={`file-${type}`} className="file-label">
            {formData.file ? `📄 ${formData.file.name}` : '📎 Choose File *'}
          </label>
        </div>

        <button type="submit" className="compact-upload-btn" disabled={loading}>
          {loading ? '⏳ Uploading...' : `📤 Upload ${type === 'textbook' ? 'Textbook' : 'Paper'}`}
        </button>
      </div>

      {message.text && (
        <div className={`compact-message ${message.type}`}>
          {message.text}
        </div>
      )}
    </form>
  );
};

export default CompactUpload;
