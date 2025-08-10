import React, { useState } from 'react';
import { FileUploadComponent, FileDisplay } from './components/FileUploadComponent';
import AnalysisResultsComponent from './components/AnalysisResultsComponent';
import ChatComponent from './components/ChatComponent';
import { analyzeDocuments, getLLMFeedback } from './services/apiService';
import ReactMarkdown from 'react-markdown';
import './App.css';

function App() {
  const [requirements, setRequirements] = useState([]);
  const [design, setDesign] = useState([]);
  const [analysisResults, setAnalysisResults] = useState([]);
  const [summary, setSummary] = useState(null);
  const [llmFeedback, setLlmFeedback] = useState(null);
  const [currentConversationId, setCurrentConversationId] = useState(null);

  const handleRequirementsUploaded = (filename) => {
    console.log('Requirements uploaded:', filename);
  };

  const handleDesignUploaded = (filename) => {
    console.log('Design uploaded:', filename);
  };

  const handleRequirementsParsed = (items) => {
    setRequirements(items);
  };

  const handleDesignParsed = (items) => {
    setDesign(items);
  };

  const handleAnalyze = async () => {
    if (requirements.length === 0 || design.length === 0) {
      alert('Please upload both requirements and design documents first.');
      return;
    }

    try {
      const results = await analyzeDocuments(requirements, design);
      setAnalysisResults(results);
      setLlmFeedback(null);

      // Calculate summary
      const summary = {
        total_requirements: requirements.length,
        total_design_items: design.length,
        covered_requirements: results.filter(r => r.coverage === 'Present').length,
        missing_requirements: results.filter(r => r.coverage === 'Missing').length,
      };
      setSummary(summary);
    } catch (error) {
      console.error('Error analyzing documents:', error);
      alert('Error analyzing documents: ' + error.message);
    }
  };

  const handleGetLLMFeedback = async () => {
    if (requirements.length === 0 || design.length === 0) {
      alert('Please upload both requirements and design documents first.');
      return;
    }

    try {
      const response = await getLLMFeedback(requirements, design);
      setLlmFeedback(response);
      setAnalysisResults(response.semantic_analysis);

      // Update summary based on LLM feedback summary
      if (response.summary) {
        setSummary({
          total_requirements: response.summary.total_requirements,
          total_design_items: response.summary.total_design_items,
          covered_requirements: response.summary.covered_requirements,
          missing_requirements: response.summary.missing_requirements,
        });
      }
    } catch (error) {
      console.error('Error getting LLM feedback:', error);
      alert('Error getting LLM feedback: ' + error.message);
    }
  };

  const handleConversationUpdate = (conversationId) => {
    setCurrentConversationId(conversationId);
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>Requirements vs Design Comparator</h1>
        <p>Semantic analysis and AI-powered comparison tool</p>
      </header>

      <main className="app-main">
        <section className="upload-section">
          <h2>Upload Documents</h2>
          <div className="upload-grid">
      <div className="upload-card">
        <h3>Requirements</h3>
        <FileUploadComponent
          type="requirements"
          onFileUploaded={handleRequirementsUploaded}
          onItemsParsed={handleRequirementsParsed}
        />
        <FileDisplay title="Requirements Items" items={requirements} />
      </div>
      
      <div className="upload-card">
        <h3>Design</h3>
        <FileUploadComponent
          type="design"
          onFileUploaded={handleDesignUploaded}
          onItemsParsed={handleDesignParsed}
        />
        <FileDisplay title="Design Items" items={design} />
      </div>
    </div>
    
    <button 
      onClick={handleAnalyze}
      className="analyze-button"
          disabled={requirements.length === 0 || design.length === 0}
        >
          Analyze Documents
        </button>
        <button
          onClick={handleGetLLMFeedback}
          className="analyze-button"
          disabled={requirements.length === 0 || design.length === 0}
          style={{ marginLeft: '1rem' }}
        >
          Get LLM Feedback
        </button>
      </section>

        {analysisResults.length > 0 && (
          <section className="results-section">
            <h2>Analysis Results</h2>
            <AnalysisResultsComponent 
              results={analysisResults} 
              summary={summary}
            />
            {llmFeedback && llmFeedback.llm_feedback && (
              <div className="llm-feedback">
                <h3>LLM Feedback</h3>
                <ReactMarkdown>{llmFeedback.llm_feedback}</ReactMarkdown>
              </div>
            )}
          </section>
        )}

        <section className="chat-section">
          <h2>AI Assistant</h2>
          <ChatComponent 
            conversationId={currentConversationId}
            onConversationUpdate={handleConversationUpdate}
          />
        </section>
      </main>

      <footer className="app-footer">
        <p>&copy; 2024 Requirements vs Design Comparator. Built with React & FastAPI.</p>
      </footer>
    </div>
  );
}

export default App;
