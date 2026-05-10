import React, { useState, useRef } from 'react';
import { Play, Pause, RotateCcw, Volume2 } from 'lucide-react';

interface AudioRendererProps {
  config: any;
  mediaReferences?: Array<{ id: string; type: string; url: string; alt_text: string; duration_seconds?: number }>;
  selectedAnswer: any;
  onAnswerChange: (answer: any) => void;
  isFeedbackMode: boolean;
}

/**
 * Audio comprehension exercise renderer.
 * Plays an audio file and displays timestamped questions.
 */
export const AudioRenderer: React.FC<AudioRendererProps> = ({
  config,
  mediaReferences,
  selectedAnswer,
  onAnswerChange,
  isFeedbackMode,
}) => {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [replaysUsed, setReplaysUsed] = useState(0);

  const audioMedia = mediaReferences?.find(m => m.type === 'audio');
  const maxReplays = config?.max_replays ?? 3;
  const questions = config?.questions || [];
  const answers: Record<number, any> = selectedAnswer || {};

  const togglePlay = () => {
    const audio = audioRef.current;
    if (!audio) return;
    if (isPlaying) {
      audio.pause();
    } else {
      audio.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleReplay = () => {
    const audio = audioRef.current;
    if (!audio || replaysUsed >= maxReplays) return;
    audio.currentTime = 0;
    audio.play();
    setIsPlaying(true);
    setReplaysUsed(prev => prev + 1);
  };

  const handleQuestionAnswer = (qIndex: number, answer: any) => {
    if (isFeedbackMode) return;
    const newAnswers = { ...answers, [qIndex]: answer };
    onAnswerChange(newAnswers);
  };

  if (!audioMedia) {
    return <div className="text-gray-400 text-center p-4">Aucun fichier audio disponible pour cet exercice.</div>;
  }

  return (
    <div className="max-w-lg mx-auto space-y-4">
      {/* Audio player */}
      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-4 rounded-xl">
        <audio
          ref={audioRef}
          src={audioMedia.url}
          onTimeUpdate={() => setCurrentTime(audioRef.current?.currentTime || 0)}
          onEnded={() => setIsPlaying(false)}
          preload="metadata"
        />

        <div className="flex items-center gap-3">
          <button
            onClick={togglePlay}
            className="w-12 h-12 rounded-full bg-sitou-primary text-white flex items-center justify-center hover:bg-sitou-primary-dark transition-colors"
            aria-label={isPlaying ? 'Pause' : 'Lecture'}
          >
            {isPlaying ? <Pause size={20} /> : <Play size={20} className="ml-0.5" />}
          </button>

          <div className="flex-1">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-gray-500">
                {Math.floor(currentTime / 60)}:{String(Math.floor(currentTime % 60)).padStart(2, '0')}
                {audioMedia.duration_seconds && ` / ${Math.floor(audioMedia.duration_seconds / 60)}:${String(audioMedia.duration_seconds % 60).padStart(2, '0')}`}
              </span>
              <button
                onClick={handleReplay}
                disabled={replaysUsed >= maxReplays}
                className="flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800 disabled:text-gray-300 disabled:cursor-not-allowed"
                aria-label="Réécouter"
              >
                <RotateCcw size={12} />
                Réécouter ({maxReplays - replaysUsed} restantes)
              </button>
            </div>

            {/* Progress bar */}
            <div className="w-full bg-gray-200 h-1.5 rounded-full overflow-hidden">
              <div
                className="h-full bg-indigo-500 rounded-full transition-all"
                style={{ width: `${audioMedia.duration_seconds ? (currentTime / audioMedia.duration_seconds) * 100 : 0}%` }}
              />
            </div>
          </div>

          <Volume2 size={16} className="text-gray-400" />
        </div>
      </div>

      {/* Illustration if available */}
      {mediaReferences?.filter(m => m.type === 'image').map(img => (
        <div key={img.id} className="flex justify-center">
          <img src={img.url} alt={img.alt_text} loading="lazy" decoding="async" className="rounded-xl max-h-48 object-cover shadow-sm" />
        </div>
      ))}

      {/* Questions */}
      <div className="space-y-3">
        {questions.map((q: any, i: number) => (
          <div key={i} className="p-3 bg-white border border-gray-200 rounded-xl">
            <p className="text-sm font-medium text-gray-700 mb-2">{q.question}</p>

            {q.type === 'mcq' && (
              <div className="space-y-1.5">
                {(q.options || []).map((opt: string) => {
                  const isSelected = answers[i] === opt;
                  return (
                    <button
                      key={opt}
                      onClick={() => handleQuestionAnswer(i, opt)}
                      disabled={isFeedbackMode}
                      className={`w-full text-left px-3 py-2 rounded-lg text-sm border transition-all ${
                        isSelected ? 'border-sitou-primary bg-amber-50 font-bold' : 'border-gray-100 hover:border-amber-200'
                      }`}
                    >
                      {opt}
                    </button>
                  );
                })}
              </div>
            )}

            {q.type === 'multi_select' && (
              <div className="space-y-1.5">
                {(q.options || []).map((opt: string) => {
                  const selected: string[] = answers[i] || [];
                  const isSelected = selected.includes(opt);
                  return (
                    <button
                      key={opt}
                      onClick={() => {
                        if (isFeedbackMode) return;
                        const newSel = isSelected ? selected.filter(s => s !== opt) : [...selected, opt];
                        handleQuestionAnswer(i, newSel);
                      }}
                      disabled={isFeedbackMode}
                      className={`w-full text-left px-3 py-2 rounded-lg text-sm border transition-all ${
                        isSelected ? 'border-sitou-primary bg-amber-50 font-bold' : 'border-gray-100 hover:border-amber-200'
                      }`}
                    >
                      <span className={`inline-block w-4 h-4 rounded border mr-2 align-middle ${isSelected ? 'bg-sitou-primary border-sitou-primary' : 'border-gray-300'}`} />
                      {opt}
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
