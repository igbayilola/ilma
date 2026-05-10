import React, { useState } from 'react';
import { Check, X, GripVertical } from 'lucide-react';

interface DragDropRendererProps {
  config: any;
  selectedAnswer: any;
  onAnswerChange: (answer: any) => void;
  isFeedbackMode: boolean;
  correctAnswer?: any;
}

/**
 * Drag-and-drop exercise renderer.
 * Supports two layouts:
 * - two_columns: drag items from left to drop zones on right (conversions, matching)
 * - reorder: reorder a list of items
 */
export const DragDropRenderer: React.FC<DragDropRendererProps> = ({
  config,
  selectedAnswer,
  onAnswerChange,
  isFeedbackMode,
  correctAnswer,
}) => {
  const layout = config?.layout || 'two_columns';

  if (layout === 'two_columns') {
    return (
      <TwoColumnDragDrop
        config={config}
        selectedAnswer={selectedAnswer}
        onAnswerChange={onAnswerChange}
        isFeedbackMode={isFeedbackMode}
        correctAnswer={correctAnswer}
      />
    );
  }

  return <div className="text-gray-400 text-center p-4">Type de drag-drop non supporté: {layout}</div>;
};

const TwoColumnDragDrop: React.FC<DragDropRendererProps> = ({
  config,
  selectedAnswer,
  onAnswerChange,
  isFeedbackMode,
  correctAnswer,
}) => {
  const leftItems = config?.left_column?.items || [];
  const dropZones = config?.right_column?.drop_zones || [];
  const assignments: Record<string, string> = selectedAnswer || {};
  const [draggedItem, setDraggedItem] = useState<string | null>(null);

  const handleDrop = (zoneId: string) => {
    if (isFeedbackMode || !draggedItem) return;
    const newAssignments = { ...assignments, [draggedItem]: zoneId };
    onAnswerChange(newAssignments);
    setDraggedItem(null);
  };

  const handleRemove = (itemId: string) => {
    if (isFeedbackMode) return;
    const newAssignments = { ...assignments };
    delete newAssignments[itemId];
    onAnswerChange(newAssignments);
  };

  const isCorrect = (itemId: string) => {
    const zone = dropZones.find((z: any) => z.accepts === itemId);
    return zone && assignments[itemId] === zone.id;
  };

  // Items not yet placed
  const unplaced = leftItems.filter((item: any) => !assignments[item.id]);

  return (
    <div className="max-w-lg mx-auto space-y-4">
      {/* Source items */}
      {unplaced.length > 0 && (
        <div className="flex flex-wrap gap-2 p-3 bg-gray-50 rounded-xl min-h-[48px]" aria-label="Éléments à placer">
          {unplaced.map((item: any) => (
            <button
              key={item.id}
              draggable
              onDragStart={() => setDraggedItem(item.id)}
              onClick={() => setDraggedItem(draggedItem === item.id ? null : item.id)}
              className={`px-4 py-2 rounded-lg font-medium text-sm border-2 transition-all cursor-grab active:cursor-grabbing ${
                draggedItem === item.id
                  ? 'border-sitou-primary bg-amber-50 ring-2 ring-amber-200 scale-105'
                  : 'border-gray-200 bg-white hover:border-amber-300'
              }`}
              aria-label={`Élément : ${item.label}`}
            >
              <GripVertical size={14} className="inline mr-1 text-gray-300" />
              {item.label}
            </button>
          ))}
        </div>
      )}

      {draggedItem && !isFeedbackMode && (
        <p className="text-xs text-amber-600 text-center">Clique sur une zone ci-dessous pour placer « {leftItems.find((i: any) => i.id === draggedItem)?.label} »</p>
      )}

      {/* Drop zones */}
      <div className="space-y-2">
        {dropZones.map((zone: any) => {
          const placedItem = leftItems.find((item: any) => assignments[item.id] === zone.id);
          const correct = isFeedbackMode && placedItem && isCorrect(placedItem.id);
          const wrong = isFeedbackMode && placedItem && !isCorrect(placedItem.id);

          return (
            <div
              key={zone.id}
              onClick={() => handleDrop(zone.id)}
              onDragOver={(e) => e.preventDefault()}
              onDrop={() => handleDrop(zone.id)}
              className={`flex items-center gap-3 p-3 rounded-xl border-2 min-h-[52px] transition-all ${
                correct ? 'border-green-300 bg-green-50' :
                wrong ? 'border-red-300 bg-red-50' :
                placedItem ? 'border-sitou-primary bg-amber-50' :
                draggedItem ? 'border-dashed border-amber-300 bg-amber-50/30 cursor-pointer' :
                'border-gray-200 bg-white'
              }`}
              role="button"
              aria-label={`Zone : ${zone.label}`}
            >
              <span className="text-sm font-medium text-gray-500 flex-shrink-0 min-w-[80px]">{zone.label}</span>
              <span className="text-gray-300 mx-1">←</span>
              {placedItem ? (
                <span className="flex items-center gap-2 flex-1">
                  <span className="font-bold text-gray-800 text-sm">{placedItem.label}</span>
                  {!isFeedbackMode && (
                    <button onClick={(e) => { e.stopPropagation(); handleRemove(placedItem.id); }} className="text-gray-400 hover:text-red-500 ml-auto" aria-label="Retirer">
                      <X size={14} />
                    </button>
                  )}
                  {correct && <Check size={16} className="text-green-600 ml-auto" />}
                  {wrong && <X size={16} className="text-red-500 ml-auto" />}
                </span>
              ) : (
                <span className="text-gray-300 text-sm italic">Glisse un élément ici</span>
              )}
            </div>
          );
        })}
      </div>

      {isFeedbackMode && (
        <div className="text-sm text-gray-500 mt-2" role="alert" aria-live="polite">
          {dropZones.filter((z: any) => {
            const placed = leftItems.find((i: any) => assignments[i.id] === z.id);
            return placed && z.accepts === placed.id;
          }).length === dropZones.length
            ? 'Toutes les associations sont correctes !'
            : 'Certaines associations sont incorrectes.'}
        </div>
      )}
    </div>
  );
};
