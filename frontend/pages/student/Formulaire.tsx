import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../../components/ui/Cards';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { ButtonVariant } from '../../types';
import { Search, BookOpen, Lightbulb, Play, ChevronDown, ChevronUp } from 'lucide-react';
import { contentService, FormulaDTO } from '../../services/contentService';

export const FormulairePage: React.FC = () => {
  const navigate = useNavigate();
  const [formulas, setFormulas] = useState<FormulaDTO[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  useEffect(() => {
    contentService.listFormulas()
      .then(setFormulas)
      .catch(() => setFormulas([]))
      .finally(() => setIsLoading(false));
  }, []);

  const filtered = useMemo(() => {
    if (!search.trim()) return formulas;
    const q = search.toLowerCase();
    return formulas.filter(f =>
      f.title.toLowerCase().includes(q) ||
      f.skillName.toLowerCase().includes(q) ||
      f.domainName.toLowerCase().includes(q) ||
      (f.formula && f.formula.toLowerCase().includes(q))
    );
  }, [formulas, search]);

  // Group by domain
  const grouped = useMemo(() => {
    const map = new Map<string, { domainName: string; subjectName: string; items: FormulaDTO[] }>();
    for (const f of filtered) {
      const key = f.domainId;
      if (!map.has(key)) {
        map.set(key, { domainName: f.domainName, subjectName: f.subjectName, items: [] });
      }
      map.get(key)!.items.push(f);
    }
    return Array.from(map.values());
  }, [filtered]);

  const toggleExpand = (id: string) => {
    setExpandedIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  if (isLoading) {
    return (
      <div className="space-y-6 p-4">
        <Skeleton variant="text" className="w-48 h-8" />
        <Skeleton variant="rect" className="h-12" />
        {[1, 2, 3, 4].map(i => <Skeleton key={i} variant="rect" className="h-24" />)}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 flex items-center font-display">
            <BookOpen size={24} className="mr-3 text-sitou-primary" />
            Formulaire
          </h1>
          <p className="text-gray-500 text-sm mt-1">
            Toutes les r&egrave;gles et formules &agrave; conna&icirc;tre pour le CEP
          </p>
        </div>
        <div className="relative w-full md:w-72">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Rechercher une r&egrave;gle..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2.5 bg-white border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-sitou-primary focus:border-transparent"
          />
        </div>
      </header>

      {/* Empty state */}
      {grouped.length === 0 && (
        <div className="text-center py-16 bg-gradient-to-br from-amber-50 to-purple-50 rounded-3xl border border-dashed border-gray-300">
          <Lightbulb size={48} className="text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 font-medium">
            {search ? 'Aucune r\u00e8gle trouv\u00e9e pour cette recherche.' : 'Aucune r\u00e8gle disponible pour le moment.'}
          </p>
          {search && (
            <Button variant={ButtonVariant.GHOST} onClick={() => setSearch('')} className="mt-2 text-sitou-primary">
              R&eacute;initialiser
            </Button>
          )}
        </div>
      )}

      {/* Grouped formulas */}
      {grouped.map(group => (
        <section key={group.domainName}>
          <h2 className="text-lg font-bold text-gray-800 mb-3 flex items-center">
            <span className="w-1.5 h-6 bg-sitou-primary rounded-full mr-3" />
            {group.domainName}
            <span className="text-xs text-gray-400 font-normal ml-2">({group.subjectName})</span>
          </h2>

          <div className="space-y-3">
            {group.items.map(formula => {
              const isExpanded = expandedIds.has(formula.id);
              const hasDetails = formula.retenons || formula.summary;

              return (
                <Card key={formula.id} className="bg-white border border-gray-100 hover:border-amber-200 transition-colors">
                  {/* Card header */}
                  <div
                    className={`flex items-start justify-between ${hasDetails ? 'cursor-pointer' : ''}`}
                    onClick={() => hasDetails && toggleExpand(formula.id)}
                  >
                    <div className="flex-1">
                      <h3 className="font-bold text-gray-900">{formula.title}</h3>
                      <p className="text-xs text-gray-400 mt-0.5">{formula.skillName}</p>

                      {formula.formula && (
                        <div className="mt-2 inline-block bg-yellow-50 border border-yellow-200 rounded-lg px-3 py-1.5">
                          <span className="font-mono text-sm text-yellow-900 font-semibold">
                            {formula.formula}
                          </span>
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-2 ml-3 flex-shrink-0">
                      <Button
                        size="sm"
                        variant={ButtonVariant.SECONDARY}
                        className="text-xs"
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/app/student/exercise/${formula.skillId}`, {
                            state: { returnPath: '/app/student/formulaire' },
                          });
                        }}
                      >
                        <Play size={14} className="mr-1" /> Pratiquer
                      </Button>
                      {hasDetails && (
                        isExpanded
                          ? <ChevronUp size={18} className="text-gray-400" />
                          : <ChevronDown size={18} className="text-gray-400" />
                      )}
                    </div>
                  </div>

                  {/* Expanded details */}
                  {isExpanded && hasDetails && (
                    <div className="mt-3 pt-3 border-t border-gray-100">
                      {formula.retenons && (
                        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 mb-3">
                          <h4 className="font-bold text-yellow-800 text-sm flex items-center mb-2">
                            <Lightbulb size={16} className="mr-2 text-yellow-600" /> Retenons
                          </h4>
                          <div
                            className="prose prose-sm max-w-none text-gray-700"
                            dangerouslySetInnerHTML={{ __html: formula.retenons.body_html }}
                          />
                          {formula.retenons.rules && formula.retenons.rules.length > 0 && (
                            <div className="mt-3 space-y-1.5">
                              {formula.retenons.rules.map((rule, idx) => (
                                <div key={idx} className="flex items-start space-x-2 bg-yellow-100 rounded-lg px-3 py-2">
                                  <Lightbulb size={14} className="text-yellow-600 mt-0.5 flex-shrink-0" />
                                  <span className="text-yellow-900 text-sm font-medium">{rule}</span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}

                      {formula.summary && !formula.retenons && (
                        <p className="text-gray-600 text-sm">{formula.summary}</p>
                      )}
                    </div>
                  )}
                </Card>
              );
            })}
          </div>
        </section>
      ))}
    </div>
  );
};
