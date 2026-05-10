import React, { useState, useEffect, useCallback } from 'react';
import { Card } from '../../components/ui/Cards';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { Modal } from '../../components/ui/Modal';
import { ButtonVariant, Question } from '../../types';
import { FileEdit, CheckCircle2, Archive, AlertCircle, ChevronRight, Send, RotateCcw, Eye, Plus, MessageCircle, Trash2, Upload, Download, History, Play, ArrowRight } from 'lucide-react';
import { QuestionRenderer } from '../../components/exercise/QuestionRenderer';
import { contentService, KanbanQuestionDTO, QuestionCommentDTO, ContentVersionDTO, BulkImportReport, BulkImportRowError } from '../../services/contentService';
import { apiClient } from '../../services/apiClient';

const QUESTION_TYPES = [
  { value: 'MCQ', label: 'QCM' },
  { value: 'TRUE_FALSE', label: 'Vrai/Faux' },
  { value: 'FILL_BLANK', label: 'Compl\u00e9ter' },
  { value: 'NUMERIC_INPUT', label: 'R\u00e9ponse num\u00e9rique' },
  { value: 'SHORT_ANSWER', label: 'R\u00e9ponse courte' },
  { value: 'ORDERING', label: 'Classement' },
  { value: 'MATCHING', label: 'Glisser-d\u00e9poser' },
  { value: 'ERROR_CORRECTION', label: "Correction d'erreur" },
  { value: 'CONTEXTUAL_PROBLEM', label: 'Probl\u00e8me contextualis\u00e9' },
  { value: 'GUIDED_STEPS', label: '\u00c9tapes guid\u00e9es' },
  { value: 'JUSTIFICATION', label: 'Justification' },
  { value: 'TRACING', label: 'Tracer' },
];

const DIFFICULTY_OPTIONS = [
  { value: 'EASY', label: 'Facile' },
  { value: 'MEDIUM', label: 'Moyen' },
  { value: 'HARD', label: 'Difficile' },
];

interface QuestionFormData {
  skill_id: string;
  question_type: string;
  difficulty: string;
  text: string;
  choices: string;
  correct_answer: string;
  explanation: string;
  points: number;
}

const COLUMNS = [
  { status: 'DRAFT', label: 'Brouillon', icon: <FileEdit size={16} />, color: 'text-gray-600', bg: 'bg-gray-50', border: 'border-gray-200' },
  { status: 'IN_REVIEW', label: 'En relecture', icon: <Eye size={16} />, color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-200' },
  { status: 'PUBLISHED', label: 'Publie', icon: <CheckCircle2 size={16} />, color: 'text-green-600', bg: 'bg-green-50', border: 'border-green-200' },
  { status: 'ARCHIVED', label: 'Archive', icon: <Archive size={16} />, color: 'text-gray-400', bg: 'bg-gray-50', border: 'border-gray-100' },
];

const TRANSITIONS: Record<string, { label: string; target: string; icon: React.ReactNode; variant: ButtonVariant; needsNotes?: boolean }[]> = {
  DRAFT: [
    { label: 'Soumettre', target: 'IN_REVIEW', icon: <Send size={14} />, variant: ButtonVariant.PRIMARY },
  ],
  IN_REVIEW: [
    { label: 'Approuver', target: 'PUBLISHED', icon: <CheckCircle2 size={14} />, variant: ButtonVariant.PRIMARY },
    { label: 'Retourner', target: 'DRAFT', icon: <RotateCcw size={14} />, variant: ButtonVariant.SECONDARY, needsNotes: true },
  ],
  PUBLISHED: [
    { label: 'Archiver', target: 'ARCHIVED', icon: <Archive size={14} />, variant: ButtonVariant.GHOST },
  ],
  ARCHIVED: [
    { label: 'Restaurer', target: 'DRAFT', icon: <RotateCcw size={14} />, variant: ButtonVariant.SECONDARY },
  ],
};

const EMPTY_FORM: QuestionFormData = {
  skill_id: '',
  question_type: 'MCQ',
  difficulty: 'MEDIUM',
  text: '',
  choices: '',
  correct_answer: '',
  explanation: '',
  points: 1,
};

export const AdminEditorialPage: React.FC = () => {
  const [columns, setColumns] = useState<Record<string, KanbanQuestionDTO[]>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [transitionModal, setTransitionModal] = useState<{
    question: KanbanQuestionDTO;
    target: string;
    needsNotes: boolean;
  } | null>(null);
  const [notes, setNotes] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  // Question form state
  const [questionModal, setQuestionModal] = useState(false);
  const [editingQuestionId, setEditingQuestionId] = useState<string | null>(null);
  const [formData, setFormData] = useState<QuestionFormData>({ ...EMPTY_FORM });
  const [formSaving, setFormSaving] = useState(false);
  const [formError, setFormError] = useState('');

  // Detail modal (with tabs: Edition / Commentaires / Historique)
  const [detailQuestion, setDetailQuestion] = useState<KanbanQuestionDTO | null>(null);
  const [detailTab, setDetailTab] = useState<'edition' | 'commentaires' | 'historique'>('edition');
  const [comments, setComments] = useState<QuestionCommentDTO[]>([]);
  const [versions, setVersions] = useState<ContentVersionDTO[]>([]);
  const [versionsLoading, setVersionsLoading] = useState(false);
  const [rollbackConfirm, setRollbackConfirm] = useState<number | null>(null);
  const [rollbackSaving, setRollbackSaving] = useState(false);
  const [commentsLoading, setCommentsLoading] = useState(false);
  const [newCommentText, setNewCommentText] = useState('');
  const [commentSaving, setCommentSaving] = useState(false);
  const [commentCounts, setCommentCounts] = useState<Record<string, number>>({});

  // Preview state
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewQuestion, setPreviewQuestion] = useState<Question | null>(null);
  const [previewAnswer, setPreviewAnswer] = useState<any>(null);
  const [previewFeedback, setPreviewFeedback] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewStatus, setPreviewStatus] = useState('');

  // Batch test state ("Tester en série")
  const [batchTestOpen, setBatchTestOpen] = useState(false);
  const [batchQuestions, setBatchQuestions] = useState<Question[]>([]);
  const [batchIndex, setBatchIndex] = useState(0);
  const [batchAnswer, setBatchAnswer] = useState<any>(null);
  const [batchFeedback, setBatchFeedback] = useState(false);
  const [batchResults, setBatchResults] = useState<{ correct: boolean; answer: any }[]>([]);
  const [batchDone, setBatchDone] = useState(false);
  const [batchLoading, setBatchLoading] = useState(false);

  // Import state
  const [importModalOpen, setImportModalOpen] = useState(false);
  const [importFile, setImportFile] = useState<File | null>(null);
  const [importLoading, setImportLoading] = useState(false);
  const [importReport, setImportReport] = useState<BulkImportReport | null>(null);
  const [importError, setImportError] = useState('');

  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleImportFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    if (file) {
      const ext = file.name.toLowerCase();
      if (!ext.endsWith('.csv') && !ext.endsWith('.json')) {
        setImportError('Seuls les fichiers CSV (.csv) et JSON (.json) sont acceptes.');
        setImportFile(null);
        return;
      }
      setImportError('');
      setImportFile(file);
    }
  };

  const handleImportSubmit = async () => {
    if (!importFile) return;
    setImportLoading(true);
    setImportError('');
    setImportReport(null);
    try {
      const report = await contentService.importQuestions(importFile);
      setImportReport(report);
      if (report.status === 'success') {
        await loadAll();
      }
    } catch (err: any) {
      setImportError(err?.message || 'Erreur lors de l\'import.');
    } finally {
      setImportLoading(false);
    }
  };

  const closeImportModal = () => {
    setImportModalOpen(false);
    setImportFile(null);
    setImportReport(null);
    setImportError('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const downloadErrorReport = () => {
    if (!importReport || !importReport.errors.length) return;
    const header = 'Ligne,Message\n';
    const rows = importReport.errors.map(e => `${e.row},"${e.message.replace(/"/g, '""')}"`).join('\n');
    const csv = header + rows;
    const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'rapport_erreurs_import.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  const QUESTION_TYPE_MAP_PREVIEW: Record<string, string> = {
    mcq: 'MCQ', true_false: 'TRUE_FALSE', fill_blank: 'FILL_BLANK',
    numeric_input: 'NUMERIC_INPUT', short_answer: 'SHORT_ANSWER',
    ordering: 'ORDERING', matching: 'MATCHING', error_correction: 'ERROR_CORRECTION',
    contextual_problem: 'CONTEXTUAL_PROBLEM', guided_steps: 'GUIDED_STEPS',
    justification: 'JUSTIFICATION', tracing: 'TRACING',
    drag_drop: 'DRAG_DROP', interactive_draw: 'INTERACTIVE_DRAW',
    chart_input: 'CHART_INPUT', audio_comprehension: 'AUDIO_COMPREHENSION',
  };

  const openPreview = async (q: KanbanQuestionDTO) => {
    setPreviewLoading(true);
    setPreviewOpen(true);
    setPreviewAnswer(null);
    setPreviewFeedback(false);
    setPreviewStatus('');
    try {
      const data = await contentService.previewQuestion(q.id);
      const mappedType = QUESTION_TYPE_MAP_PREVIEW[data.questionType.toLowerCase()] || 'MCQ';
      setPreviewQuestion({
        id: data.id,
        type: mappedType as any,
        prompt: data.text,
        options: Array.isArray(data.choices) ? data.choices : undefined,
        choices: data.choices,
        correctAnswer: data.correctAnswer,
        explanation: data.explanation || '',
        hint: data.hint || undefined,
        imageUrl: data.mediaUrl || undefined,
      });
      setPreviewStatus(data.status);
    } catch {
      setPreviewQuestion(null);
    } finally {
      setPreviewLoading(false);
    }
  };

  const handlePreviewValidate = () => {
    if (previewAnswer === null || previewAnswer === '') return;
    setPreviewFeedback(true);
  };

  const handlePreviewReset = () => {
    setPreviewAnswer(null);
    setPreviewFeedback(false);
  };

  // ── Batch test functions ──────────────────────────────────
  const startBatchTest = async (status: string) => {
    const questionsInColumn = columns[status] || [];
    if (questionsInColumn.length === 0) return;
    setBatchLoading(true);
    setBatchTestOpen(true);
    setBatchIndex(0);
    setBatchAnswer(null);
    setBatchFeedback(false);
    setBatchResults([]);
    setBatchDone(false);

    const loaded: Question[] = [];
    for (const q of questionsInColumn.slice(0, 20)) {
      try {
        const data = await contentService.previewQuestion(q.id);
        const mappedType = QUESTION_TYPE_MAP_PREVIEW[data.questionType.toLowerCase()] || 'MCQ';
        loaded.push({
          id: q.id,
          type: mappedType as any,
          prompt: data.text,
          options: Array.isArray(data.choices) ? data.choices : undefined,
          choices: data.choices,
          correctAnswer: data.correctAnswer,
          explanation: data.explanation,
          hint: data.hint,
          imageUrl: data.mediaUrl || undefined,
        } as Question);
      } catch { /* skip failed loads */ }
    }
    setBatchQuestions(loaded);
    setBatchLoading(false);
  };

  const batchValidate = () => {
    if (batchAnswer === null || batchAnswer === '') return;
    setBatchFeedback(true);
    const current = batchQuestions[batchIndex];
    const correct = String(current.correctAnswer).trim().toLowerCase();
    const answer = String(batchAnswer).trim().toLowerCase();
    const isCorrect = correct === answer;
    setBatchResults(prev => [...prev, { correct: isCorrect, answer: batchAnswer }]);
  };

  const batchNext = () => {
    if (batchIndex + 1 >= batchQuestions.length) {
      setBatchDone(true);
    } else {
      setBatchIndex(prev => prev + 1);
      setBatchAnswer(null);
      setBatchFeedback(false);
    }
  };

  const closeBatchTest = () => {
    setBatchTestOpen(false);
    setBatchQuestions([]);
    setBatchResults([]);
    setBatchDone(false);
  };

  const batchScore = batchResults.filter(r => r.correct).length;

  const openDetailModal = async (q: KanbanQuestionDTO) => {
    setDetailQuestion(q);
    setDetailTab('edition');
    setComments([]);
    setNewCommentText('');
    setVersions([]);
    setRollbackConfirm(null);
    loadComments(q.id);
    loadVersions(q.id);
  };

  const loadVersions = async (questionId: string) => {
    setVersionsLoading(true);
    try {
      const data = await contentService.getQuestionVersions(questionId);
      setVersions(data);
    } catch {
      setVersions([]);
    } finally {
      setVersionsLoading(false);
    }
  };

  const handleRollback = async (versionNum: number) => {
    if (!detailQuestion) return;
    setRollbackSaving(true);
    try {
      await contentService.rollbackQuestion(detailQuestion.id, versionNum);
      setRollbackConfirm(null);
      // Reload kanban and version list
      await loadAll();
      await loadVersions(detailQuestion.id);
    } catch {
      // silently fail
    } finally {
      setRollbackSaving(false);
    }
  };

  const loadComments = async (questionId: string) => {
    setCommentsLoading(true);
    try {
      const data = await contentService.getQuestionComments(questionId);
      setComments(data);
      setCommentCounts(prev => ({ ...prev, [questionId]: data.length }));
    } catch {
      setComments([]);
    } finally {
      setCommentsLoading(false);
    }
  };

  const handleAddComment = async () => {
    if (!detailQuestion || !newCommentText.trim()) return;
    setCommentSaving(true);
    try {
      const c = await contentService.addQuestionComment(detailQuestion.id, newCommentText.trim());
      setComments(prev => [...prev, c]);
      setCommentCounts(prev => ({ ...prev, [detailQuestion.id]: (prev[detailQuestion.id] || 0) + 1 }));
      setNewCommentText('');
    } catch {
      // silently fail
    } finally {
      setCommentSaving(false);
    }
  };

  const handleDeleteComment = async (commentId: string) => {
    if (!detailQuestion) return;
    try {
      await contentService.deleteQuestionComment(detailQuestion.id, commentId);
      setComments(prev => prev.filter(c => c.id !== commentId));
      setCommentCounts(prev => ({ ...prev, [detailQuestion.id]: Math.max(0, (prev[detailQuestion.id] || 1) - 1) }));
    } catch {
      // silently fail
    }
  };

  const closeDetailModal = () => {
    setDetailQuestion(null);
    setComments([]);
    setNewCommentText('');
    setVersions([]);
    setRollbackConfirm(null);
  };

  const formatCommentDate = (iso: string) => {
    try {
      const d = new Date(iso);
      return d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch {
      return iso;
    }
  };

  const isPreviewCorrect = (): boolean => {
    if (!previewQuestion || previewAnswer === null) return false;
    const correct = String(previewQuestion.correctAnswer).trim().toLowerCase();
    const answer = String(previewAnswer).trim().toLowerCase();
    return correct === answer;
  };

  const loadAll = useCallback(async () => {
    setIsLoading(true);
    try {
      const [draft, review, published, archived] = await Promise.all([
        contentService.listQuestionsByStatus('DRAFT').catch(() => []),
        contentService.listQuestionsByStatus('IN_REVIEW').catch(() => []),
        contentService.listQuestionsByStatus('PUBLISHED', 30).catch(() => []),
        contentService.listQuestionsByStatus('ARCHIVED', 20).catch(() => []),
      ]);
      setColumns({ DRAFT: draft, IN_REVIEW: review, PUBLISHED: published, ARCHIVED: archived });
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { loadAll(); }, [loadAll]);

  const handleTransition = async () => {
    if (!transitionModal) return;
    setSaving(true);
    setError('');
    try {
      await contentService.transitionQuestion(
        transitionModal.question.id,
        transitionModal.target,
        notes || undefined,
      );
      setTransitionModal(null);
      setNotes('');
      await loadAll();
    } catch (err: any) {
      setError(err?.message || 'Erreur lors de la transition.');
    } finally {
      setSaving(false);
    }
  };

  const openCreateForm = () => {
    setEditingQuestionId(null);
    setFormData({ ...EMPTY_FORM });
    setFormError('');
    setQuestionModal(true);
  };

  const openEditForm = async (q: KanbanQuestionDTO) => {
    setEditingQuestionId(q.id);
    setFormData({
      skill_id: q.skillId || '',
      question_type: q.questionType || 'MCQ',
      difficulty: q.difficulty || 'MEDIUM',
      text: q.text || '',
      choices: '',
      correct_answer: '',
      explanation: '',
      points: 1,
    });
    setFormError('');
    setQuestionModal(true);
    // Load full question data to pre-populate choices, correct_answer, explanation, points
    try {
      const data = await contentService.previewQuestion(q.id);
      setFormData(prev => ({
        ...prev,
        choices: Array.isArray(data.choices) ? data.choices.join('\n') : '',
        correct_answer: data.correctAnswer != null ? String(data.correctAnswer) : '',
        explanation: data.explanation || '',
        points: data.points || 1,
      }));
    } catch { /* keep defaults if preview fails */ }
  };

  const updateField = (field: keyof QuestionFormData, value: string | number) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleQuestionSubmit = async () => {
    if (!formData.skill_id.trim() || !formData.text.trim() || !formData.correct_answer.trim()) {
      setFormError('Les champs Competence (skill_id), Texte et Reponse correcte sont obligatoires.');
      return;
    }
    setFormSaving(true);
    setFormError('');
    try {
      const payload: Record<string, any> = {
        skill_id: formData.skill_id.trim(),
        question_type: formData.question_type,
        difficulty: formData.difficulty,
        text: formData.text.trim(),
        correct_answer: formData.correct_answer.trim(),
        points: formData.points,
      };
      if (formData.explanation.trim()) {
        payload.explanation = formData.explanation.trim();
      }
      if (formData.question_type === 'MCQ' && formData.choices.trim()) {
        payload.choices = formData.choices.split('\n').map(c => c.trim()).filter(Boolean);
      }

      if (editingQuestionId) {
        await apiClient.put(`/admin/content/questions/${editingQuestionId}`, payload);
      } else {
        await apiClient.post('/admin/content/questions', payload);
      }
      setQuestionModal(false);
      setEditingQuestionId(null);
      setFormData({ ...EMPTY_FORM });
      await loadAll();
    } catch (err: any) {
      setFormError(err?.message || 'Erreur lors de la sauvegarde.');
    } finally {
      setFormSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton variant="text" className="w-64 h-8" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => <Skeleton key={i} variant="rect" className="h-64" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <header className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900">Workflow Editorial</h1>
          <p className="text-gray-500 text-sm">Gerez le cycle de vie des questions : brouillon, relecture, publication.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant={ButtonVariant.SECONDARY}
            onClick={() => { setImportReport(null); setImportFile(null); setImportError(''); setImportModalOpen(true); }}
          >
            <Upload size={16} className="mr-1.5" />
            Importer
          </Button>
          <Button variant={ButtonVariant.GHOST} onClick={loadAll}>Actualiser</Button>
        </div>
      </header>

      {/* Kanban columns */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 items-start">
        {COLUMNS.map(col => {
          const items = columns[col.status] || [];
          return (
            <div key={col.status} className={`rounded-2xl border ${col.border} ${col.bg} min-h-[200px]`}>
              {/* Column header */}
              <div className={`flex items-center gap-2 px-4 py-3 border-b ${col.border}`}>
                <span className={col.color}>{col.icon}</span>
                <h2 className={`text-sm font-bold ${col.color}`}>{col.label}</h2>
                <span className={`ml-auto text-xs font-bold px-2 py-0.5 rounded-full ${col.bg} ${col.color} border ${col.border}`}>
                  {items.length}
                </span>
                {items.length > 0 && (
                  <button
                    onClick={() => startBatchTest(col.status)}
                    className="ml-1 p-1 rounded-lg bg-indigo-100 text-indigo-600 hover:bg-indigo-200 transition-colors"
                    title={`Tester les ${items.length} questions`}
                  >
                    <Play size={14} />
                  </button>
                )}
                {col.status === 'DRAFT' && (
                  <button
                    onClick={openCreateForm}
                    className="ml-1 p-1 rounded-lg bg-sitou-primary text-white hover:opacity-90 transition-opacity"
                    aria-label="Creer une nouvelle question"
                    title="Nouvelle question"
                  >
                    <Plus size={14} />
                  </button>
                )}
              </div>

              {/* Cards */}
              <div className="p-2 space-y-2">
                {items.length === 0 && (
                  <p className="text-xs text-gray-400 text-center py-6">Aucune question</p>
                )}
                {items.map(q => (
                  <Card key={q.id} className="p-3 bg-white shadow-sm hover:shadow-md transition-shadow">
                    <p
                      className="text-sm text-gray-800 font-medium line-clamp-2 mb-2 cursor-pointer hover:text-sitou-primary transition-colors"
                      onClick={() => openDetailModal(q)}
                      role="button"
                      tabIndex={0}
                      onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openDetailModal(q); } }}
                      title="Cliquer pour voir les details"
                    >
                      {q.text || '(Sans texte)'}
                    </p>
                    <div className="flex items-center gap-2 text-[11px] text-gray-400 mb-2">
                      {q.questionType && <span className="bg-gray-100 px-1.5 py-0.5 rounded">{q.questionType}</span>}
                      {q.difficulty && <span className="bg-purple-50 text-purple-500 px-1.5 py-0.5 rounded">{q.difficulty}</span>}
                      {(commentCounts[q.id] || 0) > 0 && (
                        <button
                          onClick={(e) => { e.stopPropagation(); openDetailModal(q); setDetailTab('commentaires'); }}
                          className="flex items-center gap-0.5 bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded hover:bg-blue-100 transition-colors"
                          title="Voir les commentaires"
                        >
                          <MessageCircle size={10} />
                          <span>{commentCounts[q.id]}</span>
                        </button>
                      )}
                    </div>
                    {q.reviewerNotes && (
                      <p className="text-xs text-amber-600 bg-amber-50 rounded-lg px-2 py-1 mb-2 line-clamp-2">
                        {q.reviewerNotes}
                      </p>
                    )}
                    {/* Transition actions */}
                    <div className="flex gap-1.5 flex-wrap">
                      <button
                        onClick={() => openPreview(q)}
                        className="flex items-center gap-1 text-xs font-bold px-2 py-1 rounded-lg transition-colors bg-indigo-50 text-indigo-600 hover:bg-indigo-100"
                        title="Apercu mode eleve"
                        aria-label="Previsualiser la question"
                      >
                        <Eye size={14} />
                        Apercu
                      </button>
                      {(TRANSITIONS[q.status] || []).map(t => (
                        <button
                          key={t.target}
                          onClick={() => {
                            if (t.needsNotes) {
                              setTransitionModal({ question: q, target: t.target, needsNotes: true });
                            } else {
                              setTransitionModal({ question: q, target: t.target, needsNotes: false });
                            }
                          }}
                          className={`flex items-center gap-1 text-xs font-bold px-2 py-1 rounded-lg transition-colors ${
                            t.variant === ButtonVariant.PRIMARY
                              ? 'bg-sitou-primary text-white hover:opacity-90'
                              : t.variant === ButtonVariant.GHOST
                              ? 'text-gray-500 hover:bg-gray-100'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          {t.icon}
                          {t.label}
                        </button>
                      ))}
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Transition confirmation modal */}
      <Modal
        isOpen={!!transitionModal}
        onClose={() => { setTransitionModal(null); setNotes(''); setError(''); }}
        title="Confirmer la transition"
      >
        {transitionModal && (
          <div className="space-y-4">
            <p className="text-sm text-gray-700">
              Transition : <b>{transitionModal.question.status}</b> <ChevronRight size={14} className="inline" /> <b>{transitionModal.target}</b>
            </p>
            <p className="text-sm text-gray-500 line-clamp-3">{transitionModal.question.text}</p>

            {transitionModal.needsNotes && (
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-1">Notes de relecture *</label>
                <textarea
                  value={notes}
                  onChange={e => setNotes(e.target.value)}
                  rows={3}
                  placeholder="Expliquez pourquoi la question est retournee..."
                  className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-sitou-primary/20 focus:border-sitou-primary text-sm resize-none"
                />
              </div>
            )}

            {!transitionModal.needsNotes && (
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-1">Notes (optionnel)</label>
                <textarea
                  value={notes}
                  onChange={e => setNotes(e.target.value)}
                  rows={2}
                  placeholder="Commentaire..."
                  className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-sitou-primary/20 focus:border-sitou-primary text-sm resize-none"
                />
              </div>
            )}

            {error && (
              <div className="flex items-center text-sm text-red-600 bg-red-50 px-4 py-2 rounded-xl">
                <AlertCircle size={16} className="mr-2 shrink-0" /> {error}
              </div>
            )}

            <div className="flex justify-end space-x-3 pt-2">
              <Button variant={ButtonVariant.GHOST} onClick={() => { setTransitionModal(null); setNotes(''); setError(''); }}>
                Annuler
              </Button>
              <Button
                onClick={handleTransition}
                isLoading={saving}
                disabled={transitionModal.needsNotes && !notes.trim()}
              >
                Confirmer
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Question creation / editing modal */}
      <Modal
        isOpen={questionModal}
        onClose={() => { setQuestionModal(false); setEditingQuestionId(null); setFormError(''); }}
        title={editingQuestionId ? 'Modifier la question' : 'Nouvelle question'}
      >
        <div className="space-y-4 max-h-[70vh] overflow-y-auto pr-1">
          {/* skill_id */}
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-1">Competence (skill_id) *</label>
            <input
              type="text"
              value={formData.skill_id}
              onChange={e => updateField('skill_id', e.target.value)}
              placeholder="UUID de la competence"
              className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-sitou-primary/20 focus:border-sitou-primary text-sm"
              disabled={!!editingQuestionId}
            />
          </div>

          {/* question_type */}
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-1">Type de question</label>
            <select
              value={formData.question_type}
              onChange={e => updateField('question_type', e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-sitou-primary/20 focus:border-sitou-primary text-sm bg-white"
            >
              {QUESTION_TYPES.map(qt => (
                <option key={qt.value} value={qt.value}>{qt.label}</option>
              ))}
            </select>
          </div>

          {/* difficulty */}
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-1">Difficulte</label>
            <select
              value={formData.difficulty}
              onChange={e => updateField('difficulty', e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-sitou-primary/20 focus:border-sitou-primary text-sm bg-white"
            >
              {DIFFICULTY_OPTIONS.map(d => (
                <option key={d.value} value={d.value}>{d.label}</option>
              ))}
            </select>
          </div>

          {/* text */}
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-1">Texte de la question *</label>
            <textarea
              value={formData.text}
              onChange={e => updateField('text', e.target.value)}
              rows={3}
              placeholder="Saisissez l'enonce de la question..."
              className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-sitou-primary/20 focus:border-sitou-primary text-sm resize-none"
            />
          </div>

          {/* choices - only for MCQ */}
          {formData.question_type === 'MCQ' && (
            <div>
              <label className="block text-sm font-bold text-gray-700 mb-1">Choix (un par ligne)</label>
              <textarea
                value={formData.choices}
                onChange={e => updateField('choices', e.target.value)}
                rows={4}
                placeholder={"Choix A\nChoix B\nChoix C\nChoix D"}
                className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-sitou-primary/20 focus:border-sitou-primary text-sm resize-none font-mono"
              />
            </div>
          )}

          {/* correct_answer */}
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-1">Reponse correcte *</label>
            <input
              type="text"
              value={formData.correct_answer}
              onChange={e => updateField('correct_answer', e.target.value)}
              placeholder="La bonne reponse"
              className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-sitou-primary/20 focus:border-sitou-primary text-sm"
            />
          </div>

          {/* explanation */}
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-1">Explication (optionnel)</label>
            <textarea
              value={formData.explanation}
              onChange={e => updateField('explanation', e.target.value)}
              rows={2}
              placeholder="Explication affichee apres la reponse..."
              className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-sitou-primary/20 focus:border-sitou-primary text-sm resize-none"
            />
          </div>

          {/* points */}
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-1">Points</label>
            <input
              type="number"
              min={1}
              max={100}
              value={formData.points}
              onChange={e => updateField('points', Math.max(1, parseInt(e.target.value) || 1))}
              className="w-32 px-4 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-sitou-primary/20 focus:border-sitou-primary text-sm"
            />
          </div>

          {/* Error display */}
          {formError && (
            <div className="flex items-center text-sm text-red-600 bg-red-50 px-4 py-2 rounded-xl">
              <AlertCircle size={16} className="mr-2 shrink-0" /> {formError}
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-2">
            <Button
              variant={ButtonVariant.GHOST}
              onClick={() => { setQuestionModal(false); setEditingQuestionId(null); setFormError(''); }}
            >
              Annuler
            </Button>
            <Button
              onClick={handleQuestionSubmit}
              isLoading={formSaving}
              disabled={!formData.skill_id.trim() || !formData.text.trim() || !formData.correct_answer.trim()}
            >
              {editingQuestionId ? 'Enregistrer' : 'Creer'}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Question detail modal (Edition + Commentaires tabs) */}
      <Modal
        isOpen={!!detailQuestion}
        onClose={closeDetailModal}
        title={detailQuestion ? `Question : ${detailQuestion.text?.slice(0, 60) || '(Sans texte)'}${(detailQuestion.text?.length || 0) > 60 ? '...' : ''}` : 'Detail'}
      >
        {detailQuestion && (
          <div className="space-y-4">
            {/* Tab bar */}
            <div className="flex border-b border-gray-200">
              <button
                onClick={() => setDetailTab('edition')}
                className={`px-4 py-2 text-sm font-bold border-b-2 transition-colors ${
                  detailTab === 'edition'
                    ? 'border-sitou-primary text-sitou-primary'
                    : 'border-transparent text-gray-400 hover:text-gray-600'
                }`}
              >
                Edition
              </button>
              <button
                onClick={() => setDetailTab('commentaires')}
                className={`px-4 py-2 text-sm font-bold border-b-2 transition-colors flex items-center gap-1.5 ${
                  detailTab === 'commentaires'
                    ? 'border-sitou-primary text-sitou-primary'
                    : 'border-transparent text-gray-400 hover:text-gray-600'
                }`}
              >
                <MessageCircle size={14} />
                Commentaires
                {comments.length > 0 && (
                  <span className="bg-blue-100 text-blue-700 text-xs font-bold px-1.5 py-0.5 rounded-full">{comments.length}</span>
                )}
              </button>
              <button
                onClick={() => setDetailTab('historique')}
                className={`px-4 py-2 text-sm font-bold border-b-2 transition-colors flex items-center gap-1.5 ${
                  detailTab === 'historique'
                    ? 'border-sitou-primary text-sitou-primary'
                    : 'border-transparent text-gray-400 hover:text-gray-600'
                }`}
              >
                <History size={14} />
                Historique
                {versions.length > 0 && (
                  <span className="bg-purple-100 text-purple-700 text-xs font-bold px-1.5 py-0.5 rounded-full">{versions.length}</span>
                )}
              </button>
            </div>

            {/* Edition tab */}
            {detailTab === 'edition' && (
              <div className="space-y-3 max-h-[60vh] overflow-y-auto pr-1">
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-gray-400 text-xs">Type</span>
                    <p className="font-medium text-gray-700">{detailQuestion.questionType || '-'}</p>
                  </div>
                  <div>
                    <span className="text-gray-400 text-xs">Difficulte</span>
                    <p className="font-medium text-gray-700">{detailQuestion.difficulty || '-'}</p>
                  </div>
                  <div>
                    <span className="text-gray-400 text-xs">Statut</span>
                    <p className="font-medium text-gray-700">{detailQuestion.status}</p>
                  </div>
                  <div>
                    <span className="text-gray-400 text-xs">Mise a jour</span>
                    <p className="font-medium text-gray-700">{detailQuestion.updatedAt ? formatCommentDate(detailQuestion.updatedAt) : '-'}</p>
                  </div>
                </div>
                <div>
                  <span className="text-gray-400 text-xs">Texte</span>
                  <p className="text-sm text-gray-800 mt-1 bg-gray-50 rounded-xl p-3">{detailQuestion.text}</p>
                </div>
                {detailQuestion.reviewerNotes && (
                  <div>
                    <span className="text-gray-400 text-xs">Notes de relecture</span>
                    <p className="text-sm text-amber-700 bg-amber-50 rounded-xl p-3 mt-1">{detailQuestion.reviewerNotes}</p>
                  </div>
                )}
                <div className="flex gap-2 pt-2">
                  <Button
                    variant={ButtonVariant.SECONDARY}
                    onClick={() => { closeDetailModal(); openEditForm(detailQuestion); }}
                  >
                    <FileEdit size={14} className="mr-1.5" />
                    Modifier
                  </Button>
                  <Button
                    variant={ButtonVariant.GHOST}
                    onClick={() => { closeDetailModal(); openPreview(detailQuestion); }}
                  >
                    <Eye size={14} className="mr-1.5" />
                    Apercu
                  </Button>
                </div>
              </div>
            )}

            {/* Commentaires tab */}
            {detailTab === 'commentaires' && (
              <div className="space-y-3 max-h-[60vh] overflow-y-auto pr-1">
                {commentsLoading && (
                  <div className="flex items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-sitou-primary" />
                  </div>
                )}

                {!commentsLoading && comments.length === 0 && (
                  <p className="text-sm text-gray-400 text-center py-8">Aucun commentaire pour cette question.</p>
                )}

                {!commentsLoading && comments.map(c => (
                  <div key={c.id} className="bg-gray-50 rounded-xl p-3 space-y-1">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-gray-700">{c.authorName || 'Inconnu'}</span>
                        <span className="text-[10px] text-gray-400">{formatCommentDate(c.createdAt)}</span>
                      </div>
                      <button
                        onClick={() => handleDeleteComment(c.id)}
                        className="text-gray-300 hover:text-red-500 transition-colors p-1"
                        title="Supprimer ce commentaire"
                        aria-label="Supprimer le commentaire"
                      >
                        <Trash2 size={12} />
                      </button>
                    </div>
                    <p className="text-sm text-gray-700">{c.text}</p>
                  </div>
                ))}

                {/* New comment input */}
                <div className="flex gap-2 pt-2 border-t border-gray-100">
                  <input
                    type="text"
                    value={newCommentText}
                    onChange={e => setNewCommentText(e.target.value)}
                    placeholder="Ajouter un commentaire..."
                    className="flex-1 px-4 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-sitou-primary/20 focus:border-sitou-primary text-sm"
                    onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleAddComment(); } }}
                    disabled={commentSaving}
                  />
                  <Button
                    onClick={handleAddComment}
                    disabled={!newCommentText.trim() || commentSaving}
                    isLoading={commentSaving}
                  >
                    <Send size={14} />
                  </Button>
                </div>
              </div>
            )}

            {/* Historique tab */}
            {detailTab === 'historique' && (
              <div className="space-y-3 max-h-[60vh] overflow-y-auto pr-1">
                {versionsLoading && (
                  <div className="flex items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-sitou-primary" />
                  </div>
                )}

                {!versionsLoading && versions.length === 0 && (
                  <p className="text-sm text-gray-400 text-center py-8">Aucune version precedente pour cette question.</p>
                )}

                {!versionsLoading && versions.map(v => (
                  <div key={v.id} className="bg-gray-50 rounded-xl p-3 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="bg-purple-100 text-purple-700 text-xs font-bold px-2 py-0.5 rounded-full">
                          v{v.version}
                        </span>
                        <span className="text-xs text-gray-500">
                          {formatCommentDate(v.modified_at)}
                        </span>
                      </div>
                      {rollbackConfirm === v.version ? (
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-amber-600">Confirmer ?</span>
                          <Button
                            onClick={() => handleRollback(v.version)}
                            isLoading={rollbackSaving}
                            className="text-xs px-2.5 py-1"
                          >
                            Oui
                          </Button>
                          <button
                            onClick={() => setRollbackConfirm(null)}
                            className="text-xs text-gray-400 hover:text-gray-600 px-2 py-1"
                          >
                            Non
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setRollbackConfirm(v.version)}
                          className="flex items-center gap-1 text-xs text-sitou-primary hover:text-sitou-primary/80 font-medium transition-colors"
                        >
                          <RotateCcw size={12} />
                          Restaurer cette version
                        </button>
                      )}
                    </div>
                    {v.modified_by && (
                      <p className="text-[10px] text-gray-400">
                        Modifie par : {v.modified_by.slice(0, 8)}...
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* Preview "mode eleve" modal */}
      <Modal
        isOpen={previewOpen}
        onClose={() => { setPreviewOpen(false); setPreviewQuestion(null); setPreviewAnswer(null); setPreviewFeedback(false); }}
        title="Apercu mode eleve"
      >
        <div className="space-y-4 max-h-[75vh] overflow-y-auto">
          {previewLoading && (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sitou-primary" />
            </div>
          )}

          {!previewLoading && !previewQuestion && (
            <div className="flex items-center text-sm text-red-600 bg-red-50 px-4 py-3 rounded-xl">
              <AlertCircle size={16} className="mr-2 shrink-0" /> Impossible de charger la question.
            </div>
          )}

          {!previewLoading && previewQuestion && (
            <>
              {/* Status badge */}
              <div className="flex items-center gap-2">
                <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${
                  previewStatus === 'draft' ? 'bg-gray-100 text-gray-600' :
                  previewStatus === 'in_review' ? 'bg-amber-100 text-amber-700' :
                  previewStatus === 'published' ? 'bg-green-100 text-green-700' :
                  'bg-gray-100 text-gray-400'
                }`}>
                  {previewStatus === 'draft' ? 'Brouillon' :
                   previewStatus === 'in_review' ? 'En relecture' :
                   previewStatus === 'published' ? 'Publie' : 'Archive'}
                </span>
                <span className="text-xs text-gray-400">Mode apercu — aucune donnee enregistree</span>
              </div>

              {/* Question rendered exactly like the student sees it */}
              <div className="bg-sitou-surface rounded-2xl p-4 border border-gray-100">
                <QuestionRenderer
                  question={previewQuestion}
                  selectedAnswer={previewAnswer}
                  onAnswerChange={previewFeedback ? () => {} : setPreviewAnswer}
                  isFeedbackMode={previewFeedback}
                />
              </div>

              {/* Feedback section */}
              {previewFeedback && (
                <div className={`rounded-2xl p-4 animate-slide-up ${isPreviewCorrect() ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
                  <div className="flex items-start">
                    {isPreviewCorrect() ? (
                      <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                        <CheckCircle2 className="text-green-600 w-5 h-5" />
                      </div>
                    ) : (
                      <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                        <AlertCircle className="text-red-600 w-5 h-5" />
                      </div>
                    )}
                    <div>
                      <h3 className={`font-extrabold text-lg ${isPreviewCorrect() ? 'text-green-700' : 'text-red-700'}`}>
                        {isPreviewCorrect() ? 'Bonne reponse !' : 'Mauvaise reponse'}
                      </h3>
                      {!isPreviewCorrect() && (
                        <p className="text-sm text-gray-700 mt-1">
                          Reponse correcte : <b>{String(previewQuestion.correctAnswer)}</b>
                        </p>
                      )}
                      {previewQuestion.explanation && (
                        <p className="text-sm text-gray-600 mt-2 leading-relaxed">
                          {previewQuestion.explanation}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Action buttons */}
              <div className="flex justify-end gap-3 pt-2">
                {previewFeedback && (
                  <Button variant={ButtonVariant.SECONDARY} onClick={handlePreviewReset}>
                    <RotateCcw size={14} className="mr-1.5" />
                    Reessayer
                  </Button>
                )}
                {!previewFeedback && (
                  <Button
                    onClick={handlePreviewValidate}
                    disabled={previewAnswer === null || previewAnswer === ''}
                  >
                    Valider
                  </Button>
                )}
                <Button
                  variant={ButtonVariant.GHOST}
                  onClick={() => { setPreviewOpen(false); setPreviewQuestion(null); setPreviewAnswer(null); setPreviewFeedback(false); }}
                >
                  Fermer
                </Button>
              </div>
            </>
          )}
        </div>
      </Modal>

      {/* Import questions modal */}
      <Modal
        isOpen={importModalOpen}
        onClose={closeImportModal}
        title="Importer des questions"
      >
        <div className="space-y-4">
          {/* File upload section (shown when no report yet) */}
          {!importReport && (
            <>
              <p className="text-sm text-gray-600">
                Selectionnez un fichier CSV ou JSON contenant les questions a importer.
                Toutes les lignes seront validees avant l'import. En cas d'erreur, aucune question ne sera creee.
              </p>

              <div className="space-y-2">
                <label className="block text-sm font-bold text-gray-700">Fichier (.csv ou .json)</label>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv,.json"
                  onChange={handleImportFileChange}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-bold file:bg-sitou-primary/10 file:text-sitou-primary hover:file:bg-sitou-primary/20 transition-colors"
                />
              </div>

              {importFile && (
                <div className="bg-gray-50 rounded-xl px-4 py-3 text-sm text-gray-700">
                  Fichier : <b>{importFile.name}</b> ({(importFile.size / 1024).toFixed(1)} Ko)
                </div>
              )}

              <div className="bg-blue-50 rounded-xl px-4 py-3 text-xs text-blue-700 space-y-1">
                <p className="font-bold">Format attendu :</p>
                <p><b>CSV :</b> colonnes skill_id, text, correct_answer (obligatoires), question_type, choices (separees par ;), explanation, points</p>
                <p><b>JSON :</b> tableau d'objets avec les memes champs</p>
              </div>

              {importError && (
                <div className="flex items-center text-sm text-red-600 bg-red-50 px-4 py-2 rounded-xl">
                  <AlertCircle size={16} className="mr-2 shrink-0" /> {importError}
                </div>
              )}

              <div className="flex justify-end space-x-3 pt-2">
                <Button variant={ButtonVariant.GHOST} onClick={closeImportModal}>
                  Annuler
                </Button>
                <Button
                  onClick={handleImportSubmit}
                  isLoading={importLoading}
                  disabled={!importFile || importLoading}
                >
                  <Upload size={16} className="mr-1.5" />
                  Lancer l'import
                </Button>
              </div>
            </>
          )}

          {/* Import results */}
          {importReport && (
            <div className="space-y-4">
              {/* Status banner */}
              {importReport.status === 'success' ? (
                <div className="flex items-center bg-green-50 border border-green-200 rounded-xl px-4 py-3">
                  <CheckCircle2 size={20} className="text-green-600 mr-3 shrink-0" />
                  <div>
                    <p className="text-sm font-bold text-green-800">Import reussi</p>
                    <p className="text-xs text-green-600">
                      {importReport.created} question{importReport.created > 1 ? 's' : ''} creee{importReport.created > 1 ? 's' : ''} sur {importReport.total_rows} ligne{importReport.total_rows > 1 ? 's' : ''}.
                    </p>
                  </div>
                </div>
              ) : (
                <div className="flex items-center bg-red-50 border border-red-200 rounded-xl px-4 py-3">
                  <AlertCircle size={20} className="text-red-600 mr-3 shrink-0" />
                  <div>
                    <p className="text-sm font-bold text-red-800">Import echoue — aucune question creee</p>
                    <p className="text-xs text-red-600">
                      {importReport.invalid_rows} erreur{importReport.invalid_rows > 1 ? 's' : ''} sur {importReport.total_rows} ligne{importReport.total_rows > 1 ? 's' : ''}.
                      {importReport.rolled_back && ' Toutes les modifications ont ete annulees.'}
                    </p>
                  </div>
                </div>
              )}

              {/* Stats summary */}
              <div className="grid grid-cols-3 gap-3">
                <div className="bg-gray-50 rounded-xl px-4 py-3 text-center">
                  <p className="text-2xl font-extrabold text-gray-900">{importReport.total_rows}</p>
                  <p className="text-xs text-gray-500">Total lignes</p>
                </div>
                <div className="bg-green-50 rounded-xl px-4 py-3 text-center">
                  <p className="text-2xl font-extrabold text-green-700">{importReport.valid_rows}</p>
                  <p className="text-xs text-green-600">Valides</p>
                </div>
                <div className={`rounded-xl px-4 py-3 text-center ${importReport.invalid_rows > 0 ? 'bg-red-50' : 'bg-gray-50'}`}>
                  <p className={`text-2xl font-extrabold ${importReport.invalid_rows > 0 ? 'text-red-700' : 'text-gray-400'}`}>{importReport.invalid_rows}</p>
                  <p className={`text-xs ${importReport.invalid_rows > 0 ? 'text-red-600' : 'text-gray-400'}`}>Erreurs</p>
                </div>
              </div>

              {/* Errors table */}
              {importReport.errors.length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-bold text-gray-700">Detail des erreurs</h3>
                    <button
                      onClick={downloadErrorReport}
                      className="flex items-center gap-1.5 text-xs font-bold text-sitou-primary hover:underline"
                    >
                      <Download size={14} />
                      Telecharger le rapport d'erreurs
                    </button>
                  </div>
                  <div className="max-h-[40vh] overflow-y-auto border border-gray-200 rounded-xl">
                    <table className="w-full text-sm">
                      <thead className="bg-gray-50 sticky top-0">
                        <tr>
                          <th className="text-left px-4 py-2 text-xs font-bold text-gray-500 w-20">Ligne</th>
                          <th className="text-left px-4 py-2 text-xs font-bold text-gray-500">Message</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100">
                        {importReport.errors.map((err, idx) => (
                          <tr key={idx} className="hover:bg-red-50/50">
                            <td className="px-4 py-2 text-xs font-mono font-bold text-red-600">{err.row}</td>
                            <td className="px-4 py-2 text-xs text-gray-700">{err.message}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex justify-end space-x-3 pt-2">
                {importReport.status === 'failed' && (
                  <Button
                    variant={ButtonVariant.SECONDARY}
                    onClick={() => { setImportReport(null); setImportFile(null); if (fileInputRef.current) fileInputRef.current.value = ''; }}
                  >
                    Reessayer
                  </Button>
                )}
                <Button variant={ButtonVariant.GHOST} onClick={closeImportModal}>
                  Fermer
                </Button>
              </div>
            </div>
          )}
        </div>
      </Modal>

      {/* Batch test modal ("Tester en série") */}
      <Modal
        isOpen={batchTestOpen}
        onClose={closeBatchTest}
        title={batchDone ? 'Résultats du test' : `Test en série — Question ${batchIndex + 1}/${batchQuestions.length}`}
      >
        <div className="space-y-4 max-h-[75vh] overflow-y-auto">
          {batchLoading && (
            <div className="flex flex-col items-center justify-center py-12 gap-3">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sitou-primary" />
              <p className="text-sm text-gray-500">Chargement des questions...</p>
            </div>
          )}

          {!batchLoading && batchQuestions.length === 0 && (
            <p className="text-sm text-gray-500 text-center py-8">Aucune question à tester.</p>
          )}

          {/* Score summary */}
          {!batchLoading && batchDone && batchQuestions.length > 0 && (
            <div className="space-y-4">
              <div className="text-center py-4">
                <div className={`inline-flex items-center justify-center w-20 h-20 rounded-full text-2xl font-black ${
                  batchScore / batchResults.length >= 0.7 ? 'bg-green-100 text-green-700' :
                  batchScore / batchResults.length >= 0.4 ? 'bg-amber-100 text-amber-700' :
                  'bg-red-100 text-red-700'
                }`}>
                  {batchScore}/{batchResults.length}
                </div>
                <p className="text-sm text-gray-500 mt-2">
                  {Math.round(batchScore / batchResults.length * 100)}% de bonnes réponses
                </p>
              </div>

              <div className="space-y-2">
                {batchQuestions.map((q, i) => (
                  <div key={q.id} className={`flex items-center gap-3 p-3 rounded-xl text-sm ${
                    batchResults[i]?.correct ? 'bg-green-50' : 'bg-red-50'
                  }`}>
                    <span className="font-bold text-gray-500 w-6">{i + 1}.</span>
                    {batchResults[i]?.correct ? (
                      <CheckCircle2 size={16} className="text-green-600 shrink-0" />
                    ) : (
                      <AlertCircle size={16} className="text-red-600 shrink-0" />
                    )}
                    <span className="truncate flex-1">{q.prompt}</span>
                    {!batchResults[i]?.correct && (
                      <span className="text-xs text-red-600 shrink-0">→ {String(q.correctAnswer)}</span>
                    )}
                  </div>
                ))}
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <Button variant={ButtonVariant.SECONDARY} onClick={() => { setBatchIndex(0); setBatchAnswer(null); setBatchFeedback(false); setBatchResults([]); setBatchDone(false); }}>
                  <RotateCcw size={14} className="mr-1.5" /> Recommencer
                </Button>
                <Button variant={ButtonVariant.GHOST} onClick={closeBatchTest}>Fermer</Button>
              </div>
            </div>
          )}

          {/* Active question */}
          {!batchLoading && !batchDone && batchQuestions.length > 0 && (
            <>
              {/* Progress bar */}
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-sitou-primary h-2 rounded-full transition-all duration-300"
                    style={{ width: `${((batchIndex) / batchQuestions.length) * 100}%` }}
                  />
                </div>
                <span className="text-xs font-bold text-gray-500">{batchIndex + 1}/{batchQuestions.length}</span>
              </div>

              <div className="bg-sitou-surface rounded-2xl p-4 border border-gray-100">
                <QuestionRenderer
                  question={batchQuestions[batchIndex]}
                  selectedAnswer={batchAnswer}
                  onAnswerChange={batchFeedback ? () => {} : setBatchAnswer}
                  isFeedbackMode={batchFeedback}
                />
              </div>

              {batchFeedback && (
                <div className={`rounded-2xl p-4 animate-slide-up ${
                  batchResults[batchResults.length - 1]?.correct ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
                }`}>
                  <div className="flex items-start">
                    {batchResults[batchResults.length - 1]?.correct ? (
                      <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mr-3 shrink-0">
                        <CheckCircle2 className="text-green-600 w-5 h-5" />
                      </div>
                    ) : (
                      <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center mr-3 shrink-0">
                        <AlertCircle className="text-red-600 w-5 h-5" />
                      </div>
                    )}
                    <div>
                      <h3 className={`font-extrabold text-lg ${batchResults[batchResults.length - 1]?.correct ? 'text-green-700' : 'text-red-700'}`}>
                        {batchResults[batchResults.length - 1]?.correct ? 'Bonne réponse !' : 'Mauvaise réponse'}
                      </h3>
                      {!batchResults[batchResults.length - 1]?.correct && (
                        <p className="text-sm text-gray-700 mt-1">Réponse correcte : <b>{String(batchQuestions[batchIndex].correctAnswer)}</b></p>
                      )}
                      {batchQuestions[batchIndex].explanation && (
                        <p className="text-sm text-gray-600 mt-2">{batchQuestions[batchIndex].explanation}</p>
                      )}
                    </div>
                  </div>
                </div>
              )}

              <div className="flex justify-end gap-3 pt-2">
                {batchFeedback ? (
                  <Button onClick={batchNext}>
                    {batchIndex + 1 >= batchQuestions.length ? 'Voir les résultats' : 'Question suivante'}
                    <ArrowRight size={14} className="ml-1.5" />
                  </Button>
                ) : (
                  <Button onClick={batchValidate} disabled={batchAnswer === null || batchAnswer === ''}>
                    Valider
                  </Button>
                )}
                <Button variant={ButtonVariant.GHOST} onClick={closeBatchTest}>Quitter</Button>
              </div>
            </>
          )}
        </div>
      </Modal>
    </div>
  );
};
