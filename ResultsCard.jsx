import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  CheckCircleIcon,
  XCircleIcon,
  InformationCircleIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  ClockIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline';

const ResultsCard = ({ 
  type,
  timeRange,
  participants,
  location,
  conflicts,
  alternatives,
  rationale
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const icons = {
    suggested: CheckCircleIcon,
    conflict: XCircleIcon,
    alternative: InformationCircleIcon,
  };

  const Icon = icons[type];

  const statusColors = {
    suggested: 'bg-green-100 text-green-800',
    conflict: 'bg-red-100 text-red-800',
    alternative: 'bg-yellow-100 text-yellow-800',
  };

  const renderTimeRange = () => {
    if (Array.isArray(timeRange)) {
      return timeRange.map((range, index) => (
        <div key={index} className="flex items-center space-x-2 text-gray-600">
          <ClockIcon className="h-4 w-4" />
          <span>{range}</span>
        </div>
      ));
    }
    return (
      <div className="flex items-center space-x-2 text-gray-600">
        <ClockIcon className="h-4 w-4" />
        <span>{timeRange}</span>
      </div>
    );
  };

  const renderParticipants = () => {
    if (!participants?.length) return null;
    return (
      <div className="flex items-center space-x-2 text-gray-600">
        <UserGroupIcon className="h-4 w-4" />
        <span>{participants.join(', ')}</span>
      </div>
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="mb-4 overflow-hidden rounded-2xl bg-white/5 backdrop-blur-sm shadow-lg"
    >
      <div className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Icon className={`h-6 w-6 ${statusColors[type]}`} />
            <span className="text-lg font-semibold">{type.charAt(0).toUpperCase() + type.slice(1)}</span>
          </div>
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="text-gray-500 hover:text-gray-700"
          >
            {isOpen ? (
              <ChevronUpIcon className="h-5 w-5" />
            ) : (
              <ChevronDownIcon className="h-5 w-5" />
            )}
          </button>
        </div>

        <div className="mt-3 space-y-2">
          {renderTimeRange()}
          {renderParticipants()}
          {location && (
            <div className="flex items-center space-x-2 text-gray-600">
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span>{location}</span>
            </div>
          )}
        </div>

        {isOpen && (
          <div className="mt-4 p-4 border-t border-gray-200">
            {conflicts?.length > 0 && (
              <div className="mb-4">
                <h3 className="font-semibold text-red-600 mb-2">Conflicts</h3>
                <ul className="space-y-1">
                  {conflicts.map((conflict, index) => (
                    <li key={index} className="text-red-500">
                      <XCircleIcon className="h-4 w-4 inline-block mr-1" />
                      {conflict}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {alternatives?.length > 0 && (
              <div className="mb-4">
                <h3 className="font-semibold text-yellow-600 mb-2">Alternatives</h3>
                <ul className="space-y-1">
                  {alternatives.map((alternative, index) => (
                    <li key={index} className="text-yellow-500">
                      <InformationCircleIcon className="h-4 w-4 inline-block mr-1" />
                      {alternative}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {rationale && (
              <div className="text-gray-600">
                <h3 className="font-semibold mb-2">Rationale</h3>
                <p>{rationale}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default ResultsCard;
