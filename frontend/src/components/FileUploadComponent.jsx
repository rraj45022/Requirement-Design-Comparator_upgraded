import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, AlertCircle } from 'lucide-react';
import { uploadFile } from '../services/apiService';

const FileUploadComponent = ({ type, onFileUploaded, onItemsParsed }) => {
  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    try {
      const result = await uploadFile(file, type);
      onFileUploaded(file.name);
      onItemsParsed(result.items);
    } catch (error) {
      console.error(`Error uploading ${type} file:`, error);
      alert(`Error uploading ${type} file: ${error.message}`);
    }
  }, [type, onFileUploaded, onItemsParsed]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt'],
      'application/json': ['.json'],
      'application/yaml': ['.yaml', '.yml'],
      'text/yaml': ['.yaml', '.yml'],
    },
    maxFiles: 1,
  });

  return (
    <div className="file-upload-container">
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''}`}
      >
        <input {...getInputProps()} />
        <div className="dropzone-content">
          <Upload size={48} className="dropzone-icon" />
          {isDragActive ? (
            <p>Drop the file here...</p>
          ) : (
            <div>
              <p>Drag & drop a file here, or click to select</p>
              <small>Supports: JSON, YAML, TXT files</small>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const FileDisplay = ({ title, items, filename }) => {
  return (
    <div className="file-display">
      <div className="file-header">
        <FileText size={20} />
        <h3>{title}</h3>
        {filename && <span className="filename">{filename}</span>}
      </div>
      <div className="items-list">
        {items.map((item, index) => (
          <div key={index} className="item">
            <span className="item-number">{index + 1}.</span>
            <span className="item-text">{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export { FileUploadComponent, FileDisplay };
