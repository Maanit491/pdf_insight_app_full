import React, { useState } from 'react';
import '../styles/chatbot.css';
import axios from 'axios';
import BotIcon from './boticon.svg';
import Spinner from './spinner.svg';

function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');

  const backendURL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';


  const handleMessageSubmit = async () => {
    if (inputValue.trim() === '') return;
    setMessages(prev => [...prev, { text: inputValue, sender: 'user' }]);
    setInputValue('');
    setIsLoading(true);
    try {
      const response = await axios.post(`${backendURL}/api/query`, { question: inputValue });
      const answer = response.data.answer;
      setMessages(prev => [...prev, { text: answer, sender: 'bot' }]);
    } catch (error) {
      console.error('Error sending query:', error);
      setMessages(prev => [
        ...prev,
        { text: 'An error occurred. Please try again later.', sender: 'bot' }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleFileUpload = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append("file", selectedFile);

    setUploadStatus("Uploading...");

    try {
      const response = await axios.post(`${backendURL}/uploadfile/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setUploadStatus("✅ File uploaded successfully.");
      console.log(response.data);
    } catch (error) {
      console.error('Error uploading file:', error);
      setUploadStatus("❌ Upload failed. Please try again.");
    }
  };

  return (
    <div className="chatbot-container">
      {/* PDF Upload Section */}
      <div className="upload-section">
        <input type="file" accept="application/pdf" onChange={handleFileChange} />
        <button onClick={handleFileUpload}>Upload PDF</button>
        {uploadStatus && <p style={{ marginTop: '5px' }}>{uploadStatus}</p>}
      </div>

      {/* Chat Messages */}
      <div className="messages-container">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.sender}`}>
            <div className="circle">
              {message.sender === 'user' ? 'U' : <img src={BotIcon} alt="Bot" />}
            </div>
            <div className="text">{message.text}</div>
          </div>
        ))}
        {isLoading && (
          <div className="message bot">
            <div className="circle"><img src={BotIcon} alt="Bot" /></div>
            <div className="text"><img src={Spinner} alt="Loading..." className="spinner" /></div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="input-container">
        <input
          type="text"
          placeholder="Send a message..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
        />
        <button className="send-button" onClick={handleMessageSubmit}>
          <svg width="19" height="16" viewBox="0 0 19 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18.1667 7.99999L0.75 15.3333L4.01608 7.99999L0.75 0.666656L18.1667 7.99999ZM18.1667 7.99999H3.95833" stroke="#222222" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>
      </div>
    </div>
  );
}

export default Chatbot;
