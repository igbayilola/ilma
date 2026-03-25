import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card } from '../../components/ui/Cards';
import { Skeleton } from '../../components/ui/Skeleton';
import {
  teacherService,
  AssignmentResultDTO,
} from '../../services/teacherService';
import { ArrowLeft, ClipboardList } from 'lucide-react';

const scoreColor = (score: number): string => {
  if (score >= 70) return 'bg-green-100 text-green-700';
  if (score >= 40) return 'bg-orange-100 text-orange-700';
  return 'bg-red-100 text-red-700';
};

export const AssignmentResults: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [result, setResult] = useState<AssignmentResultDTO | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!id) return;
    teacherService
      .getAssignmentResults(id)
      .then(setResult)
      .catch((err) => setError(err?.message || 'Erreur de chargement.'))
      .finally(() => setIsLoading(false));
  }, [id]);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton variant="text" className="w-48 h-8" />
        <Skeleton variant="rect" className="h-24" />
        <Skeleton variant="rect" className="h-64" />
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="text-center py-20">
        <p className="text-gray-500 font-medium">
          {error || 'Résultats introuvables.'}
        </p>
        <button
          onClick={() => navigate(-1)}
          className="mt-4 text-ilma-primary font-bold hover:underline"
        >
          Retour
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <button
        onClick={() => navigate(-1)}
        className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 font-medium"
      >
        <ArrowLeft size={16} className="mr-1" />
        Retour
      </button>

      {/* Header */}
      <Card>
        <h1 className="text-2xl font-extrabold text-gray-900">
          {result.title}
        </h1>
        <div className="flex flex-wrap gap-4 mt-2 text-sm text-gray-500">
          {result.skill_name && (
            <span>
              Compétence : <strong>{result.skill_name}</strong>
            </span>
          )}
          {result.deadline && (
            <span>
              Échéance :{' '}
              <strong>
                {new Date(result.deadline).toLocaleDateString('fr-FR')}
              </strong>
            </span>
          )}
        </div>
      </Card>

      {/* Results Table */}
      {result.results.length === 0 ? (
        <Card className="text-center py-12">
          <ClipboardList size={48} className="mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500 font-medium">
            Aucun résultat pour le moment.
          </p>
        </Card>
      ) : (
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50">
                  <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase tracking-wide">
                    Élève
                  </th>
                  <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase tracking-wide text-center">
                    Meilleur score
                  </th>
                  <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase tracking-wide text-center">
                    Score moyen
                  </th>
                  <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase tracking-wide text-center">
                    Tentatives
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {result.results.map((r) => (
                  <tr key={r.profile_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium text-gray-800">
                      {r.display_name}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span
                        className={`inline-block px-3 py-1 rounded-full text-sm font-bold ${scoreColor(r.best_score)}`}
                      >
                        {r.best_score}%
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span
                        className={`inline-block px-3 py-1 rounded-full text-sm font-bold ${scoreColor(r.avg_score)}`}
                      >
                        {r.avg_score}%
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center text-gray-600 font-medium">
                      {r.attempts}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
