import React from 'react';
import AuthForm from '../../components/AuthForm';

const LoginPage: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      <div className="backdrop-blur-xl bg-white/10 rounded-2xl border border-white/20 shadow-2xl p-8 max-w-md w-full">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">Login to Algonex</h1>
          <p className="text-blue-200 text-sm">Welcome back! Please sign in to your account.</p>
        </div>
        <AuthForm />
      </div>
    </div>
  );
};

export default LoginPage; 