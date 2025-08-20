import React, { useState, useEffect, useRef } from 'react';
import { Send, MessageCircle, User, Bot, Clock } from 'lucide-react';
import {sendChatMessage, getChatHistory} from '../services/apiService';

const ChatComponent = ({ conversationId, onConversationUpdate }) => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hello! I'm your AI assistant. I'm here to help you analyze requirements and design documents. Feel free to ask me any questions about your uploaded documents or request specific analyses.",
      timestamp: new Date().toISOString(),
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState(conversationId);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (currentConversationId) {
      loadConversationHistory(currentConversationId);
    }
  }, [currentConversationId]);

  const loadConversationHistory = async (convId) => {
    try {
      const history = await getChatHistory(convId);
      setMessages(history.messages || []);
    } catch (error) {
      console.error('Error loading conversation history:', error);
      setMessages([]);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    setIsLoading(true);
    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');

    try {
      const response = await sendChatMessage(inputMessage, currentConversationId);
      
      const botMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, botMessage]);
      
      if (!currentConversationId) {
        setCurrentConversationId(response.conversation_id);
        if (onConversationUpdate) {
          onConversationUpdate(response.conversation_id);
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="chat-component">
      <div className="chat-header">
        <MessageCircle size={20} />
        <h3>AI Assistant</h3>
      </div>

      <div className="chat-messages">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${message.role === 'user' ? 'user-message' : 'bot-message'}`}
          >
            <div className="message-avatar">
              {message.role === 'user' ? <User size={16} /> : <Bot size={16} />}
            </div>
            <div className="message-content">
              <div className="message-text">{message.content}</div>
              <div className="message-timestamp">
                <Clock size={12} />
                <span>{new Date(message.timestamp).toLocaleTimeString()}</span>
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message bot-message">
            <div className="message-avatar">
              <Bot size={16} />
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input">
        <textarea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          rows="2"
          disabled={isLoading}
        />
        <button
          onClick={handleSendMessage}
          disabled={isLoading || !inputMessage.trim()}
          className="send-button"
        >
          <Send size={20} />
        </button>
      </div>
    </div>
  );
};

export default ChatComponent;
