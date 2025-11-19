import React from 'react';
import '../styles/chat.css';

export interface ChatMessageProps {
  message: string;
  isUser: boolean;
  timestamp?: Date;
}

const parseMessage = (text: string): React.ReactNode[] => {
  const lines = text.split('\n');
  const result: React.ReactNode[] = [];

  lines.forEach((line, lineIndex) => {
    // Check if line starts with ###
    if (line.trim().startsWith('###')) {
      const headerText = line.replace(/^###\s*/, '');
      // Parse bold text within the header
      const headerParts = parseBold(headerText);
      result.push(
        <div key={lineIndex} className="message-header">
          {headerParts}
        </div>
      );
    } else if (line.trim()) {
      // Regular line with potential bold text
      const lineParts = parseBold(line);
      result.push(
        <div key={lineIndex} className="message-line">
          {lineParts}
        </div>
      );
    } else {
      // Empty line
      result.push(<br key={lineIndex} />);
    }
  });

  return result;
};

const parseBold = (text: string): React.ReactNode[] => {
  const parts: React.ReactNode[] = [];
  const regex = /\*\*(.*?)\*\*/g;
  let lastIndex = 0;
  let match;
  let key = 0;

  while ((match = regex.exec(text)) !== null) {
    // Add text before the bold
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index));
    }
    // Add bold text
    parts.push(
      <strong key={key++}>{match[1]}</strong>
    );
    lastIndex = regex.lastIndex;
  }

  // Add remaining text
  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }

  // If no bold text found, return the original text
  return parts.length > 0 ? parts : [text];
};

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  isUser,
  timestamp,
}) => {
  return (
    <div className={`chat-message ${isUser ? 'user-message' : 'assistant-message'}`}>
      <div className="message-content">
        <div className="message-text">{parseMessage(message)}</div>
        {timestamp && (
          <div className="message-timestamp">
            {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        )}
      </div>
    </div>
  );
};

