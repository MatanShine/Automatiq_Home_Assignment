import React, { useState, useEffect, useRef } from 'react';
import { ChatMessage, ChatMessageProps } from './ChatMessage';
import { InputBar } from './InputBar';
import { apiClient } from '../api/client';
import '../styles/chat.css';

export interface Message extends Omit<ChatMessageProps, 'timestamp'> {
  id: string;
  timestamp: Date;
}

const EMPLOYEE_ID_KEY = 'chat_employee_id';
const EMPLOYEE_NAME_KEY = 'chat_employee_name';

export const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<Array<{ role: string; content: string }>>([]);
  const [employeeId, setEmployeeId] = useState<string | null>(() => {
    return sessionStorage.getItem(EMPLOYEE_ID_KEY);
  });
  const [employeeName, setEmployeeName] = useState<string | null>(() => {
    return sessionStorage.getItem(EMPLOYEE_NAME_KEY);
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (messageText: string) => {
    // Add user message immediately
    const userMessage: Message = {
      id: Date.now().toString(),
      message: messageText,
      isUser: true,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    
    // Update history with user message
    const updatedHistory = [
      ...history,
      { role: 'user', content: messageText }
    ];
    setHistory(updatedHistory);
    
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.sendMessage(
        messageText,
        updatedHistory,
        employeeId,
        employeeName
      );
      
      // Save employee_id and employee_name if they're not null
      if (response.employee_id !== null && response.employee_id !== undefined) {
        setEmployeeId(response.employee_id);
        sessionStorage.setItem(EMPLOYEE_ID_KEY, response.employee_id);
      }
      if (response.employee_name !== null && response.employee_name !== undefined) {
        setEmployeeName(response.employee_name);
        sessionStorage.setItem(EMPLOYEE_NAME_KEY, response.employee_name);
      }
      
      // Add assistant response
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        message: response.message,
        isUser: false,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
      
      // Update history with assistant response
      setHistory([
        ...updatedHistory,
        { role: 'assistant', content: response.message }
      ]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      
      // Add error message
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        message: `Error: ${errorMessage}`,
        isUser: false,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>Cybersecurity Training Assistant</h1>
      </div>
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="empty-state">
            <p>Start a conversation by asking about training progress or employee status.</p>
          </div>
        )}
        {messages.map((msg) => (
          <ChatMessage
            key={msg.id}
            message={msg.message}
            isUser={msg.isUser}
            timestamp={msg.timestamp}
          />
        ))}
        {isLoading && (
          <div className="chat-message assistant-message">
            <div className="message-content">
              <div className="message-text">
                <span className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="chat-input-container">
        {error && <div className="error-message">{error}</div>}
        <InputBar onSendMessage={handleSendMessage} disabled={isLoading} />
      </div>
    </div>
  );
};

