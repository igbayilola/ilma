import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../../components/ui/Cards';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { ButtonVariant } from '../../types';
import { Calculator, Book, FlaskConical, Globe, BookOpen, ChevronRight } from 'lucide-react';
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

  useEffect(() => {
    contentService.listSubjects(gradeLevelId)
      .then(setSubjects)
      .catch(() => setSubjects([]))
      .finally(() => setIsLoading(false));
  }, [gradeLevelId]);

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

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl md:text-3xl font-extrabold text-gray-900 mb-2 font-display">&#128214; Mati&egrave;res</h1>
        <p className="text-gray-500">Choisis une mati&egrave;re pour t'entra&icirc;ner. Tu vas y arriver !</p>
      </header>

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
