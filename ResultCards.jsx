import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircleIcon, ExclamationCircleIcon, LightBulbIcon } from '@heroicons/react/24/outline';

const ResultCard = ({ type, title, content, icon: Icon }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg
               border border-gray-200 dark:border-gray-700
               hover:shadow-xl transition-shadow duration-200"
  >
    <div className="flex items-start space-x-4">
      <div className="flex-shrink-0">
        <Icon className="w-8 h-8" />
      </div>
      <div>
        <h3 className="text-lg font-semibold mb-2">{title}</h3>
        <div className="text-gray-600 dark:text-gray-300">{content}</div>
      </div>
    </div>
  </motion.div>
);

const ResultCards = ({ results }) => {
  if (!results || results.type !== 'scheduling') return null;

  const { suggested, conflicts, alternatives, rationale } = results;

  return (
    <div className="space-y-6 max-w-2xl mx-auto p-6">
      {suggested && suggested.length > 0 && (
        <ResultCard
          type="success"
          title="Suggested Times"
          content={
            <ul className="list-disc list-inside space-y-2">
              {suggested.map((time, index) => (
                <li key={index}>{time}</li>
              ))}
            </ul>
          }
          icon={CheckCircleIcon}
        />
      )}

      {conflicts && conflicts.length > 0 && (
        <ResultCard
          type="warning"
          title="Conflicts"
          content={
            <ul className="list-disc list-inside space-y-2">
              {conflicts.map((conflict, index) => (
                <li key={index}>{conflict}</li>
              ))}
            </ul>
          }
          icon={ExclamationCircleIcon}
        />
      )}

      {alternatives && alternatives.length > 0 && (
        <ResultCard
          type="info"
          title="Alternative Suggestions"
          content={
            <ul className="list-disc list-inside space-y-2">
              {alternatives.map((alt, index) => (
                <li key={index}>{alt}</li>
              ))}
            </ul>
          }
          icon={LightBulbIcon}
        />
      )}

      {rationale && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-sm text-gray-500 dark:text-gray-400 italic mt-4"
        >
          {rationale}
        </motion.div>
      )}
    </div>
  );
};

export default ResultCards; 