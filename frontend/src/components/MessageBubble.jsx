import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const MessageBubble = ({ role, content }) => {
  const isUser = role === 'user';
  
  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div 
        className={`max-w-[85%] sm:max-w-[75%] px-4 py-3 shadow-sm ${
          isUser 
            ? 'bg-blue-600 text-white rounded-2xl rounded-tr-sm' 
            : 'bg-white border border-gray-200 text-gray-800 rounded-2xl rounded-tl-sm prose prose-sm prose-blue max-w-none'
        }`}
      >
        <div className="text-[15px] leading-relaxed break-words whitespace-pre-wrap">
          {isUser ? content : (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {content}
            </ReactMarkdown>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
