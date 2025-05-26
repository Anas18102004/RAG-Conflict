import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import InputBox from './components/InputBox';
import ResultCards from './components/ResultCards';

// Add a logo SVG (placeholder)
const Logo = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="20" cy="20" r="20" fill="#2563eb" fillOpacity="0.8" />
    <path d="M12 20c0-4.418 3.582-8 8-8s8 3.582 8 8-3.582 8-8 8-8-3.582-8-8zm8-5a5 5 0 100 10 5 5 0 000-10z" fill="#fff" />
  </svg>
);

function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);

  useEffect(() => {
    // Check system preference for dark mode
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setDarkMode(true);
    }
  }, []);

  useEffect(() => {
    // Apply dark mode class to document
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const handleSubmit = async (query) => {
    setLoading(true);
    try {
      // Add user message to chat history
      setChatHistory(prev => [...prev, { type: 'user', content: query }]);

      console.log('Sending query:', query); // Debug log

      const response = await fetch('http://localhost:8000/analyze-query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Received response:', data); // Debug log

      // Validate response format
      if (!data || typeof data !== 'object') {
        throw new Error('Invalid response format: response is not an object');
      }

      if (!data.type) {
        throw new Error('Invalid response format: missing type field');
      }

      setResults(data);

      // Add assistant response to chat history
      if (data.type === 'chat') {
        if (!data.response) {
          throw new Error('Invalid chat response: missing response field');
        }
        setChatHistory(prev => [...prev, { 
          type: 'assistant', 
          content: data.response 
        }]);
      } else if (data.type === 'scheduling') {
        setChatHistory(prev => [...prev, { 
          type: 'assistant', 
          content: data.rationale || 'Here are the scheduling suggestions.' 
        }]);
      } else {
        console.error('Unknown response type:', data.type);
        setChatHistory(prev => [...prev, { 
          type: 'error', 
          content: `Received unexpected response type: ${data.type}` 
        }]);
      }
    } catch (error) {
      console.error('Error:', error);
      setChatHistory(prev => [...prev, { 
        type: 'error', 
        content: `Error: ${error.message}` 
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-blue-100 via-indigo-100 to-pink-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 font-sans transition-colors duration-200">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        html { font-family: 'Inter', sans-serif; }
      `}</style>
      <div className="container mx-auto py-8 flex flex-col items-center">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-4 mb-8"
        >
          <Logo />
          <div className="text-left">
            <h1 className="text-4xl font-extrabold text-gray-800 dark:text-white mb-1 tracking-tight drop-shadow-lg">
              Smart Assistant
            </h1>
            <p className="text-gray-600 dark:text-gray-300 text-lg font-medium">
              Ask me anything or schedule meetings intelligently
            </p>
          </div>
        </motion.div>

        <div className="w-full max-w-2xl mx-auto">
          {/* Chat History */}
          <div className="space-y-4 mb-6 max-h-[60vh] overflow-y-auto rounded-2xl p-6 bg-white/60 dark:bg-gray-800/60 shadow-2xl backdrop-blur-md border border-gray-200 dark:border-gray-700 transition-all">
            {chatHistory.map((message, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.04 }}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-5 py-3 shadow-md transition-all
                    ${message.type === 'user'
                      ? 'bg-blue-500 text-white rounded-br-sm'
                      : message.type === 'error'
                      ? 'bg-red-500 text-white'
                      : 'bg-white/80 dark:bg-gray-700/80 text-gray-800 dark:text-white border border-gray-200 dark:border-gray-600'}
                  `}
                  style={{backdropFilter: 'blur(6px)'}}
                >
                  {message.content}
                </div>
              </motion.div>
            ))}
          </div>

          <InputBox onSubmit={handleSubmit} />

          {loading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center mt-8"
            >
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
            </motion.div>
          )}

          {results && results.type === 'scheduling' && <ResultCards results={results} />}

          <button
            onClick={() => setDarkMode(!darkMode)}
            className="fixed bottom-4 right-4 p-3 rounded-full bg-white/80 dark:bg-gray-700/80 shadow-lg border border-gray-200 dark:border-gray-600 hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors duration-200 text-2xl"
            style={{backdropFilter: 'blur(6px)'}}
            aria-label="Toggle dark mode"
          >
            {darkMode ? '🌞' : '🌙'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
