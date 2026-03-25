import React from 'react';
import type { SkillWithProgress } from '../../types';

interface SkillItemProps {
  skill: SkillWithProgress;
  onClick: (skillId: string) => void;
}

function dotColor(score: number): string {
  if (score >= 90) return 'bg-green-500 shadow-sm shadow-green-300';
  if (score > 0) return 'bg-orange-400 shadow-sm shadow-amber-200';
  return 'bg-gray-300';
}

function scoreColor(score: number): string {
  if (score >= 80) return 'text-green-600';
  if (score >= 50) return 'text-amber-500';
  if (score > 0) return 'text-orange-400';
  return 'text-gray-400';
}

export const SkillItem: React.FC<SkillItemProps> = ({ skill, onClick }) => {
  const label = skill.score > 0
    ? `${skill.name} \u2014 score ${skill.score}`
    : skill.name;

  return (
    <button
      type="button"
      onClick={() => onClick(skill.id)}
      aria-label={label}
      className="flex items-start w-full text-left px-3 py-2.5 rounded-xl hover:bg-amber-50 hover:text-amber-700 hover:translate-x-0.5 transition-all group focus:outline-none focus:ring-2 focus:ring-sitou-primary focus:ring-offset-1"
    >
      <span className={`w-2.5 h-2.5 mt-1.5 rounded-full flex-shrink-0 ${dotColor(skill.score)}`} aria-hidden="true" />
      <span className="ml-2.5 flex-1 text-sm text-gray-700 group-hover:text-amber-700">
        {skill.name}
      </span>
      {skill.score > 0 && (
        <span className={`ml-2 text-xs font-semibold flex-shrink-0 ${scoreColor(skill.score)} group-hover:text-amber-600`}>
          {skill.score}
        </span>
      )}
    </button>
  );
};
