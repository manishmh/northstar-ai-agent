import { useState, useEffect, useRef } from 'react';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import LeadSummary from './components/LeadSummary';
import { Home, RefreshCw } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function generateUUID() {
  return crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).substring(2) + Date.now().toString(36);
}

function App() {
  const [sessionId, setSessionId] = useState(() => {
    return sessionStorage.getItem('ns_session_id') || generateUUID();
  });
  
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hi! I'm the Northstar Homes AI assistant. I can help you with Northstar One in Sector 79, Gurugram, including available configurations, starting prices, and site visits.\n\nWhat are you looking for — a 2 BHK or 3 BHK?"
    }
  ]);
  const [loading, setLoading] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const [error, setError] = useState(null);
  const [conversationEnded, setConversationEnded] = useState(false);
  const [analytics, setAnalytics] = useState(null);
  
  const isSending = useRef(false);

  useEffect(() => {
    sessionStorage.setItem('ns_session_id', sessionId);
    
    // Attempt to restore session
    const restoreSession = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/session/${sessionId}`);
        if (res.ok) {
          const data = await res.json();
          if (data.conversation_history && data.conversation_history.length > 0) {
            // Filter out system and tool messages for UI
            const uiMessages = data.conversation_history
              .filter(msg => msg.role === 'user' || msg.role === 'assistant')
              .map(msg => ({ role: msg.role, content: msg.content }));
            
            if (uiMessages.length > 0) {
              const welcomeMsg = {
                role: 'assistant',
                content: "Hi! I'm the Northstar Homes AI assistant. I can help you with Northstar One in Sector 79, Gurugram, including available configurations, starting prices, and site visits.\n\nWhat are you looking for — a 2 BHK or 3 BHK?"
              };
              setMessages([welcomeMsg, ...uiMessages]);
            }
          }
          if (data.conversation_ended) {
            setConversationEnded(true);
          }
          fetchAnalytics(sessionId);
        }
      } catch (err) {
        console.error("Failed to restore session:", err);
      } finally {
        setIsInitializing(false);
      }
    };
    
    restoreSession();
  }, [sessionId]);

  const fetchAnalytics = async (sid) => {
    try {
      const res = await fetch(`${API_BASE_URL}/analytics/${sid}`);
      if (res.ok) {
        const data = await res.json();
        setAnalytics(data);
      }
    } catch (err) {
      console.error("Failed to fetch analytics:", err);
    }
  };

  const handleSendMessage = async (text) => {
    if (!text.trim() || conversationEnded || loading || isSending.current) return;
    
    isSending.current = true;
    const userMsg = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, message: text }),
      });

      if (!res.ok) {
        throw new Error(`HTTP Error ${res.status}`);
      }

      const data = await res.json();
      
      setMessages((prev) => [...prev, { role: 'assistant', content: data.reply }]);
      
      if (data.conversation_ended) {
        setConversationEnded(true);
      }
      
      // Fetch analytics in the background to update the side panel
      fetchAnalytics(sessionId);
      
    } catch (err) {
      console.error(err);
      setError("I couldn't connect right now. Please try again.");
    } finally {
      setLoading(false);
      isSending.current = false;
    }
  };

  const handleReset = async () => {
    try {
      await fetch(`${API_BASE_URL}/reset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      });
    } catch (err) {
      console.error("Failed to reset backend session:", err);
    }
    
    const newSessionId = generateUUID();
    setSessionId(newSessionId);
    setMessages([
      {
        role: 'assistant',
        content: "Hi! I'm the Northstar Homes AI assistant. I can help you with Northstar One in Sector 79, Gurugram, including available configurations, starting prices, and site visits.\n\nWhat are you looking for — a 2 BHK or 3 BHK?"
      }
    ]);
    setConversationEnded(false);
    setError(null);
    setAnalytics(null);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <header className="bg-white shadow-sm py-4 px-6 flex justify-between items-center z-10">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600 p-2 rounded-lg text-white">
            <Home size={24} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900 leading-tight">Northstar Homes</h1>
            <p className="text-xs text-gray-500">Northstar One · Sector 79, Gurugram</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1 bg-blue-50 text-blue-700 text-xs font-semibold rounded-full border border-blue-100">
            <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
            AI Sales Assistant
          </div>
          <button 
            onClick={handleReset}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 cursor-pointer"
          >
            <RefreshCw size={16} />
            <span className="hidden sm:inline">New Conversation</span>
          </button>
        </div>
      </header>

      <main className="flex-1 overflow-hidden flex flex-col md:flex-row max-w-7xl w-full mx-auto">
        <div className="flex-1 flex flex-col h-full bg-white shadow-lg md:my-4 md:rounded-lg overflow-hidden border border-gray-200 relative">
          {isInitializing ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="flex flex-col items-center text-gray-500">
                <RefreshCw className="animate-spin mb-2" size={24} />
                <p className="text-sm">Restoring conversation...</p>
              </div>
            </div>
          ) : (
            <ChatWindow 
              messages={messages} 
              loading={loading} 
              error={error} 
            />
          )}
          
          <div className="border-t border-gray-200 bg-white p-4">
            {conversationEnded ? (
              <div className="text-center py-3 bg-gray-50 rounded-lg border border-gray-200">
                <p className="text-gray-600 text-sm mb-2">This conversation has ended.</p>
                <button 
                  onClick={handleReset}
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium cursor-pointer"
                >
                  Start New Conversation
                </button>
              </div>
            ) : (
              <ChatInput onSend={handleSendMessage} disabled={loading} />
            )}
          </div>
        </div>
        
        {/* Optional Lead Summary side panel on large screens */}
        {analytics && (
          <div className="hidden lg:block w-80 p-4 shrink-0 overflow-y-auto">
            <LeadSummary data={analytics} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
