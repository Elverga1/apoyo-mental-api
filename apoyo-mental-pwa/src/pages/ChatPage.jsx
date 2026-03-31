// src/pages/ChatPage.jsx
import React from 'react';
import { ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import ChatInterface from '../components/chat/ChatInterface';

export const ChatPage = () => {
  return (
    <div className="h-screen flex flex-col">
      <div className="bg-blue-600 text-white p-4">
        <div className="flex items-center gap-4">
          <Link to="/" className="p-1 hover:bg-white/20 rounded-full">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <h1 className="font-semibold">Chat de Apoyo</h1>
        </div>
      </div>
      <ChatInterface />
    </div>
  );
};