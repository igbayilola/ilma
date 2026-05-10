import React, { useState } from 'react';
import { Card } from '../ui/Cards';
import { LessonDTO, LessonSections } from '../../services/contentService';
import { BookOpen, Lightbulb, PenTool, ClipboardCheck, ChevronDown, ChevronUp } from 'lucide-react';

interface SectionConfig {
  key: keyof LessonSections;
  label: string;
  icon: React.ReactNode;
  bgClass: string;
  borderClass: string;
  iconBgClass: string;
  stepNumber: number;
}

const SECTION_CONFIG: SectionConfig[] = [
  {
    key: 'activite_depart',
    label: 'Activit\u00e9 de d\u00e9part',
    icon: <BookOpen size={20} />,
    bgClass: 'bg-blue-50',
    borderClass: 'border-blue-200',
    iconBgClass: 'bg-blue-100 text-blue-600',
    stepNumber: 1,
  },
  {
    key: 'retenons',
    label: 'Retenons',
    icon: <Lightbulb size={20} />,
    bgClass: 'bg-yellow-50',
    borderClass: 'border-yellow-300',
    iconBgClass: 'bg-yellow-100 text-yellow-700',
    stepNumber: 2,
  },
  {
    key: 'exemples',
    label: 'Exemples',
    icon: <PenTool size={20} />,
    bgClass: 'bg-green-50',
    borderClass: 'border-green-200',
    iconBgClass: 'bg-green-100 text-green-600',
    stepNumber: 3,
  },
  {
    key: 'evaluation_note',
    label: '\u00c9valuation',
    icon: <ClipboardCheck size={20} />,
    bgClass: 'bg-purple-50',
    borderClass: 'border-purple-200',
    iconBgClass: 'bg-purple-100 text-purple-600',
    stepNumber: 4,
  },
];

interface LessonRendererProps {
  lesson: LessonDTO;
}

export const LessonRenderer: React.FC<LessonRendererProps> = ({ lesson }) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(SECTION_CONFIG.map(s => s.key))
  );

  const toggleSection = (key: string) => {
    setExpandedSections(prev => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  // If lesson has structured sections, render 4-step view
  if (lesson.sections) {
    const sections = lesson.sections as LessonSections;

    return (
      <div className="space-y-4">
        {SECTION_CONFIG.map(config => {
          const section = sections[config.key];
          if (!section) return null;

          const isExpanded = expandedSections.has(config.key);
          const isRetenons = config.key === 'retenons';

          return (
            <Card
              key={config.key}
              className={`${config.bgClass} ${config.borderClass} border-2 overflow-hidden ${isRetenons ? 'ring-2 ring-yellow-300 shadow-md' : ''}`}
            >
              <button
                onClick={() => toggleSection(config.key)}
                className="w-full flex items-center justify-between p-4"
              >
                <div className="flex items-center space-x-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${config.iconBgClass}`}>
                    {config.stepNumber}
                  </div>
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${config.iconBgClass}`}>
                    {config.icon}
                  </div>
                  <span className="font-bold text-gray-900 text-lg">
                    {section.title || config.label}
                  </span>
                </div>
                {isExpanded
                  ? <ChevronUp size={20} className="text-gray-400" />
                  : <ChevronDown size={20} className="text-gray-400" />
                }
              </button>

              {isExpanded && (
                <div className="px-4 pb-4">
                  <div
                    className="prose prose-blue max-w-none text-gray-700 leading-relaxed"
                    dangerouslySetInnerHTML={{ __html: section.body_html }}
                  />

                  {isRetenons && section.rules && section.rules.length > 0 && (
                    <div className="mt-4 space-y-2">
                      {section.rules.map((rule, idx) => (
                        <div
                          key={idx}
                          className="flex items-start space-x-2 bg-yellow-100 border border-yellow-200 rounded-xl px-4 py-3"
                        >
                          <Lightbulb size={16} className="text-yellow-600 mt-0.5 flex-shrink-0" />
                          <span className="text-yellow-900 font-semibold text-sm">{rule}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </Card>
          );
        })}
      </div>
    );
  }

  // Fallback: render content_html as before (legacy lessons)
  const paragraphs = lesson.contentHtml
    ? lesson.contentHtml.split(/<\/p>|<br\s*\/?>|\n/).filter(Boolean).map(p => p.replace(/<[^>]+>/g, '').trim()).filter(Boolean)
    : ['Contenu de la le\u00e7on'];

  return (
    <div className="prose prose-blue max-w-none mb-8 text-gray-700 leading-relaxed text-lg">
      {paragraphs.map((paragraph, idx) => (
        <p key={idx} className="mb-4">{paragraph}</p>
      ))}
    </div>
  );
};
