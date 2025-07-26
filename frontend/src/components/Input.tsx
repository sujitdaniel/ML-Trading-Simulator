"use client";
import React from 'react';

interface InputProps {
  label: string;
  type?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  required?: boolean;
  placeholder?: string;
  error?: string;
}

const Input: React.FC<InputProps> = ({ label, type = 'text', value, onChange, required, placeholder, error }) => (
  <div className="mb-4">
    <label className="block text-sm font-medium text-blue-200 mb-2">{label}</label>
    <input
      type={type}
      value={value}
      onChange={onChange}
      required={required}
      placeholder={placeholder}
      className={`w-full px-4 py-2 bg-white/10 border border-white/20 rounded-xl text-white placeholder-blue-300/60 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all duration-200 backdrop-blur-xl ${error ? 'border-red-400' : ''}`}
    />
    {error && <div className="text-red-400 text-xs mt-1">{error}</div>}
  </div>
);

export default Input; 