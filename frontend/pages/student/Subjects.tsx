import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../../components/ui/Cards';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { ButtonVariant } from '../../types';
import {
  Calculator,
  Book,
  FlaskConical,
  Globe,
  BookOpen,
  ChevronRight,
  AlertCircle,
  GraduationCap,
} from 'lucide-react';
import { contentService, SubjectDTO } from '../../services/contentService';
import { useAuthStore } from '../../store/authStore';

const ICON_COMPONENTS: Record<string, React.ReactNode> = {
  Calculator: <Calculator size={32} />,
  Book: <Book size={32} />,
  FlaskConical: <FlaskConical size={32} />,
  Globe: <Globe size={32} />,
  BookOpen: <BookOpen size={32} />,
};

const ACCENT_MAP: Record<string, 'blue' | 'purple' | 'green' | 'orange'> = {
  math: 'blue',
  fr: 'purple',
  sci: 'green',
  geo: 'orange',
};

export const SubjectsPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, activeProfile } = useAuthStore();
  const gradeLevelId = activeProfile?.gradeLevelId || user?.gradeLevelId;
  const [subjects, setSubjects] = useState<SubjectDTO[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [retryToken, setRetryToken] = useState(0);

  useEffect(() => {
    if (!gradeLevelId) {
      setIsLoading(false);
      return;
    }
    let cancelled = false;
    setIsLoading(true);
    contentService
      .listSubjects(gradeLevelId)
      .then(data => {
        if (!cancelled) setSubjects(data);
      })
      .catch(() => {
        if (!cancelled) setSubjects([]);
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [gradeLevelId, retryToken]);

  const renderHeader = () => (
    <header>
      <h1 className="text-2xl md:text-3xl font-extrabold text-gray-900 mb-2 font-display">
        &#128214; Mati&egrave;res
      </h1>
      <p className="text-gray-500">
        Choisis une mati&egrave;re pour t'entra&icirc;ner. Tu vas y arriver !
      </p>
    </header>
  );

  if (!gradeLevelId) {
    return (
      <div className="space-y-6">
        {renderHeader()}
        <Card>
          <div className="text-center py-8 flex flex-col items-center">
            <div className="w-16 h-16 gradient-hero rounded-full flex items-center justify-center mb-4 text-white">
              <GraduationCap size={32} />
            </div>
            <h3 className="text-lg font-bold text-gray-800 mb-1 font-display">
              Choisis ta classe
            </h3>
            <p className="text-gray-500 mb-6">
              Pour voir tes mati&egrave;res, s&eacute;lectionne d'abord ta classe.
            </p>
            <Button onClick={() => navigate('/select-profile')}>
              Choisir ma classe
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton variant="text" className="w-48 h-8" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map(i => <Skeleton key={i} variant="rect" className="h-24" />)}
        </div>
      </div>
    );
  }

  if (subjects.length === 0) {
    return (
      <div className="space-y-6">
        {renderHeader()}
        <Card>
          <div className="text-center py-8 flex flex-col items-center">
            <div className="w-16 h-16 gradient-hero rounded-full flex items-center justify-center mb-4 text-white">
              <AlertCircle size={32} />
            </div>
            <h3 className="text-lg font-bold text-gray-800 mb-1 font-display">
              Mati&egrave;res indisponibles
            </h3>
            <p className="text-gray-500 mb-6">
              Aucune mati&egrave;re n'a pu &ecirc;tre charg&eacute;e. V&eacute;rifie ta connexion et r&eacute;essaie.
            </p>
            <Button
              variant={ButtonVariant.SECONDARY}
              onClick={() => setRetryToken(t => t + 1)}
            >
              R&eacute;essayer
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {renderHeader()}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {subjects.map((subject) => (
          <Card
            key={subject.id}
            interactive
            accent={ACCENT_MAP[subject.slug] || 'blue'}
            onClick={() => navigate(`/app/student/subjects/${subject.id}`)}
            className="flex items-center p-6 group clay-card"
          >
            <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mr-6 ${subject.color} ${subject.textColor} group-hover:scale-110 group-hover:shadow-md transition-all duration-300`}>
              {ICON_COMPONENTS[subject.iconName] || <BookOpen size={32} />}
            </div>

            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-bold text-gray-900 mb-1 font-display">{subject.emoji} {subject.name}</h3>
              <div className="flex items-center text-sm text-gray-500 mb-2">
                <span className="font-medium">{subject.description || 'Exercices et le\u00e7ons'}</span>
              </div>
            </div>

            <div className="ml-4">
              <Button
                variant={ButtonVariant.GHOST}
                className="rounded-full w-12 h-12 p-0 flex items-center justify-center bg-gray-50 group-hover:gradient-hero group-hover:text-white transition-all"
              >
                <ChevronRight size={24} />
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};
