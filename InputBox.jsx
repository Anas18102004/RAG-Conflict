import React, { useState } from 'react';
import { motion } from 'framer-motion';

const InputBox = ({ onSubmit }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSubmit(query);
      setQuery('');
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-2xl mx-auto p-6"
    >
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Schedule a meeting with Alice next Monday..."
            className="w-full px-6 py-4 text-lg bg-white dark:bg-gray-800 rounded-xl shadow-lg
                     border border-gray-200 dark:border-gray-700
                     focus:outline-none focus:ring-2 focus:ring-blue-500
                     transition-all duration-200
                     placeholder-gray-400 dark:placeholder-gray-500"
          />
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            type="submit"
            className="absolute right-3 top-1/2 transform -translate-y-1/2
                     bg-blue-500 hover:bg-blue-600 text-white
                     px-6 py-2 rounded-lg shadow-md
                     transition-colors duration-200"
          >
            Schedule
          </motion.button>
        </div>
      </form>
    </motion.div>
  );
};

export default InputBox; 