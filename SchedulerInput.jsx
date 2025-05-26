import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { PaperAirplaneIcon } from '@heroicons/react/24/outline';

const SchedulerInput = ({ onSubmit }) => {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    setIsLoading(true);
    await onSubmit(input);
    setInput('');
    setIsLoading(false);
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex items-center space-x-2 bg-white/5 backdrop-blur-sm rounded-full p-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your scheduling request..."
            className="flex-1 bg-transparent text-gray-700 placeholder-gray-400 focus:outline-none"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="p-2 rounded-full hover:bg-blue-100/50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500"></div>
            ) : (
              <PaperAirplaneIcon className="h-5 w-5 text-blue-500" />
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default SchedulerInput;
