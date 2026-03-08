import { Lock } from 'lucide-react';

export const UnauthorizedPage = () => (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 text-center">
        <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mb-6">
            <Lock size={40} className="text-red-600" />
        </div>
        <h1 className="text-2xl font-extrabold text-gray-900 mb-2">Accès non autorisé</h1>
        <p className="text-gray-500">Tu n'as pas la permission d'accéder à cette page.</p>
    </div>
);
