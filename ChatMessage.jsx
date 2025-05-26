import React from 'react';
import { motion } from 'framer-motion';
import {
  CheckCircleIcon,
  XCircleIcon,
  InformationCircleIcon,
  ChatBubbleLeftRightIcon,
} from '@heroicons/react/24/outline';

const icons = {
  user: ChatBubbleLeftRightIcon,
  bot: ChatBubbleLeftRightIcon,
  suggested: CheckCircleIcon,
  conflict: XCircleIcon,
  alternative: InformationCircleIcon,
};

const statusColors = {
  user: 'bg-blue-100 text-blue-800',
  bot: 'bg-gray-100 text-gray-800',
  suggested: 'bg-green-100 text-green-800',
  conflict: 'bg-red-100 text-red-800',
  alternative: 'bg-yellow-100 text-yellow-800',
};

const ChatMessage = ({ type, content, time, status }) => {
  const Icon = icons[type];
  const isUser = type === 'user';
  const isBot = type === 'bot';
  const isResult = type !== 'user' && type !== 'bot';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`mb-4 flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-blue-100 text-blue-800'
            : isBot
            ? 'bg-gray-100 text-gray-800'
            : statusColors[type]
        } relative`}
      >
        {isResult && (
          <Icon className="h-5 w-5 absolute -left-2 top-1/2 transform -translate-y-1/2" />
        )}
        <div className="flex flex-col space-y-1">
          {isResult && (
            <span className="text-sm font-medium">
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </span>
          )}
          <p className="text-sm">{content}</p>
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>{time}</span>
            {isResult && <span>{status}</span>}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default ChatMessage;
