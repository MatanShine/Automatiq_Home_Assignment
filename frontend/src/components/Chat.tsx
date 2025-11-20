import React, { useState, useEffect, useRef } from 'react';
import { ChatMessage, ChatMessageProps } from './ChatMessage';
import { InputBar } from './InputBar';
import { ThemeToggle } from './ThemeToggle';
import { apiClient } from '../api/client';
import '../styles/chat.css';

export interface Message extends Omit<ChatMessageProps, 'timestamp'> {
  id: string;
  timestamp: Date;
}

interface ChatProps {
  messages: Message[];
  history: Array<{ role: string; content: string }>;
  employeeId?: string | null;
  employeeName?: string | null;
  onUpdateSession: (
    messages: Message[],
    history: Array<{ role: string; content: string }>,
    employeeId?: string | null,
    employeeName?: string | null
  ) => void;
  onToggleSidebar: () => void;
}

export const Chat: React.FC<ChatProps> = ({
  messages,
  history,
  employeeId,
  employeeName,
  onUpdateSession,
  onToggleSidebar
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // We keep employee state here to persist across a single session's API calls if needed,
  // but ideally it should come from the session too if we want to resume perfectly.
  // For now, we'll rely on the passed history, but the API might need the IDs.
  // The previous code stored them in state. Let's assume the parent manages them in the session if needed.
  // Actually, the previous code sent employeeId/Name in sendMessage.
  // We should probably store them in the session.

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Show system message after 1 second if empty
  useEffect(() => {
    if (messages.length === 0) {
      const timer = setTimeout(() => {
        const systemMessage: Message = {
          id: 'system-init',
          message: 'Hello! Please provide your name and ID before asking anything further.',
          isUser: false,
          timestamp: new Date(),
        };

        // Check again to avoid race conditions
        if (messages.length === 0) {
          onUpdateSession(
            [systemMessage],
            [{ role: 'system', content: systemMessage.message }]
          );
        }
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [messages.length]); // Only run if messages length changes to 0 (new session)

  const handleSendMessage = async (messageText: string) => {
    // Add user message immediately
    const userMessage: Message = {
      id: Date.now().toString(),
      message: messageText,
      isUser: true,
      timestamp: new Date(),
    };

    const newMessages = [...messages, userMessage];
    const newHistory = [...history, { role: 'user', content: messageText }];

    // Optimistic update
    onUpdateSession(newMessages, newHistory);

    setIsLoading(true);
    setError(null);

    try {
      // We need to retrieve employeeId/Name from the session (passed via props? or just stored in history?)
      // The previous code stored them in state.
      // Let's try to find them in the session or just pass null if we don't have them.
      // If the backend relies on them being passed back, we need to store them in the session.
      // The hook has employeeId/Name in ChatSession. We should pass them as props.
      // For now, I'll assume we can just pass null and the backend handles history.
      // Wait, the previous code: `setEmployeeId(response.employee_id)`

      const response = await apiClient.sendMessage(
        messageText,
        newHistory,
        employeeId ?? null,
        employeeName ?? null
      );

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        message: response.message,
        isUser: false,
        timestamp: new Date(),
      };

      onUpdateSession(
        [...newMessages, assistantMessage],
        [...newHistory, { role: 'assistant', content: response.message }],
        response.employee_id,
        response.employee_name
      );

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);

      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        message: `Error: ${errorMessage}`,
        isUser: false,
        timestamp: new Date(),
      };

      onUpdateSession([...newMessages, errorMsg], newHistory);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button className="menu-btn" onClick={onToggleSidebar}>
            ☰
          </button>
          <h1>Cybersecurity Training Assistant</h1>
        </div>
        <ThemeToggle />
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

