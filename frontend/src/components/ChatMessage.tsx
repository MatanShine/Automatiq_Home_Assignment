import React from 'react';
import '../styles/chat.css';

export interface ChatMessageProps {
  message: string;
  isUser: boolean;
  timestamp?: Date;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  isUser,
  timestamp,
}) => {
  return (
    <div className={`chat-message ${isUser ? 'user-message' : 'assistant-message'}`}>
      <div className="message-content">
        <div className="message-text">{message}</div>
        {timestamp && (
          <div className="message-timestamp">
            {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        )}
      </div>
    </div>
  );
};

