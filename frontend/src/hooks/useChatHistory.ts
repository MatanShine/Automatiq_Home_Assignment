import { useState, useEffect } from 'react';
import { Message } from '../components/Chat';

export interface ChatSession {
    id: string;
    title: string;
    messages: Message[];
    history: Array<{ role: string; content: string }>;
    timestamp: number;
    employeeId?: string | null;
    employeeName?: string | null;
}

const STORAGE_KEY = 'chat_sessions';

export const useChatHistory = () => {
    const [sessions, setSessions] = useState<ChatSession[]>([]);
    const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);

    // Load sessions from local storage on mount
    useEffect(() => {
        const storedSessions = localStorage.getItem(STORAGE_KEY);
        if (storedSessions) {
            try {
                const parsed = JSON.parse(storedSessions);
                // Convert string timestamps back to Date objects for messages
                const hydratedSessions = parsed.map((session: any) => ({
                    ...session,
                    messages: session.messages.map((msg: any) => ({
                        ...msg,
                        timestamp: new Date(msg.timestamp)
                    }))
                }));
                setSessions(hydratedSessions);
                if (hydratedSessions.length > 0) {
                    setCurrentSessionId(hydratedSessions[0].id);
                } else {
                    createNewSession();
                }
            } catch (e) {
                console.error('Failed to parse chat sessions', e);
                createNewSession();
            }
        } else {
            createNewSession();
        }
    }, []);

    // Save sessions to local storage whenever they change
    useEffect(() => {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
    }, [sessions]);

    const createNewSession = () => {
        // Check if there's already an empty "New Chat" session
        const existingEmptyChat = sessions.find(
            s => s.title === 'New Chat' && s.messages.filter(m => m.isUser).length === 0
        );

        if (existingEmptyChat) {
            // Switch to the existing empty chat instead of creating a new one
            setCurrentSessionId(existingEmptyChat.id);
            return existingEmptyChat.id;
        }

        const newSession: ChatSession = {
            id: Date.now().toString(),
            title: 'New Chat',
            messages: [],
            history: [],
            timestamp: Date.now(),
        };
        setSessions(prev => [newSession, ...prev]);
        setCurrentSessionId(newSession.id);
        return newSession.id;
    };

    const deleteSession = (id: string, e?: React.MouseEvent) => {
        e?.stopPropagation();
        setSessions(prev => {
            const newSessions = prev.filter(s => s.id !== id);
            if (newSessions.length === 0) {
                // If we deleted the last one, create a new one immediately
                // We need to handle this carefully to avoid infinite loops or empty states
                // Ideally we'd call createNewSession but we're inside a state update.
                // So we'll return an empty array and let the effect or a separate check handle it,
                // OR we just create one here.
                const newSession: ChatSession = {
                    id: Date.now().toString(),
                    title: 'New Chat',
                    messages: [],
                    history: [],
                    timestamp: Date.now(),
                };
                if (currentSessionId === id) {
                    setCurrentSessionId(newSession.id);
                }
                return [newSession];
            }

            if (currentSessionId === id) {
                setCurrentSessionId(newSessions[0].id);
            }
            return newSessions;
        });
    };

    const updateCurrentSession = (
        updater: (session: ChatSession) => ChatSession
    ) => {
        if (!currentSessionId) return;

        setSessions(prev => prev.map(session => {
            if (session.id === currentSessionId) {
                return updater(session);
            }
            return session;
        }));
    };

    const currentSession = sessions.find(s => s.id === currentSessionId) || sessions[0];

    return {
        sessions,
        currentSessionId,
        currentSession,
        setCurrentSessionId,
        createNewSession,
        deleteSession,
        updateCurrentSession
    };
};
