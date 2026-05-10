import React, { useState, useEffect } from 'react';
import { Question } from '../../types';
import { Input } from '../ui/Input';
import { OptimizedImage } from '../ui/OptimizedImage';
import { MediaGallery } from './MediaGallery';
import { DragDropRenderer } from './DragDropRenderer';
import { ChartInputRenderer } from './ChartInputRenderer';
import { DrawCanvasRenderer } from './DrawCanvasRenderer';
import { AudioRenderer } from './AudioRenderer';
import { Check, X, GripVertical, ArrowUp, ArrowDown, Volume2 } from 'lucide-react';

interface QuestionRendererProps {
  question: Question;
  selectedAnswer: any;
  onAnswerChange: (answer: any) => void;
  isFeedbackMode: boolean;
  onHintRequested?: () => void;
}

export const QuestionRenderer: React.FC<QuestionRendererProps> = ({
  question,
  selectedAnswer,
  onAnswerChange,
  isFeedbackMode,
  onHintRequested,
}) => {

  // Progressive hints: track how many levels have been revealed (0 = none shown)
  const allHints = question.hints?.length ? question.hints : (question.hint ? [question.hint] : []);
  const totalHintLevels = allHints.length;
  const [revealedHints, setRevealedHints] = useState(0);

  useEffect(() => {
    setRevealedHints(0);
    // Initialize ORDERING with shuffled items
    if (question.type === 'ORDERING' && !selectedAnswer && question.choices) {
      const shuffled = [...(Array.isArray(question.choices) ? question.choices : [])].sort(() => Math.random() - 0.5);
      onAnswerChange(shuffled);
    }
  }, [question.id]);

  const handleSelect = (val: any) => {
    if (!isFeedbackMode) {
      onAnswerChange(val);
    }
  };

  const renderMCQ = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4" role="radiogroup" aria-label="Choix de réponse">
      {question.options?.map((option) => {
        const isSelected = selectedAnswer === option;
        const isCorrect = option === question.correctAnswer;

        let cardClass = "border-2 border-gray-200 bg-white hover:border-amber-300 hover:bg-amber-50";
        let icon = null;

        if (isSelected && !isFeedbackMode) {
          cardClass = "border-2 border-sitou-primary bg-amber-50 ring-2 ring-amber-200";
        }

        if (isFeedbackMode) {
           if (isCorrect) {
               cardClass = "border-sitou-green bg-green-50 text-green-800";
               icon = <Check className="text-sitou-green" />;
           } else if (isSelected && !isCorrect) {
               cardClass = "border-sitou-red bg-red-50 text-red-800";
               icon = <X className="text-sitou-red" />;
           } else {
               cardClass = "border-gray-100 opacity-50";
           }
        }

        return (
          <button
            key={option}
            onClick={() => handleSelect(option)}
            role="radio"
            aria-checked={isSelected}
            disabled={isFeedbackMode}
            className={`
              relative p-6 rounded-2xl cursor-pointer transition-all duration-200 flex items-center justify-between
              font-bold text-lg text-gray-700 text-left w-full focus:outline-none focus:ring-4 focus:ring-opacity-50 focus:ring-sitou-primary
              ${cardClass}
            `}
          >
            <span>{option}</span>
            {icon}
          </button>
        );
      })}
    </div>
  );

  const renderBoolean = () => (
    <div className="flex flex-col sm:flex-row gap-4">
      {[true, false].map((val) => {
        const label = val ? "Vrai" : "Faux";
        const isSelected = selectedAnswer === val;
        const isCorrect = val === question.correctAnswer;

        let btnClass = "bg-white border-2 border-gray-200 text-gray-600 hover:bg-gray-50";

        if (isSelected && !isFeedbackMode) {
          btnClass = "bg-sitou-primary text-white border-sitou-primary shadow-lg";
        }

        if (isFeedbackMode) {
            if (isCorrect) {
                btnClass = "bg-sitou-green text-white border-sitou-green";
            } else if (isSelected) {
                btnClass = "bg-sitou-red text-white border-sitou-red";
            } else {
                btnClass = "bg-gray-100 text-gray-300 border-gray-200";
            }
        }

        return (
          <button
            key={String(val)}
            onClick={() => handleSelect(val)}
            disabled={isFeedbackMode}
            className={`
              flex-1 py-8 rounded-2xl text-2xl font-bold transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-opacity-50 focus:ring-sitou-primary
              ${btnClass}
            `}
          >
            {label}
          </button>
        );
      })}
    </div>
  );

  const renderInput = () => {
      const isCorrect = String(selectedAnswer).trim().toLowerCase() === String(question.correctAnswer).trim().toLowerCase();

      return (
        <div className="max-w-md mx-auto">
            <Input
                placeholder="Tape ta réponse ici..."
                value={selectedAnswer || ''}
                onChange={(e) => handleSelect(e.target.value)}
                disabled={isFeedbackMode}
                className="text-center text-xl"
                style={isFeedbackMode ? {
                    borderColor: isCorrect ? '#22C55E' : '#DC2626',
                    backgroundColor: isCorrect ? '#F0FFF4' : '#FFF5F5',
                    color: isCorrect ? '#166534' : '#991B1B'
                } : {}}
            />
            {isFeedbackMode && !isCorrect && (
                <div className="mt-2 text-center text-gray-500" role="alert">
                    Réponse attendue : <span className="font-bold">{String(question.correctAnswer)}</span>
                </div>
            )}
        </div>
      );
  };

  const renderOrdering = () => {
    const items: string[] = selectedAnswer || question.choices || [];

    const moveItem = (fromIndex: number, direction: 'up' | 'down') => {
      if (isFeedbackMode) return;
      const toIndex = direction === 'up' ? fromIndex - 1 : fromIndex + 1;
      if (toIndex < 0 || toIndex >= items.length) return;
      const newItems = [...items];
      [newItems[fromIndex], newItems[toIndex]] = [newItems[toIndex], newItems[fromIndex]];
      handleSelect(newItems);
    };

    const correctOrder = question.correctAnswer as string[];

    return (
      <div className="max-w-md mx-auto space-y-2">
        {items.map((item: string, idx: number) => {
          const isCorrectPos = isFeedbackMode && correctOrder && item === correctOrder[idx];
          return (
            <div
              key={`${item}-${idx}`}
              className={`flex items-center p-4 rounded-xl border-2 transition-all ${
                isFeedbackMode
                  ? isCorrectPos ? 'border-green-300 bg-green-50' : 'border-red-300 bg-red-50'
                  : 'border-gray-200 bg-white hover:border-amber-200'
              }`}
            >
              <GripVertical size={18} className="text-gray-300 mr-3 flex-shrink-0" />
              <span className="flex-1 font-medium text-gray-800">{item}</span>
              {!isFeedbackMode && (
                <div className="flex flex-col ml-1">
                  <button onClick={() => moveItem(idx, 'up')} disabled={idx === 0} className="p-2.5 text-gray-400 hover:text-sitou-primary disabled:opacity-30 min-w-[44px] min-h-[44px] flex items-center justify-center" aria-label={`Monter ${item}`}>
                    <ArrowUp size={18} />
                  </button>
                  <button onClick={() => moveItem(idx, 'down')} disabled={idx === items.length - 1} className="p-2.5 text-gray-400 hover:text-sitou-primary disabled:opacity-30 min-w-[44px] min-h-[44px] flex items-center justify-center" aria-label={`Descendre ${item}`}>
                    <ArrowDown size={18} />
                  </button>
                </div>
              )}
              {isFeedbackMode && (isCorrectPos ? <Check size={18} className="text-green-600 ml-2" /> : <X size={18} className="text-red-500 ml-2" />)}
            </div>
          );
        })}
        {isFeedbackMode && (
          <p className="text-sm text-gray-500 mt-3">Ordre attendu : {(correctOrder || []).join(' → ')}</p>
        )}
      </div>
    );
  };

  const renderMatching = () => {
    const leftItems: string[] = question.choices?.left || [];
    const rightItems: string[] = question.choices?.right || [];
    const pairs: Record<string, string> = selectedAnswer || {};

    const handleMatch = (left: string, right: string) => {
      if (isFeedbackMode) return;
      handleSelect({ ...pairs, [left]: right });
    };

    return (
      <div className="max-w-lg mx-auto space-y-4">
        {leftItems.map((left) => (
          <div key={left} className="flex items-center gap-3">
            <div className="flex-1 p-3 rounded-xl bg-amber-50 border border-amber-100 font-medium text-gray-800 text-sm">
              {left}
            </div>
            <span className="text-gray-300">→</span>
            <div className="flex-1 relative">
              <select
                value={pairs[left] || ''}
                onChange={(e) => handleMatch(left, e.target.value)}
                disabled={isFeedbackMode}
                aria-label={`Associer : ${left}`}
                className={`w-full p-3 rounded-xl border-2 text-sm font-medium focus:ring-2 focus:ring-sitou-primary ${
                  isFeedbackMode
                    ? pairs[left] === (question.correctAnswer as any)?.[left]
                      ? 'border-green-300 bg-green-50'
                      : 'border-red-300 bg-red-50'
                    : 'border-gray-200 bg-white'
                }`}
              >
                <option value="">Choisir...</option>
                {rightItems.map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
              {isFeedbackMode && pairs[left] !== (question.correctAnswer as any)?.[left] && (
                <span className="text-xs text-red-600 mt-0.5 block">Attendu : {(question.correctAnswer as any)?.[left]}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderGuidedSteps = () => {
    const steps: Array<{ instruction: string; expected?: string }> = question.choices || [];
    const answers: string[] = selectedAnswer || steps.map(() => '');
    const correctAnswers: string[] = Array.isArray(question.correctAnswer) ? question.correctAnswer as string[] : [];

    const handleStepAnswer = (idx: number, val: string) => {
      if (isFeedbackMode) return;
      const newAnswers = [...answers];
      newAnswers[idx] = val;
      handleSelect(newAnswers);
    };

    return (
      <div className="max-w-md mx-auto space-y-4">
        {steps.map((step, idx) => {
          const stepCorrect = isFeedbackMode && correctAnswers[idx] !== undefined
            ? String(answers[idx] || '').trim().toLowerCase() === String(correctAnswers[idx]).trim().toLowerCase()
            : null;

          return (
            <div key={idx} className={`p-4 rounded-xl border-2 transition-all ${
              isFeedbackMode
                ? stepCorrect ? 'border-green-300 bg-green-50' : 'border-red-300 bg-red-50'
                : 'border-gray-200 bg-white'
            }`}>
              <div className="flex items-center mb-2">
                <span className="w-7 h-7 rounded-full bg-sitou-primary text-white flex items-center justify-center text-sm font-bold mr-3">{idx + 1}</span>
                <p className="text-sm font-medium text-gray-700">{step.instruction}</p>
              </div>
              <Input
                placeholder="Ta réponse..."
                value={answers[idx] || ''}
                onChange={(e) => handleStepAnswer(idx, e.target.value)}
                disabled={isFeedbackMode}
                className={`text-sm ${isFeedbackMode ? stepCorrect ? 'border-green-400 text-green-700' : 'border-red-400 text-red-700' : ''}`}
              />
              {isFeedbackMode && !stepCorrect && correctAnswers[idx] !== undefined && (
                <p className="text-xs text-red-600 mt-1">Réponse attendue : <b>{correctAnswers[idx]}</b></p>
              )}
            </div>
          );
        })}
      </div>
    );
  };

  // Fallback for types that use simple text input
  const renderTextInput = (placeholder: string) => {
    const isCorrect = String(selectedAnswer).trim().toLowerCase() === String(question.correctAnswer).trim().toLowerCase();
    return (
      <div className="max-w-md mx-auto">
        <Input
          placeholder={placeholder}
          value={selectedAnswer || ''}
          onChange={(e) => handleSelect(e.target.value)}
          disabled={isFeedbackMode}
          className="text-center text-xl"
          style={isFeedbackMode ? {
            borderColor: isCorrect ? '#22C55E' : '#DC2626',
            backgroundColor: isCorrect ? '#F0FFF4' : '#FFF5F5',
            color: isCorrect ? '#166534' : '#991B1B'
          } : {}}
        />
        {isFeedbackMode && !isCorrect && (
          <div className="mt-2 text-center text-gray-500" role="alert">
            Réponse attendue : <span className="font-bold">{String(question.correctAnswer)}</span>
          </div>
        )}
      </div>
    );
  };

  const renderByType = () => {
    switch (question.type) {
      case 'MCQ':
        return renderMCQ();
      case 'TRUE_FALSE':
        return renderBoolean();
      case 'FILL_BLANK':
        return renderInput();
      case 'NUMERIC_INPUT':
        return renderTextInput("Entre le nombre...");
      case 'SHORT_ANSWER':
        return renderTextInput("Écris ta réponse...");
      case 'ORDERING':
        return renderOrdering();
      case 'MATCHING':
        return renderMatching();
      case 'GUIDED_STEPS':
        return renderGuidedSteps();
      case 'ERROR_CORRECTION':
        return renderTextInput("Corrige l'erreur...");
      case 'CONTEXTUAL_PROBLEM':
        return renderTextInput("Ta réponse au problème...");
      case 'JUSTIFICATION':
        return renderTextInput("Explique ta réponse...");
      case 'TRACING':
        return renderTextInput("Résultat du tracé...");
      case 'DRAG_DROP':
        return (
          <DragDropRenderer
            config={question.interactiveConfig?.config}
            selectedAnswer={selectedAnswer}
            onAnswerChange={handleSelect}
            isFeedbackMode={isFeedbackMode}
            correctAnswer={question.correctAnswer}
          />
        );
      case 'INTERACTIVE_DRAW':
        return (
          <DrawCanvasRenderer
            config={question.interactiveConfig?.config}
            selectedAnswer={selectedAnswer}
            onAnswerChange={handleSelect}
            isFeedbackMode={isFeedbackMode}
          />
        );
      case 'CHART_INPUT':
        return (
          <ChartInputRenderer
            config={question.interactiveConfig?.config}
            selectedAnswer={selectedAnswer}
            onAnswerChange={handleSelect}
            isFeedbackMode={isFeedbackMode}
          />
        );
      case 'AUDIO_COMPREHENSION':
        return (
          <AudioRenderer
            config={question.interactiveConfig?.config}
            mediaReferences={question.mediaReferences}
            selectedAnswer={selectedAnswer}
            onAnswerChange={handleSelect}
            isFeedbackMode={isFeedbackMode}
          />
        );
      default:
        return renderInput();
    }
  };

  // Compute feedback text for screen readers
  const feedbackAnnouncement = isFeedbackMode
    ? ((): string => {
        if (question.type === 'MCQ' || question.type === 'TRUE_FALSE') {
          const isCorrect = selectedAnswer === question.correctAnswer;
          return isCorrect ? 'Bonne réponse !' : `Mauvaise réponse. La bonne réponse est : ${question.correctAnswer}`;
        }
        const isCorrect = String(selectedAnswer).trim().toLowerCase() === String(question.correctAnswer).trim().toLowerCase();
        return isCorrect ? 'Bonne réponse !' : `Mauvaise réponse. Réponse attendue : ${question.correctAnswer}`;
      })()
    : '';

  return (
    <div className="w-full">
      {/* Live region: announces feedback to screen readers */}
      <div aria-live="polite" aria-atomic="true" className="sr-only">
        {feedbackAnnouncement}
      </div>

      {question.imageUrl && (
        <div className="mb-6 flex justify-center">
          <OptimizedImage src={question.imageUrl} alt="Illustration de la question" className="rounded-2xl max-h-60 object-cover shadow-sm" loading="eager" />
        </div>
      )}

      {question.mediaReferences && question.mediaReferences.length > 0 && (
        <MediaGallery media={question.mediaReferences} />
      )}

      <div className="mb-8">
        <h2 className="text-xl md:text-2xl font-bold text-gray-800 text-center leading-relaxed">
          {question.prompt}
        </h2>
        <div className="flex justify-center mt-2">
          <button
            onClick={() => {
              const u = new SpeechSynthesisUtterance(question.prompt);
              u.lang = 'fr-FR';
              speechSynthesis.cancel();
              speechSynthesis.speak(u);
            }}
            className="inline-flex items-center gap-1 text-sm text-sitou-primary hover:text-sitou-primary-dark transition-colors p-1 rounded"
            aria-label="Lire la question à voix haute"
            title="Lire la question"
          >
            <Volume2 size={18} />
            <span className="text-xs font-medium">Écouter</span>
          </button>
        </div>
        {totalHintLevels > 0 && !isFeedbackMode && (
          <div className="flex justify-center mt-2">
            <button
              onClick={() => {
                if (revealedHints < totalHintLevels) {
                  if (onHintRequested) onHintRequested();
                  setRevealedHints(prev => prev + 1);
                } else {
                  setRevealedHints(0);
                }
              }}
              className="inline-flex items-center gap-1 text-sm text-amber-600 hover:text-amber-700 transition-colors"
              aria-label={revealedHints > 0 && revealedHints >= totalHintLevels ? "Masquer les indices" : "Voir un indice"}
            >
              {revealedHints > 0 && revealedHints >= totalHintLevels
                ? 'Masquer les indices'
                : revealedHints > 0
                  ? `Indice suivant (${revealedHints}/${totalHintLevels})`
                  : `Indice (${totalHintLevels} disponible${totalHintLevels > 1 ? 's' : ''})`}
            </button>
          </div>
        )}
        {revealedHints > 0 && (
          <div className="mt-2 space-y-2" aria-live="polite">
            {allHints.slice(0, revealedHints).map((h, i) => (
              <div key={i} className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-sm text-amber-800 animate-slide-down flex items-start gap-2">
                <span className="w-5 h-5 rounded-full bg-amber-200 text-amber-700 flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">{i + 1}</span>
                <span>{h}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {renderByType()}
    </div>
  );
};
