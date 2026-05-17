import React, { useState, useEffect, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card } from '../../components/ui/Cards';
import { Skeleton } from '../../components/ui/Skeleton';
import { ChevronDown, ChevronUp, ChevronRight } from 'lucide-react';
import { Breadcrumb } from '../../components/ui/Breadcrumb';
import { contentService, DomainDTO, SubjectDTO } from '../../services/contentService';
import { progressService, SkillProgressDTO } from '../../services/progressService';
import type { SkillWithProgress } from '../../types';

const ACCENT_CYCLE: Array<'blue' | 'purple' | 'teal' | 'orange' | 'pink'> = ['blue', 'purple', 'teal', 'orange', 'pink'];

interface DomainEnriched extends DomainDTO {
  skills: SkillWithProgress[];
  masteredCount: number;
}

export const DomainsPage: React.FC = () => {
  const { subjectId } = useParams<{ subjectId: string }>();
  const [domains, setDomains] = useState<DomainDTO[]>([]);
  const [allSkills, setAllSkills] = useState<SkillWithProgress[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedDomain, setExpandedDomain] = useState<string | null>(null);
  const [subject, setSubject] = useState<SubjectDTO | null>(null);

  useEffect(() => {
    if (!subjectId) return;
    let cancelled = false;
    setExpandedDomain(null);
    setIsLoading(true);

    Promise.all([
      contentService.listDomains(subjectId),
      contentService.listSkills(subjectId).then(r => r.items),
      progressService.getSkillsProgress().catch(() => [] as SkillProgressDTO[]),
      contentService.getSubject(subjectId).catch(() => null),
    ]).then(([domainList, skillList, progressList, subjectData]) => {
      if (cancelled) return;
      setSubject(subjectData);
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
      setDomains(domainList);
      setAllSkills(merged);
    }).catch(() => {
      if (cancelled) return;
      setDomains([]);
      setAllSkills([]);
    }).finally(() => {
      if (!cancelled) setIsLoading(false);
    });
    return () => {
      cancelled = true;
    };
  }, [subjectId]);

  const enrichedDomains = useMemo<DomainEnriched[]>(() => {
    const byDomain = new Map<string, SkillWithProgress[]>();
    for (const sk of allSkills) {
      const list = byDomain.get(sk.domainId) || [];
      list.push(sk);
      byDomain.set(sk.domainId, list);
    }
    return domains.map(d => {
      const skills = (byDomain.get(d.id) || []).sort((a, b) => a.order - b.order);
      return {
        ...d,
        skills,
        masteredCount: skills.filter(s => s.score >= 90).length,
      };
    });
  }, [domains, allSkills]);

  const toggleExpand = (domainId: string) => {
    setExpandedDomain(prev => prev === domainId ? null : domainId);
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton variant="text" className="w-32 h-6" />
        <Skeleton variant="text" className="w-64 h-8" />
        {[1, 2, 3].map(i => <Skeleton key={i} variant="rect" className="h-32" />)}
      </div>
    );
  }

  const totalSkills = allSkills.length;
  const totalMastered = allSkills.filter(s => s.score >= 90).length;

  return (
    <div className="space-y-6">
      <header className="flex flex-col space-y-4">
        <Breadcrumb items={[
          { label: 'Mati\u00e8res', to: '/app/student/subjects' },
          { label: subject?.name || 'Domaines' },
        ]} />
        <div className="flex items-center justify-between flex-wrap gap-2">
          <h1 className="text-2xl md:text-3xl font-extrabold text-gray-900 font-display">{subject?.name || 'Domaines'}</h1>
          <div className="flex items-center space-x-2">
            <span className="text-sm font-bold bg-amber-50 text-amber-700 px-3 py-1 rounded-full">
              &#128221; {totalSkills} comp&eacute;tences
            </span>
            {totalMastered > 0 && (
              <span className="text-sm font-bold bg-green-50 text-green-700 px-3 py-1 rounded-full">
                &#11088; {totalMastered}/{totalSkills} ma&icirc;tris&eacute;es
              </span>
            )}
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 gap-4">
        {enrichedDomains.map((domain, index) => {
          const isOpen = expandedDomain === domain.id;
          const previewSkills = domain.skills.slice(0, 4);
          const remaining = domain.skills.length - previewSkills.length;
          const accent = ACCENT_CYCLE[index % ACCENT_CYCLE.length];

          return (
            <Card key={domain.id} className="p-0 overflow-hidden clay-card" accent={accent}>
              {/* Header row — click to expand/collapse */}
              <button
                type="button"
                onClick={() => toggleExpand(domain.id)}
                className="w-full text-left px-5 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-inset focus:ring-sitou-primary"
                aria-expanded={isOpen}
                aria-controls={`domain-skills-${domain.id}`}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center flex-wrap gap-2 mb-1">
                    <h3 className="text-lg font-bold text-gray-900 truncate font-display">{domain.name}</h3>
                    <span className="text-xs font-bold bg-amber-50 text-amber-600 px-2 py-0.5 rounded-full whitespace-nowrap">
                      {domain.skills.length} comp&eacute;tence{domain.skills.length !== 1 ? 's' : ''}
                    </span>
                    {domain.masteredCount > 0 && (
                      <span className="text-xs font-bold bg-green-50 text-green-600 px-2 py-0.5 rounded-full whitespace-nowrap">
                        {domain.masteredCount}/{domain.skills.length} &#10003;
                      </span>
                    )}
                  </div>
                  {/* Skill name preview (collapsed only) */}
                  {!isOpen && domain.skills.length > 0 && (
                    <p className="text-sm text-gray-500 truncate">
                      {previewSkills.map(s => s.name).join(' | ')}
                      {remaining > 0 && <span className="text-gray-400"> +{remaining}</span>}
                    </p>
                  )}
                </div>
                <span className="ml-3 flex-shrink-0 text-gray-400">
                  {isOpen ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                </span>
              </button>

              {/* Expanded skills — inline accordion */}
              {isOpen && (
                <div id={`domain-skills-${domain.id}`} className="border-t border-gray-100 px-5 py-3 animate-slide-down">
                  {domain.skills.length > 0 ? (
                    <div className="mt-1 space-y-2">
                      {domain.skills.map(skill => (
                        <Link
                          key={skill.id}
                          to={`/app/student/exercise/${skill.id}`}
                          state={{ returnPath: `/app/student/subjects/${subjectId}`, subjectId, subjectName: subject?.name }}
                          className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-amber-50 transition-colors"
                        >
                          <div className="flex items-center gap-2">
                            <div className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${skill.score >= 90 ? 'bg-green-500' : skill.score > 0 ? 'bg-orange-400' : 'bg-gray-300'}`} />
                            <span className="text-sm font-medium text-gray-700">{skill.name}</span>
                            {skill.score > 0 && (
                              <span className={`text-xs font-semibold ${skill.score >= 80 ? 'text-green-600' : skill.score >= 50 ? 'text-amber-500' : 'text-orange-400'}`}>
                                {skill.score}
                              </span>
                            )}
                          </div>
                          <ChevronRight size={16} className="text-gray-400 flex-shrink-0" />
                        </Link>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-400 py-2">Aucune comp&eacute;tence dans ce domaine.</p>
                  )}

                  {/* Footer — collapse + optional filtered view */}
                  <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
                    <button
                      type="button"
                      onClick={() => toggleExpand(domain.id)}
                      className="text-sm font-medium text-gray-500 hover:text-sitou-primary transition-colors"
                    >
                      R&eacute;duire
                    </button>
                    <Link
                      to={`/app/student/subjects/${subjectId}/domains/${domain.id}`}
                      className="text-xs text-gray-400 hover:text-sitou-primary transition-colors"
                    >
                      Vue filtr&eacute;e
                    </Link>
                  </div>
                </div>
              )}

              {/* Collapsed footer — expand prompt */}
              {!isOpen && domain.skills.length > 0 && (
                <div className="border-t border-gray-100 px-5 py-2.5">
                  <button
                    type="button"
                    onClick={() => toggleExpand(domain.id)}
                    className="text-sm font-medium text-sitou-primary hover:underline"
                  >
                    Voir les {domain.skills.length} comp&eacute;tences &rsaquo;
                  </button>
                </div>
              )}
            </Card>
          );
        })}

        {domains.length === 0 && (
          <div className="text-center py-12 bg-gradient-to-br from-amber-50 to-purple-50 rounded-3xl border border-dashed border-gray-300">
            <p className="text-gray-500 font-medium">Aucun domaine trouv&eacute; pour cette mati&egrave;re.</p>
          </div>
        )}
      </div>
    </div>
  );
};
