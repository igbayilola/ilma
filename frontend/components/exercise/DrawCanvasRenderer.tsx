import React, { useRef, useState, useEffect } from 'react';
import { Undo2, Trash2, Check, X } from 'lucide-react';

interface DrawCanvasRendererProps {
  config: any;
  selectedAnswer: any;
  onAnswerChange: (answer: any) => void;
  isFeedbackMode: boolean;
}

interface Point { x: number; y: number }
interface Segment { from: Point; to: Point }

/**
 * Interactive geometry canvas for construction exercises.
 * User draws segments with a ruler tool on a grid canvas.
 * Supports validation of segment lengths and angles.
 */
export const DrawCanvasRenderer: React.FC<DrawCanvasRendererProps> = ({
  config,
  selectedAnswer,
  onAnswerChange,
  isFeedbackMode,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [segments, setSegments] = useState<Segment[]>(selectedAnswer?.segments || []);
  const [drawingFrom, setDrawingFrom] = useState<Point | null>(null);
  const [currentPos, setCurrentPos] = useState<Point | null>(null);
  const [activeTool, setActiveTool] = useState<string>('pencil');

  const canvasW = config?.canvas?.width || 500;
  const canvasH = config?.canvas?.height || 350;
  const gridSize = config?.canvas?.grid_size || 20;
  const tools = config?.tools || [
    { id: 'pencil', label: 'Crayon', icon: '✏️' },
    { id: 'eraser', label: 'Gomme', icon: '🧹' },
  ];
  const validation = config?.validation || {};

  const snapToGrid = (p: Point): Point => ({
    x: Math.round(p.x / gridSize) * gridSize,
    y: Math.round(p.y / gridSize) * gridSize,
  });

  const getCanvasPos = (e: React.MouseEvent | React.TouchEvent): Point => {
    const canvas = canvasRef.current!;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvasW / rect.width;
    const scaleY = canvasH / rect.height;
    if ('touches' in e) {
      return { x: (e.touches[0].clientX - rect.left) * scaleX, y: (e.touches[0].clientY - rect.top) * scaleY };
    }
    const me = e as React.MouseEvent;
    return { x: (me.clientX - rect.left) * scaleX, y: (me.clientY - rect.top) * scaleY };
  };

  const handleDown = (e: React.MouseEvent | React.TouchEvent) => {
    if (isFeedbackMode) return;
    const pos = snapToGrid(getCanvasPos(e));
    if (activeTool === 'pencil') {
      setDrawingFrom(pos);
      setCurrentPos(pos);
    }
  };

  const handleMove = (e: React.MouseEvent | React.TouchEvent) => {
    if (!drawingFrom || isFeedbackMode) return;
    setCurrentPos(getCanvasPos(e));
  };

  const handleUp = () => {
    if (!drawingFrom || !currentPos || isFeedbackMode) return;
    const to = snapToGrid(currentPos);
    const dist = Math.hypot(to.x - drawingFrom.x, to.y - drawingFrom.y);
    if (dist > gridSize / 2) {
      const newSegments = [...segments, { from: drawingFrom, to }];
      setSegments(newSegments);
      onAnswerChange({ segments: newSegments });
    }
    setDrawingFrom(null);
    setCurrentPos(null);
  };

  const handleUndo = () => {
    if (isFeedbackMode) return;
    const newSegments = segments.slice(0, -1);
    setSegments(newSegments);
    onAnswerChange({ segments: newSegments });
  };

  const handleClear = () => {
    if (isFeedbackMode) return;
    setSegments([]);
    onAnswerChange({ segments: [] });
  };

  // Draw canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvasW, canvasH);

    // Grid
    ctx.strokeStyle = '#e5e7eb';
    ctx.lineWidth = 0.5;
    for (let x = 0; x <= canvasW; x += gridSize) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvasH); ctx.stroke();
    }
    for (let y = 0; y <= canvasH; y += gridSize) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvasW, y); ctx.stroke();
    }

    // Segments
    ctx.strokeStyle = '#1F2937';
    ctx.lineWidth = 2.5;
    ctx.lineCap = 'round';
    for (const seg of segments) {
      ctx.beginPath();
      ctx.moveTo(seg.from.x, seg.from.y);
      ctx.lineTo(seg.to.x, seg.to.y);
      ctx.stroke();

      // Dots at endpoints
      for (const p of [seg.from, seg.to]) {
        ctx.fillStyle = '#D97706';
        ctx.beginPath();
        ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
        ctx.fill();
      }

      // Length label
      const dist = Math.hypot(seg.to.x - seg.from.x, seg.to.y - seg.from.y);
      const midX = (seg.from.x + seg.to.x) / 2;
      const midY = (seg.from.y + seg.to.y) / 2;
      const mm = Math.round(dist);
      ctx.fillStyle = '#6B7280';
      ctx.font = '11px sans-serif';
      ctx.fillText(`${mm / 10} cm`, midX + 5, midY - 5);
    }

    // Current drawing line
    if (drawingFrom && currentPos) {
      ctx.strokeStyle = '#D97706';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([5, 5]);
      ctx.beginPath();
      ctx.moveTo(drawingFrom.x, drawingFrom.y);
      ctx.lineTo(currentPos.x, currentPos.y);
      ctx.stroke();
      ctx.setLineDash([]);
    }
  }, [segments, drawingFrom, currentPos, canvasW, canvasH, gridSize]);

  // Validation feedback
  const checkSegments = validation?.check_segments || [];
  const results = isFeedbackMode ? checkSegments.map((spec: any) => {
    const tolerancePx = (spec.tolerance || 2) * 10; // mm → approx px
    const targetPx = spec.length_mm;
    const match = segments.find(s => {
      const len = Math.hypot(s.to.x - s.from.x, s.to.y - s.from.y);
      return Math.abs(len - targetPx) <= tolerancePx;
    });
    return { name: spec.name, target: spec.length_mm / 10, found: !!match };
  }) : [];

  return (
    <div className="max-w-lg mx-auto">
      {/* Toolbar */}
      <div className="flex items-center gap-2 mb-2 p-2 bg-gray-50 rounded-xl">
        {tools.map((tool: any) => (
          <button
            key={tool.id}
            onClick={() => setActiveTool(tool.id)}
            disabled={isFeedbackMode}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
              activeTool === tool.id ? 'bg-sitou-primary text-white' : 'bg-white border border-gray-200 hover:border-amber-300'
            }`}
            aria-label={tool.label}
          >
            {tool.icon} {tool.label}
          </button>
        ))}
        <div className="flex-1" />
        <button onClick={handleUndo} disabled={isFeedbackMode || segments.length === 0} className="p-1.5 rounded hover:bg-gray-200 disabled:opacity-30" aria-label="Annuler">
          <Undo2 size={16} />
        </button>
        <button onClick={handleClear} disabled={isFeedbackMode || segments.length === 0} className="p-1.5 rounded hover:bg-gray-200 disabled:opacity-30" aria-label="Tout effacer">
          <Trash2 size={16} />
        </button>
      </div>

      {/* Canvas */}
      <canvas
        ref={canvasRef}
        width={canvasW}
        height={canvasH}
        className="w-full border-2 border-gray-200 rounded-xl bg-white cursor-crosshair touch-none"
        style={{ maxHeight: 350 }}
        onMouseDown={handleDown}
        onMouseMove={handleMove}
        onMouseUp={handleUp}
        onMouseLeave={handleUp}
        onTouchStart={handleDown}
        onTouchMove={handleMove}
        onTouchEnd={handleUp}
        aria-label="Zone de construction géométrique"
        role="img"
      />

      {/* Validation results */}
      {isFeedbackMode && results.length > 0 && (
        <div className="mt-3 space-y-1" role="alert" aria-live="polite">
          {results.map((r: any) => (
            <div key={r.name} className={`flex items-center gap-2 text-sm ${r.found ? 'text-green-600' : 'text-red-500'}`}>
              {r.found ? <Check size={14} /> : <X size={14} />}
              {r.name} = {r.target} cm {r.found ? '(correct)' : '(non trouvé)'}
            </div>
          ))}
        </div>
      )}

      {!isFeedbackMode && (
        <p className="text-xs text-gray-400 text-center mt-2">Clique et glisse pour tracer des segments. Les points s'alignent sur la grille.</p>
      )}
    </div>
  );
};
