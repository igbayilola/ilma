import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card } from '../../components/ui/Cards';
import { Skeleton } from '../../components/ui/Skeleton';
import { useAuthStore } from '../../store/authStore';
import {
  LayoutDashboard,
  BookOpen,
  FileQuestion,
  FileEdit,
  CheckCircle2,
  Eye,
  Archive,
  ArrowRight,
} from 'lucide-react';
import { contentService, KanbanQuestionDTO } from '../../services/contentService';

interface QuickStats {
  totalQuestions: number;
  draft: number;
  inReview: number;
  published: number;
  archived: number;
  totalSkills: number;
}

export const EditorDashboard: React.FC = () => {
  const { user } = useAuthStore();
  const [stats, setStats] = useState<QuickStats | null>(null);
  const [recentQuestions, setRecentQuestions] = useState<KanbanQuestionDTO[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      // Load kanban questions by status to derive stats
      const [draftQ, reviewQ, publishedQ, archivedQ] = await Promise.all([
        contentService.listQuestionsByStatus('DRAFT').catch(() => []),
        contentService.listQuestionsByStatus('IN_REVIEW').catch(() => []),
        contentService.listQuestionsByStatus('PUBLISHED', 50).catch(() => []),
        contentService.listQuestionsByStatus('ARCHIVED', 20).catch(() => []),
      ]);

      const allQuestions = [...draftQ, ...reviewQ, ...publishedQ, ...archivedQ];

      // Load tree for skill counts
      let totalSkills = 0;
      try {
        const tree = await contentService.getCurriculumTree();
        for (const grade of tree) {
          for (const subject of grade.subjects) {
            for (const domain of subject.domains) {
              totalSkills += domain.skills.length;
            }
          }
        }
      } catch {
        // Tree may fail; non-critical
      }

      setStats({
        totalQuestions: allQuestions.length,
        draft: draftQ.length,
        inReview: reviewQ.length,
        published: publishedQ.length,
        archived: archivedQ.length,
        totalSkills,
      });

      // Recent questions: sort by updatedAt descending, take 5
      const sorted = [...allQuestions].sort((a, b) =>
        (b.updatedAt || '').localeCompare(a.updatedAt || '')
      );
      setRecentQuestions(sorted.slice(0, 5));
    } catch (err) {
      console.error('Failed to load editor dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton variant="text" className="w-64 h-8" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => (
            <Skeleton key={i} variant="rect" className="h-24 rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Bienvenue, {user?.name || 'Editeur'}
        </h1>
        <p className="text-gray-500 mt-1">Tableau de bord de gestion de contenu</p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-500">Total questions</span>
            <FileQuestion size={20} className="text-ilma-primary" />
          </div>
          <p className="text-2xl font-bold">{stats?.totalQuestions ?? 0}</p>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-500">Brouillons</span>
            <FileEdit size={20} className="text-gray-500" />
          </div>
          <p className="text-2xl font-bold text-gray-600">{stats?.draft ?? 0}</p>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-500">En relecture</span>
            <Eye size={20} className="text-amber-500" />
          </div>
          <p className="text-2xl font-bold text-amber-600">{stats?.inReview ?? 0}</p>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-500">Publiees</span>
            <CheckCircle2 size={20} className="text-green-500" />
          </div>
          <p className="text-2xl font-bold text-green-600">{stats?.published ?? 0}</p>
        </Card>
      </div>

      {/* Secondary stats */}
      <div className="grid grid-cols-2 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-500">Competences</span>
            <BookOpen size={20} className="text-blue-500" />
          </div>
          <p className="text-2xl font-bold">{stats?.totalSkills ?? 0}</p>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-500">Archivees</span>
            <Archive size={20} className="text-gray-400" />
          </div>
          <p className="text-2xl font-bold text-gray-400">{stats?.archived ?? 0}</p>
        </Card>
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Link to="/app/editor/programme" className="block">
          <Card className="p-5 hover:shadow-lg transition-shadow cursor-pointer group">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-blue-50 rounded-xl">
                  <BookOpen size={24} className="text-blue-600" />
                </div>
                <div>
                  <h3 className="font-bold text-gray-900">Programme</h3>
                  <p className="text-sm text-gray-500">Arbre du curriculum</p>
                </div>
              </div>
              <ArrowRight size={20} className="text-gray-300 group-hover:text-ilma-primary transition-colors" />
            </div>
          </Card>
        </Link>
        <Link to="/app/editor/questions" className="block">
          <Card className="p-5 hover:shadow-lg transition-shadow cursor-pointer group">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-amber-50 rounded-xl">
                  <FileQuestion size={24} className="text-amber-600" />
                </div>
                <div>
                  <h3 className="font-bold text-gray-900">Questions</h3>
                  <p className="text-sm text-gray-500">Kanban editorial</p>
                </div>
              </div>
              <ArrowRight size={20} className="text-gray-300 group-hover:text-ilma-primary transition-colors" />
            </div>
          </Card>
        </Link>
      </div>

      {/* Recent Activity */}
      <div>
        <h2 className="text-lg font-bold text-gray-900 mb-4">Activite recente</h2>
        {recentQuestions.length === 0 ? (
          <Card className="p-6 text-center text-gray-400">
            Aucune question modifiee recemment.
          </Card>
        ) : (
          <div className="space-y-2">
            {recentQuestions.map(q => (
              <Card key={q.id} className="p-4 flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{q.text}</p>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {q.questionType || 'N/A'}
                  </p>
                </div>
                <span className={`text-xs font-bold px-2 py-1 rounded-full ${
                  q.status === 'DRAFT' ? 'bg-gray-100 text-gray-600' :
                  q.status === 'IN_REVIEW' ? 'bg-amber-100 text-amber-700' :
                  q.status === 'PUBLISHED' ? 'bg-green-100 text-green-700' :
                  'bg-gray-100 text-gray-400'
                }`}>
                  {q.status === 'DRAFT' ? 'Brouillon' :
                   q.status === 'IN_REVIEW' ? 'En relecture' :
                   q.status === 'PUBLISHED' ? 'Publiee' : 'Archivee'}
                </span>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
