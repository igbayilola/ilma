import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Card } from '../../components/ui/Cards';
import { Button } from '../../components/ui/Button';
import { Drawer } from '../../components/ui/Drawer';
import { Skeleton } from '../../components/ui/Skeleton';
import { SkillItem } from '../../components/ilma/SkillItem';
import { ButtonVariant, type SkillWithProgress } from '../../types';
import { ArrowLeft, Filter, Search } from 'lucide-react';
import { contentService } from '../../services/contentService';
import { progressService, SkillProgressDTO } from '../../services/progressService';

type FilterType = 'all' | 'todo' | 'mastered';

export const SkillsPage: React.FC = () => {
  const { subjectId, domainId } = useParams();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const activeFilter = (searchParams.get('filter') || 'all') as FilterType;
  const setActiveFilter = (f: string) => {
    const params: Record<string, string> = { filter: f };
    const q = searchParams.get('q');
    if (q) params.q = q;
    setSearchParams(params, { replace: true });
  };
  const search = searchParams.get('q') || '';
  const setSearch = (q: string) => {
    const params: Record<string, string> = { filter: activeFilter };
    if (q) params.q = q;
    setSearchParams(params, { replace: true });
  };
  const [skills, setSkills] = useState<SkillWithProgress[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isFilterOpen, setIsFilterOpen] = useState(false);

  useEffect(() => {
    if (!subjectId || !domainId) return;
    Promise.all([
      contentService.listSkills(subjectId, domainId),
      progressService.getSkillsProgress().catch(() => [] as SkillProgressDTO[]),
    ]).then(([skillList, progressList]) => {
      const progressMap = new Map(progressList.map(p => [p.skillId, p]));
      const merged: SkillWithProgress[] = skillList.map(sk => {
        const prog = progressMap.get(sk.id);
        const score = prog?.score ?? 0;
        return {
          ...sk,
          score,
          status: score >= 90 ? 'mastered' : score > 0 ? 'started' : 'todo',
        };
      });
      setSkills(merged);
    }).catch(() => setSkills([]))
      .finally(() => setIsLoading(false));
  }, [subjectId, domainId]);

  const filteredSkills = skills.filter(skill => {
    if (search && !skill.name.toLowerCase().includes(search.toLowerCase())) return false;
    if (activeFilter === 'all') return true;
    if (activeFilter === 'mastered') return skill.score >= 90;
    if (activeFilter === 'todo') return skill.score < 90;
    return true;
  });

  const masteredCount = skills.filter(s => s.score >= 90).length;

  const FilterContent = () => (
    <div className="space-y-6">
      <div>
        <h4 className="font-bold text-gray-900 mb-3">État</h4>
        <div className="space-y-2">
          {(['all', 'todo', 'mastered'] as FilterType[]).map(f => (
            <label key={f} className="flex items-center space-x-3 cursor-pointer">
              <input type="radio" name="filter" checked={activeFilter === f} onChange={() => setActiveFilter(f)} className="w-5 h-5 text-ilma-primary focus:ring-ilma-primary border-gray-300" />
              <span className="text-gray-700">{f === 'all' ? 'Tout afficher' : f === 'todo' ? 'À travailler' : 'Maîtrisé (90+)'}</span>
            </label>
          ))}
        </div>
      </div>
    </div>
  );

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton variant="text" className="w-48 h-8" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
          {[1, 2, 3, 4, 5, 6].map(i => <Skeleton key={i} variant="rect" className="h-10" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full md:flex-row md:space-x-8">
      <aside className="hidden md:block w-64 flex-shrink-0">
         <div className="sticky top-24 space-y-6">
             <Link to={`/app/student/subjects/${subjectId}`} className="flex items-center text-sm font-bold text-gray-500 hover:text-ilma-primary mb-6">
                <ArrowLeft size={16} className="mr-1" /> Retour au domaine
             </Link>
             <Card className="clay-card"><FilterContent /></Card>
         </div>
      </aside>

      <div className="flex-1 space-y-6">
        <header className="flex flex-col space-y-4">
            <div className="md:hidden">
                <Link to={`/app/student/subjects/${subjectId}`} className="flex items-center text-sm font-bold text-gray-500 hover:text-ilma-primary">
                    <ArrowLeft size={16} className="mr-1" /> Retour
                </Link>
            </div>
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-center flex-wrap gap-2">
                  <h1 className="text-2xl font-extrabold text-gray-900 font-display">Comp&eacute;tences</h1>
                  <span className="text-xs font-medium bg-amber-50 text-amber-600 px-2 py-0.5 rounded-full">
                    {skills.length} compétence{skills.length !== 1 ? 's' : ''}
                  </span>
                  {masteredCount > 0 && (
                    <span className="text-xs font-medium bg-green-50 text-green-600 px-2 py-0.5 rounded-full">
                      {masteredCount} maîtrisée{masteredCount !== 1 ? 's' : ''}
                    </span>
                  )}
                </div>
                <div className="flex items-center space-x-2">
                    <div className="relative flex-1 md:w-64">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                        <input type="text" placeholder="Rechercher une compétence..." value={search} onChange={(e) => setSearch(e.target.value)} className="w-full pl-9 pr-4 py-2 bg-white border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-ilma-primary focus:border-transparent" />
                    </div>
                    <Button variant={ButtonVariant.SECONDARY} className="md:hidden px-3" onClick={() => setIsFilterOpen(true)}>
                        <Filter size={20} />
                    </Button>
                </div>
            </div>
        </header>

        {filteredSkills.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-1">
            {filteredSkills.map(skill => (
              <SkillItem
                key={skill.id}
                skill={skill}
                onClick={(id) => navigate(`/app/student/exercise/${id}`)}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-12 bg-gradient-to-br from-amber-50 to-purple-50 rounded-3xl border border-dashed border-gray-300">
            <p className="text-gray-500 font-medium">Aucune comp&eacute;tence trouv&eacute;e avec ces filtres.</p>
            <Button variant={ButtonVariant.GHOST} onClick={() => {setActiveFilter('all'); setSearch('')}} className="mt-2 text-ilma-primary">Réinitialiser</Button>
          </div>
        )}
      </div>

      <Drawer isOpen={isFilterOpen} onClose={() => setIsFilterOpen(false)} title="Filtrer les compétences">
          <FilterContent />
          <div className="mt-8"><Button fullWidth onClick={() => setIsFilterOpen(false)}>Voir les résultats</Button></div>
      </Drawer>
    </div>
  );
};
