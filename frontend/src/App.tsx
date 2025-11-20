import { useState } from 'react';
import { Chat, Message } from './components/Chat';
import { Sidebar } from './components/Sidebar';
import { ThemeProvider } from './context/ThemeContext';
import { useChatHistory } from './hooks/useChatHistory';
import './styles/chat.css';

function App() {
  const {
    sessions,
    currentSessionId,
    currentSession,
    setCurrentSessionId,
    createNewSession,
    deleteSession,
    updateCurrentSession
  } = useChatHistory();

  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const handleUpdateSession = (
    messages: Message[],
    history: Array<{ role: string; content: string }>,
    employeeId?: string | null,
    employeeName?: string | null
  ) => {
    updateCurrentSession((session) => {
      // If it's the first user message, update the title
      let title = session.title;
      const hasUserMessage = session.messages.some(m => m.isUser);
      if (!hasUserMessage && messages.length > 0) {
        const firstUserMsg = messages.find(m => m.isUser);
        if (firstUserMsg) {
          title = firstUserMsg.message.slice(0, 30) + (firstUserMsg.message.length > 30 ? '...' : '');
        }
      }

      return {
        ...session,
        messages,
        history,
        title,
        employeeId: employeeId ?? session.employeeId,
        employeeName: employeeName ?? session.employeeName,
      };
    });
  };

  return (
    <ThemeProvider>
      <div className="App">
        <Sidebar
          sessions={sessions}
          currentSessionId={currentSessionId}
          onSelectSession={setCurrentSessionId}
          onCreateSession={createNewSession}
          onDeleteSession={deleteSession}
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
        />
        <div className={`main-content ${isSidebarOpen ? 'sidebar-open' : ''}`}>
          <Chat
            key={currentSessionId} // Remount chat on session change to reset transient state
            messages={currentSession?.messages || []}
            history={currentSession?.history || []}
            employeeId={currentSession?.employeeId}
            employeeName={currentSession?.employeeName}
            onUpdateSession={handleUpdateSession}
            onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
          />
        </div>
      </div>
    </ThemeProvider>
  );
}

export default App;

