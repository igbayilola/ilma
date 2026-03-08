import React from 'react';
import { Link } from 'react-router-dom';

interface AuthLayoutProps {
  children: React.ReactNode;
  title: string;
  subtitle?: string;
  backLink?: string;
}

export const AuthLayout: React.FC<AuthLayoutProps> = ({ children, title, subtitle, backLink }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50 bg-pattern-dots-warm flex flex-col justify-center items-center p-4 md:p-8">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
            <Link to="/" className="inline-block">
                <div className="w-12 h-12 gradient-hero rounded-xl flex items-center justify-center text-white font-bold text-2xl shadow-lg mx-auto mb-4">
                I
                </div>
            </Link>
          <h1 className="text-2xl font-extrabold text-gray-900 font-display">{title}</h1>
          {subtitle && <p className="text-gray-500 mt-2">{subtitle}</p>}
        </div>

        <div className="bg-white rounded-3xl shadow-clay p-6 md:p-8 border border-ilma-border clay-card">
          {children}
        </div>

        {backLink && (
           <div className="text-center mt-6">
                <Link to={backLink} className="text-sm font-bold text-gray-400 hover:text-gray-600 transition-colors">
                    &larr; Retour
                </Link>
           </div>
        )}
      </div>
    </div>
  );
};
