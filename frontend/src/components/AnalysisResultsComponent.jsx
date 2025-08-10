import React from 'react';
import { CheckCircle, AlertTriangle, XCircle, TrendingUp } from 'lucide-react';

const AnalysisResultsComponent = ({ results, summary }) => {
  if (!results || results.length === 0) {
    return (
      <div className="analysis-results empty">
        <p>No analysis results to display.</p>
      </div>
    );
  }

  const getCoverageIcon = (coverage) => {
    switch (coverage?.toLowerCase()) {
      case 'present':
        return <CheckCircle size={20} className="text-green-500" />;
      case 'missing':
        return <XCircle size={20} className="text-red-500" />;
      default:
        return <AlertTriangle size={20} className="text-yellow-500" />;
    }
  };

  const getSimilarityColor = (score) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.5) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="analysis-results">
      {summary && (
        <div className="analysis-summary">
          <h3>Analysis Summary</h3>
          <div className="summary-stats">
            <div className="stat">
              <span className="stat-label">Total Requirements</span>
              <span className="stat-value">{summary.total_requirements}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Covered</span>
              <span className="stat-value text-green-600">{summary.covered_requirements}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Missing</span>
              <span className="stat-value text-red-600">{summary.missing_requirements}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Coverage Rate</span>
              <span className="stat-value">
                {((summary.covered_requirements / summary.total_requirements) * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        </div>
      )}

      <div className="results-list">
        <h3>Detailed Analysis</h3>
        {results.map((result, index) => (
          <div key={index} className="result-item">
            <div className="result-header">
              <div className="coverage-status">
                {getCoverageIcon(result.coverage)}
                <span className={`coverage-text ${result.coverage?.toLowerCase() === 'present' ? 'text-green-600' : 'text-red-600'}`}>
                  {result.coverage}
                </span>
              </div>
              <div className={`similarity-score ${getSimilarityColor(result.similarity_score)}`}>
                <TrendingUp size={16} />
                <span>{(result.similarity_score * 100).toFixed(1)}%</span>
              </div>
            </div>
            
            <div className="requirement-text">
              <strong>Requirement:</strong> {result.requirement}
            </div>
            
            {result.issue && (
              <div className="issue-text">
                <AlertTriangle size={16} className="inline mr-2" />
                <strong>Issue:</strong> {result.issue}
              </div>
            )}
            
            {result.matched_design_items && result.matched_design_items.length > 0 && (
              <div className="matched-items">
                <strong>Matched Design Items:</strong>
                <ul>
                  {result.matched_design_items.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default AnalysisResultsComponent;
