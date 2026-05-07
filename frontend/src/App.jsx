import { useState, useRef } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [isDragActive, setIsDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (selectedFile) => {
    if (!selectedFile.type.startsWith('image/')) {
      setError("Please upload an image file.");
      return;
    }
    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
    setError(null);
    setResults(null);
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://127.0.0.1:8001/extract-prescription', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server responded with status ${response.status}`);
      }

      const data = await response.json();
      
      if (!data.extracted_data) {
        throw new Error("AI returned invalid data structure.");
      }

      setResults(data.extracted_data);
    } catch (err) {
      setError(err.message || "Something went wrong during analysis.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="glass-panel">
        <header className="header">
          <h1 className="title">MedTech AI</h1>
          <p className="subtitle">Upload a prescription to automatically extract medicines, dosages, and frequencies.</p>
        </header>

        <main>
          <div 
            className={`upload-area ${isDragActive ? 'drag-active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleChange} 
              accept="image/*" 
              style={{ display: 'none' }} 
            />
            <div className="upload-icon">📄</div>
            <h3>Drag & Drop your prescription</h3>
            <p className="subtitle" style={{marginTop: '0.5rem', fontSize: '0.9rem'}}>or click to browse files</p>
          </div>

          {error && <div style={{ color: '#ef4444', textAlign: 'center', marginTop: '1rem', padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px' }}>{error}</div>}

          {preview && (
            <div className="preview-container">
              <img src={preview} alt="Prescription preview" className="preview-image" />
            </div>
          )}

          {preview && (
            <button 
              className="analyze-btn" 
              onClick={handleUpload} 
              disabled={loading}
            >
              {loading ? (
                <><span className="spinner"></span> Analyzing Image...</>
              ) : 'Analyze Prescription'}
            </button>
          )}
        </main>
      </div>

      {results && (
        <div className="glass-panel results-container">
          <div className="results-header" style={{flexDirection: 'column', alignItems: 'flex-start', gap: '1rem'}}>
            <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
               <span style={{ fontSize: '1.5rem' }}>📋</span>
               <h2 className="results-title">Patient Profile</h2>
            </div>
            <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', width: '100%', background: 'rgba(255,255,255,0.05)', padding: '1rem', borderRadius: '12px'}}>
               <div><strong style={{color: 'var(--text-muted)'}}>Patient Name:</strong> {results.patient_name || 'N/A'}</div>
               <div><strong style={{color: 'var(--text-muted)'}}>Date:</strong> {results.date || 'N/A'}</div>
            </div>
          </div>

          <div className="results-header" style={{marginTop: '2rem'}}>
            <span style={{ fontSize: '1.5rem' }}>💊</span>
            <h2 className="results-title">Extracted Medicines</h2>
          </div>
          
          {results.medications && results.medications.length > 0 ? (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Medicine Name</th>
                    <th>Dosage</th>
                    <th>Frequency</th>
                    <th>Duration</th>
                  </tr>
                </thead>
                <tbody>
                  {results.medications.map((item, index) => (
                    <tr key={index}>
                      <td className="med-name">{item.name || 'N/A'}</td>
                      <td>{item.dosage || 'N/A'}</td>
                      <td>
                        <span className="badge">{item.frequency || 'N/A'}</span>
                      </td>
                      <td>{item.duration || 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state">
              No medicines could be extracted from this image.
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
