import { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';

const ChatInput = ({ onSend, disabled }) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  // Focus input when it becomes enabled
  useEffect(() => {
    if (!disabled && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [disabled]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || disabled) return;
    onSend(input);
    setInput('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative flex items-end gap-2">
      <div className="relative flex-1 bg-gray-50 border border-gray-300 rounded-xl shadow-sm focus-within:ring-1 focus-within:ring-blue-500 focus-within:border-blue-500 overflow-hidden transition-all">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder="Ask a question..."
          className="w-full max-h-[120px] bg-transparent py-3 pl-4 pr-12 text-sm text-gray-900 placeholder-gray-500 resize-none outline-none disabled:opacity-60"
          rows={1}
          maxLength={1000}
        />
        <button
          type="submit"
          disabled={!input.trim() || disabled}
          className="absolute right-2 bottom-1.5 p-2 rounded-lg text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:text-gray-500 transition-colors cursor-pointer"
        >
          <Send size={18} />
        </button>
      </div>
    </form>
  );
};

export default ChatInput;
