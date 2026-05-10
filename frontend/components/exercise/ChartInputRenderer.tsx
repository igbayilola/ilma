import React, { useState } from 'react';
import { Check, X } from 'lucide-react';

interface ChartInputRendererProps {
  config: any;
  selectedAnswer: any;
  onAnswerChange: (answer: any) => void;
  isFeedbackMode: boolean;
}

/**
 * Interactive chart renderer.
 * User sets bar heights by clicking/tapping on a bar chart.
 */
export const ChartInputRenderer: React.FC<ChartInputRendererProps> = ({
  config,
  selectedAnswer,
  onAnswerChange,
  isFeedbackMode,
}) => {
  const chartData = config?.data || {};
  const labels: string[] = chartData.labels || [];
  const targetValues: number[] = chartData.target_values || [];
  const unit = chartData.unit || '';
  const yAxis = chartData.y_axis || { min: 0, max: 100, step: 10 };
  const tolerance = config?.validation?.tolerance ?? 1;

  const values: (number | null)[] = selectedAnswer || labels.map(() => null);

  const setBarValue = (index: number, value: number) => {
    if (isFeedbackMode) return;
    const newValues = [...values];
    newValues[index] = Math.max(yAxis.min, Math.min(yAxis.max, value));
    onAnswerChange(newValues);
  };

  const maxHeight = 200; // px
  const valueToHeight = (val: number | null) => {
    if (val === null) return 0;
    return (val / yAxis.max) * maxHeight;
  };

  const handleBarClick = (index: number, e: React.MouseEvent<HTMLDivElement>) => {
    if (isFeedbackMode) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const clickY = e.clientY - rect.top;
    const ratio = 1 - clickY / rect.height;
    const value = Math.round(yAxis.min + ratio * (yAxis.max - yAxis.min));
    const snapped = Math.round(value / yAxis.step) * yAxis.step;
    setBarValue(index, snapped);
  };

  return (
    <div className="max-w-lg mx-auto">
      {/* Y axis labels */}
      <div className="flex items-end gap-1" style={{ height: maxHeight + 40 }}>
        {/* Y axis */}
        <div className="flex flex-col justify-between h-full text-xs text-gray-400 pr-1 pb-6" style={{ height: maxHeight }}>
          {Array.from({ length: Math.floor((yAxis.max - yAxis.min) / yAxis.step) + 1 }).reverse().map((_, i) => {
            const val = yAxis.min + i * yAxis.step;
            return <span key={val} className="leading-none">{val}</span>;
          })}
        </div>

        {/* Bars */}
        {labels.map((label, i) => {
          const val = values[i];
          const target = targetValues[i];
          const isCorrect = isFeedbackMode && val !== null && Math.abs(val - target) <= tolerance;
          const isWrong = isFeedbackMode && val !== null && Math.abs(val - target) > tolerance;

          return (
            <div key={i} className="flex-1 flex flex-col items-center">
              {/* Value display */}
              <span className={`text-xs font-bold mb-1 ${
                isCorrect ? 'text-green-600' : isWrong ? 'text-red-500' : 'text-gray-600'
              }`}>
                {val !== null ? `${val}${unit}` : '-'}
                {isCorrect && <Check size={12} className="inline ml-0.5" />}
                {isWrong && <X size={12} className="inline ml-0.5" />}
              </span>

              {/* Clickable bar area */}
              <div
                className="w-full relative cursor-pointer bg-gray-50 border border-gray-200 rounded-t"
                style={{ height: maxHeight }}
                onClick={(e) => handleBarClick(i, e)}
                role="slider"
                aria-label={`${label}: ${val !== null ? val : 'non défini'} ${unit}`}
                aria-valuemin={yAxis.min}
                aria-valuemax={yAxis.max}
                aria-valuenow={val ?? undefined}
              >
                {/* Filled bar */}
                <div
                  className={`absolute bottom-0 left-1 right-1 rounded-t transition-all duration-200 ${
                    isCorrect ? 'bg-green-400' : isWrong ? 'bg-red-400' : 'bg-sitou-primary'
                  }`}
                  style={{ height: valueToHeight(val) }}
                />

                {/* Target indicator in feedback mode */}
                {isFeedbackMode && (
                  <div
                    className="absolute left-0 right-0 border-t-2 border-dashed border-gray-400"
                    style={{ bottom: valueToHeight(target) }}
                    title={`Attendu: ${target}${unit}`}
                  />
                )}
              </div>

              {/* Label */}
              <span className="text-xs text-gray-500 mt-1 text-center truncate w-full">{label}</span>
            </div>
          );
        })}
      </div>

      {!isFeedbackMode && (
        <p className="text-xs text-gray-400 text-center mt-3">Clique sur les colonnes pour ajuster leur hauteur</p>
      )}

      {isFeedbackMode && (
        <div className="mt-3 text-sm text-center" role="alert" aria-live="polite">
          {values.every((v, i) => v !== null && Math.abs(v - targetValues[i]) <= tolerance)
            ? <span className="text-green-600 font-bold">Toutes les valeurs sont correctes !</span>
            : <span className="text-red-500">Certaines valeurs sont incorrectes. Les lignes pointillées montrent les valeurs attendues.</span>}
        </div>
      )}
    </div>
  );
};
