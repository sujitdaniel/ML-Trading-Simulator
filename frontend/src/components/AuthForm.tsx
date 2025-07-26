"use client";
import React, { useState } from 'react';
import Input from './Input';
import { useRouter } from 'next/navigation';

const AuthForm: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const validateEmail = (email: string) => /\S+@\S+\.\S+/.test(email);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!validateEmail(email)) {
      setError('Please enter a valid email address.');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }
    setIsLoading(true);
    try {
      const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, rememberMe })
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || 'Login failed.');
      }
      const { token } = await res.json();
      if (rememberMe) {
        localStorage.setItem('algonex_token', token);
      } else {
        sessionStorage.setItem('algonex_token', token);
      }
      router.push('/');
    } catch (err: any) {
      setError(err.message || 'Login failed.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Email"
        type="email"
        value={email}
        onChange={e => setEmail(e.target.value)}
        required
        placeholder="you@example.com"
        error={error && !validateEmail(email) ? error : undefined}
      />
      <Input
        label="Password"
        type="password"
        value={password}
        onChange={e => setPassword(e.target.value)}
        required
        placeholder="••••••••"
        error={error && password.length < 6 ? error : undefined}
      />
      <div className="flex items-center justify-between">
        <label className="flex items-center text-blue-200 text-sm">
          <input
            type="checkbox"
            checked={rememberMe}
            onChange={e => setRememberMe(e.target.checked)}
            className="mr-2 accent-blue-500"
          />
          Remember Me
        </label>
        <a href="#" className="text-blue-400 hover:underline text-sm">Forgot Password?</a>
      </div>
      {error && (
        <div className="bg-red-500/20 border border-red-400/30 rounded-xl text-red-200 text-sm p-2">
          {error}
        </div>
      )}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full px-4 py-2 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 disabled:from-gray-500 disabled:to-gray-600 text-white font-semibold rounded-xl transition-all duration-200 shadow-lg flex items-center justify-center"
      >
        {isLoading ? (
          <svg className="animate-spin h-5 w-5 mr-2 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        ) : null}
        {isLoading ? 'Logging in...' : 'Login'}
      </button>
      <div className="text-center mt-2">
        <span className="text-blue-200 text-sm">Don&apos;t have an account? </span>
        <a href="#" className="text-blue-400 hover:underline text-sm">Create Account</a>
      </div>
    </form>
  );
};

export default AuthForm; 