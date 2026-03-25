import React, { useState, useEffect } from 'react';
import { Tabs } from '../../components/ui/Tabs';
import { Card, Badge } from '../../components/ui/Cards';
import { SmartScoreMeter } from '../../components/ilma/Gamification';
import { AlertCircle, ChevronDown, ChevronUp, Target } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { ButtonVariant } from '../../types';
import { useNavigate } from 'react-router-dom';
import { contentService, SubjectDTO } from '../../services/contentService';
import { progressService, SkillProgressDTO, MicroSkillProgressDTO } from '../../services/progressService';

function getAccentForScore(score: number): 'green' | 'blue' | 'orange' {
  if (score >= 80) return 'green';
  if (score >= 50) return 'blue';
  return 'orange';
}

export const ProgressPage: React.FC = () => {
  const [subjects, setSubjects] = useState<SubjectDTO[]>([]);
  const [activeTab, setActiveTab] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [skillProgress, setSkillProgress] = useState<SkillProgressDTO[]>([]);
  const [expandedSkillId, setExpandedSkillId] = useState<string | null>(null);
  const [microProgress, setMicroProgress] = useState<MicroSkillProgressDTO[]>([]);
  const [microLoading, setMicroLoading] = useState(false);
  const navigate = useNavigate();

  // Load subjects for tabs
  useEffect(() => {
    contentService.listSubjects()
      .then(subs => {
        setSubjects(subs);
        if (subs.length > 0) setActiveTab(subs[0].id);
      })
      .catch(() => setSubjects([]));
  }, []);

  // Load progress
  useEffect(() => {
    progressService.getSkillsProgress()
      .then(setSkillProgress)
      .catch(() => setSkillProgress([]))
      .finally(() => setIsLoading(false));
  }, []);

  const handleToggleMicroSkills = async (skillId: string) => {
    if (expandedSkillId === skillId) {
      setExpandedSkillId(null);
      setMicroProgress([]);
      return;
    }
    setExpandedSkillId(skillId);
    setMicroLoading(true);
    try {
      const data = await progressService.getMicroSkillsProgress(skillId);
      setMicroProgress(data);
    } catch {
      setMicroProgress([]);
    } finally {
      setMicroLoading(false);
    }
  };

  const subjectTabs = subjects.map(s => ({ id: s.id, label: s.name }));

  // For now, show all skill progress (filtering by subject would require skill->subject mapping)
  const items = skillProgress;

  const EmptyState = () => (
    <div className="text-center py-12 flex flex-col items-center">
      <div className="w-16 h-16 gradient-hero rounded-full flex items-center justify-center mb-4 text-white animate-float">
        <AlertCircle size={32} />
      </div>
      <h3 className="text-lg font-bold text-gray-800 mb-1 font-display">Aucune donn&eacute;e</h3>
      <p className="text-gray-500 mb-6">Tu n'as pas encore fait d'exercices.</p>
      <Button variant={ButtonVariant.SECONDARY} onClick={() => navigate('/app/student/subjects')}>
        Explorer les mati&egrave;res
      </Button>
    </div>
  );

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl md:text-3xl font-extrabold text-gray-900 mb-2 font-display">Ma Progression</h1>
        <p className="text-gray-500">Suis tes scores et identifie tes points forts.</p>
      </header>

      {subjectTabs.length > 0 && (
        <Tabs tabs={subjectTabs} activeTab={activeTab} onChange={setActiveTab} />
      )}

      {isLoading ? (
        <div className="space-y-4">
           {[1, 2, 3].map(i => <div key={i} className="h-24 bg-gray-100 rounded-3xl animate-pulse" />)}
        </div>
      ) : (
        <div className="space-y-4">
           {items.length === 0 ? <EmptyState /> : items.map((item) => (
             <div key={item.skillId}>
               <Card
                 className="flex items-center p-4 md:p-6 clay-card cursor-pointer"
                 accent={getAccentForScore(item.score)}
                 onClick={() => handleToggleMicroSkills(item.skillId)}
               >
                 <div className="mr-4 md:mr-6 flex-shrink-0">
                   <SmartScoreMeter score={item.score} />
                 </div>

                 <div className="flex-1 min-w-0 mr-4">
                   <h3 className="text-base md:text-lg font-bold text-gray-900 truncate">{item.skillName}</h3>
                   <div className="flex items-center text-xs text-gray-500 mt-1 space-x-3">
                     {item.lastPlayedAt && <span>Dernier essai : {new Date(item.lastPlayedAt).toLocaleDateString('fr-FR')}</span>}
                     <span className="font-medium">{item.totalAttempts} tentative(s)</span>
                   </div>
                 </div>

                 <div className="hidden md:block mr-3">
                    <Badge
                      label={item.score >= 80 ? 'Ma\u00eetris\u00e9' : item.score >= 50 ? 'En cours' : '\u00c0 revoir'}
                      color={item.score >= 80 ? 'green' : item.score >= 50 ? 'blue' : 'orange'}
                    />
                 </div>

                 <div className="md:hidden mr-3">
                     <div className={`w-3 h-3 rounded-full ${item.score >= 80 ? 'bg-sitou-green' : item.score >= 50 ? 'bg-sitou-primary' : 'bg-sitou-orange'}`} />
                 </div>

                 <div className="flex-shrink-0 text-gray-400">
                   {expandedSkillId === item.skillId ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                 </div>
               </Card>

               {/* Micro-skill breakdown */}
               {expandedSkillId === item.skillId && (
                 <div className="ml-4 md:ml-8 mt-2 space-y-2 animate-fade-in">
                   {microLoading ? (
                     <div className="py-4 text-center text-sm text-gray-400">Chargement...</div>
                   ) : microProgress.length === 0 ? (
                     <div className="py-4 text-center text-sm text-gray-400">Aucune micro-comp&eacute;tence trouv&eacute;e.</div>
                   ) : microProgress.map((ms) => (
                     <div
                       key={ms.microSkillId}
                       className="flex items-center p-3 bg-white border border-gray-100 rounded-2xl shadow-sm hover:shadow-md transition-shadow"
                     >
                       <div className="mr-3 flex-shrink-0">
                         <div className="w-10 h-10 rounded-xl flex items-center justify-center text-sm font-bold"
                           style={{
                             background: ms.smartScore >= 80 ? '#dcfce7' : ms.smartScore >= 50 ? '#dbeafe' : '#fff7ed',
                             color: ms.smartScore >= 80 ? '#16a34a' : ms.smartScore >= 50 ? '#2563eb' : '#ea580c',
                           }}
                         >
                           {Math.round(ms.smartScore)}
                         </div>
                       </div>

                       <div className="flex-1 min-w-0 mr-3">
                         <p className="text-sm font-semibold text-gray-800 truncate">{ms.microSkillName}</p>
                         <p className="text-xs text-gray-400">
                           {ms.totalAttempts} tentative(s)
                           {ms.difficultyIndex ? ` \u00b7 Difficult\u00e9 ${ms.difficultyIndex}/10` : ''}
                         </p>
                       </div>

                       <Button
                         size="sm"
                         variant={ButtonVariant.SECONDARY}
                         onClick={(e: React.MouseEvent) => {
                           e.stopPropagation();
                           navigate(`/app/student/exercise/${item.skillId}?micro_skill_id=${ms.microSkillId}`);
                         }}
                         className="flex-shrink-0"
                       >
                         <Target size={14} className="mr-1" />
                         Pratiquer
                       </Button>
                     </div>
                   ))}
                 </div>
               )}
             </div>
           ))}
        </div>
      )}
    </div>
  );
};
