import { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';

const ChatWindow = ({ messages, loading, error }) => {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading, error]);

  return (
    <div className="flex-1 overflow-y-auto p-4 sm:p-6 bg-gray-50 flex flex-col gap-4">
      {messages.map((msg, idx) => (
        <MessageBubble key={idx} role={msg.role} content={msg.content} />
      ))}
      
      {loading && (
        <div className="flex justify-start">
          <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
            <TypingIndicator />
          </div>
        </div>
      )}

      {error && (
        <div className="flex justify-center my-2">
          <div className="bg-red-50 text-red-600 text-sm px-4 py-2 rounded-lg border border-red-200 shadow-sm">
            {error}
          </div>
        </div>
      )}
      
      <div ref={bottomRef} />
    </div>
  );
};

export default ChatWindow;
