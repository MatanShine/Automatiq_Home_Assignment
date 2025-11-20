import React, { useState } from 'react';
import { ChatSession } from '../hooks/useChatHistory';
import '../styles/chat.css'; // We'll add sidebar styles here or in a new file

interface SidebarProps {
    sessions: ChatSession[];
    currentSessionId: string | null;
    onSelectSession: (id: string) => void;
    onCreateSession: () => void;
    onDeleteSession: (id: string, e: React.MouseEvent) => void;
    isOpen: boolean;
    onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
    sessions,
    currentSessionId,
    onSelectSession,
    onCreateSession,
    onDeleteSession,
    isOpen,
    onClose
}) => {
    const [isPanelVisible, setIsPanelVisible] = useState(true);
    
    // Filter to only show sessions that have at least one user message
    const visibleSessions = sessions.filter(session =>
        session.messages.some(msg => msg.isUser)
    );

    // Edit icon SVG (for new chat button)
    const EditIcon = () => (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
        </svg>
    );

    // Split-screen icon SVG (for panel toggle button)
    const PanelIcon = () => (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="3" width="8" height="18" rx="1.5"></rect>
            <line x1="11" y1="3" x2="11" y2="21"></line>
            <line x1="5" y1="7" x2="9" y2="7"></line>
            <line x1="5" y1="10" x2="9" y2="10"></line>
            <rect x="13" y="3" width="8" height="18" rx="1.5"></rect>
        </svg>
    );

    return (
        <>
            <div className={`sidebar-overlay ${isOpen ? 'open' : ''}`} onClick={onClose} />
            <div className={`sidebar ${isOpen ? 'open' : ''} ${!isPanelVisible ? 'minimized' : ''}`}>
                <div className="sidebar-header">
                    <div className={`sidebar-buttons ${!isPanelVisible ? 'stacked' : 'side-by-side'}`}>
                        <button 
                            className="icon-btn new-chat-icon-btn" 
                            onClick={onCreateSession}
                            title="New Chat"
                        >
                            <EditIcon />
                        </button>
                        <button 
                            className="icon-btn panel-toggle-btn" 
                            onClick={() => setIsPanelVisible(!isPanelVisible)}
                            title={isPanelVisible ? "Hide Chat History" : "Show Chat History"}
                        >
                            <PanelIcon />
                        </button>
                    </div>
                </div>
                {isPanelVisible && (
                    <div className="sidebar-content">
                        <div className="sessions-list">
                            {visibleSessions.map((session) => (
                                <div
                                    key={session.id}
                                    className={`session-item ${session.id === currentSessionId ? 'active' : ''}`}
                                    onClick={() => {
                                        onSelectSession(session.id);
                                        if (window.innerWidth <= 768) {
                                            onClose();
                                        }
                                    }}
                                >
                                    <div className="session-info">
                                        <div className="session-title">{session.title}</div>
                                        <div className="session-date">
                                            {new Date(session.timestamp).toLocaleDateString()}
                                        </div>
                                    </div>
                                    <button
                                        className="delete-btn"
                                        onClick={(e) => onDeleteSession(session.id, e)}
                                        title="Delete chat"
                                    >
                                        ×
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </>
    );
};
