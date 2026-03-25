import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { Modal } from '../../components/ui/Modal';
import { ButtonVariant } from '../../types';
import { ChevronRight, ChevronDown, FileJson, Plus, AlertCircle, CheckCircle2, BookOpen, Layers, Target, Sparkles, Trash2, Download } from 'lucide-react';
import {
  contentService,
  GradeLevelDTO,
  CurriculumImportResult,
  TreeGradeDTO,
  TreeSubjectDTO,
  TreeDomainDTO,
  TreeSkillDTO,
  TreeMicroSkillDTO,
} from '../../services/contentService';

function slugify(text: string): string {
  return text.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
}

// ── Collapsible tree node wrapper ───────────────────────
function TreeNode({ label, badge, detail, icon, depth, defaultOpen = false, actions, children }: {
  label: React.ReactNode;
  badge?: React.ReactNode;
  detail?: React.ReactNode;
  icon?: React.ReactNode;
  depth: number;
  defaultOpen?: boolean;
  actions?: React.ReactNode;
  children?: React.ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);
  const hasChildren = !!children;
  const indent = depth * 24;

  return (
    <div>
      <div
        className={`w-full flex items-center gap-2 px-4 py-2.5 text-left hover:bg-gray-50 transition-colors rounded-xl group ${hasChildren ? 'cursor-pointer' : 'cursor-default'}`}
        style={{ paddingLeft: `${16 + indent}px` }}
        onClick={() => hasChildren && setOpen(!open)}
        role={hasChildren ? 'button' : undefined}
        aria-expanded={hasChildren ? open : undefined}
      >
        {hasChildren ? (
          open ? <ChevronDown size={16} className="text-gray-400 shrink-0" /> : <ChevronRight size={16} className="text-gray-400 shrink-0" />
        ) : (
          <span className="w-4 shrink-0" />
        )}
        {icon && <span className="shrink-0">{icon}</span>}
        <span className="font-medium text-gray-900 truncate">{label}</span>
        {badge && <span className="shrink-0">{badge}</span>}
        {detail && <span className="ml-auto text-xs text-gray-400 shrink-0 hidden sm:inline">{detail}</span>}
        {actions && <span className="ml-auto shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" onClick={e => e.stopPropagation()}>{actions}</span>}
      </div>
      {open && hasChildren && (
        <div>{children}</div>
      )}
    </div>
  );
}

// ── Badge pill ──────────────────────────────────────────
function Badge({ count, label, color = 'gray' }: { count: number; label: string; color?: string }) {
  const colors: Record<string, string> = {
    gray: 'bg-gray-100 text-gray-600',
    blue: 'bg-blue-100 text-blue-700',
    purple: 'bg-purple-100 text-purple-700',
    green: 'bg-green-100 text-green-700',
    amber: 'bg-amber-100 text-amber-700',
  };
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${colors[color] || colors.gray}`}>
      {count} {label}
    </span>
  );
}

// ── MicroSkill leaf node ────────────────────────────────
function MicroSkillNode({ ms, depth }: { ms: TreeMicroSkillDTO; depth: number }) {
  const indent = depth * 24;
  return (
    <div
      className="flex items-center gap-2 px-4 py-2 hover:bg-gray-50 rounded-xl"
      style={{ paddingLeft: `${16 + indent + 20}px` }}
    >
      <Sparkles size={14} className="text-amber-400 shrink-0" />
      <span className="text-sm text-gray-800 truncate">{ms.name}</span>
      {ms.external_id && (
        <span className="text-[11px] font-mono text-gray-400 shrink-0">{ms.external_id}</span>
      )}
      {ms.difficulty_index != null && (
        <span className="text-[11px] text-gray-400 shrink-0">diff:{ms.difficulty_index}</span>
      )}
      {ms.bloom_taxonomy_level && (
        <span className="text-[11px] text-purple-400 shrink-0">{ms.bloom_taxonomy_level}</span>
      )}
      {ms.cep_frequency != null && (
        <span className="text-[11px] text-blue-400 shrink-0">CEP:{ms.cep_frequency}%</span>
      )}
    </div>
  );
}

// ── Skill node ──────────────────────────────────────────
function SkillNode({ skill, depth }: { skill: TreeSkillDTO; depth: number }) {
  const detail = [
    skill.external_id,
    skill.cep_frequency != null ? `CEP:${skill.cep_frequency}%` : null,
    skill.mastery_threshold,
  ].filter(Boolean).join(' · ');

  return (
    <TreeNode
      label={skill.name}
      icon={<Target size={14} className="text-green-500" />}
      badge={skill.micro_skills.length > 0 ? <Badge count={skill.micro_skills.length} label="micro" color="amber" /> : undefined}
      detail={detail || undefined}
      depth={depth}
    >
      {skill.micro_skills.length > 0
        ? skill.micro_skills.map(ms => <MicroSkillNode key={ms.id} ms={ms} depth={depth + 1} />)
        : undefined}
    </TreeNode>
  );
}

// ── Domain node ─────────────────────────────────────────
function DomainNode({ domain, depth }: { domain: TreeDomainDTO; depth: number }) {
  return (
    <TreeNode
      label={domain.name}
      icon={<Layers size={14} className="text-purple-500" />}
      badge={<Badge count={domain.skills.length} label="comp." color="green" />}
      depth={depth}
    >
      {domain.skills.length > 0
        ? domain.skills.map(sk => <SkillNode key={sk.id} skill={sk} depth={depth + 1} />)
        : undefined}
    </TreeNode>
  );
}

// ── Subject node ────────────────────────────────────────
function SubjectNode({ subject, depth, onDelete }: { subject: TreeSubjectDTO; depth: number; onDelete?: (id: string, name: string) => void }) {
  const domainCount = subject.domains.length;
  return (
    <TreeNode
      label={subject.name}
      icon={
        subject.color
          ? <span className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: subject.color }} />
          : <BookOpen size={14} className="text-blue-500" />
      }
      badge={<Badge count={domainCount} label="dom." color="blue" />}
      depth={depth}
      defaultOpen
      actions={onDelete && (
        <button
          type="button"
          onClick={() => onDelete(subject.id, subject.name)}
          className="p-1 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors"
          aria-label={`Supprimer ${subject.name}`}
          title="Supprimer cette matiere"
        >
          <Trash2 size={14} />
        </button>
      )}
    >
      {subject.domains.length > 0
        ? subject.domains.map(d => <DomainNode key={d.id} domain={d} depth={depth + 1} />)
        : undefined}
    </TreeNode>
  );
}

export const AdminContentPage: React.FC = () => {
  const [grades, setGrades] = useState<GradeLevelDTO[]>([]);
  const [selectedGradeId, setSelectedGradeId] = useState<string>('');
  const [tree, setTree] = useState<TreeGradeDTO[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Create modals
  const [showCreateGrade, setShowCreateGrade] = useState(false);
  const [showCreateSubject, setShowCreateSubject] = useState(false);
  const [formName, setFormName] = useState('');
  const [formDescription, setFormDescription] = useState('');
  const [formGradeId, setFormGradeId] = useState('');
  const [formSaving, setFormSaving] = useState(false);
  const [formError, setFormError] = useState('');

  // Delete confirmation state
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<{ type: 'grade' | 'subject'; id: string; name: string } | null>(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deleteError, setDeleteError] = useState('');

  // Curriculum import state
  const [showCurriculumModal, setShowCurriculumModal] = useState(false);
  const [curriculumFile, setCurriculumFile] = useState<File | null>(null);
  const [curriculumPreview, setCurriculumPreview] = useState<{ subjects: number; domains: number; skills: number; micro_skills: number } | null>(null);
  const [curriculumLoading, setCurriculumLoading] = useState(false);
  const [curriculumResult, setCurriculumResult] = useState<CurriculumImportResult | null>(null);
  const [curriculumError, setCurriculumError] = useState('');
  const curriculumFileRef = useRef<HTMLInputElement>(null);

  // Export state
  const [showExportModal, setShowExportModal] = useState(false);
  const [exportCheckedDomains, setExportCheckedDomains] = useState<Set<string>>(new Set());

  // Load grades list for selector
  useEffect(() => {
    contentService.listGradeLevels().then(g => {
      setGrades(g);
      if (g.length > 0 && !selectedGradeId) setSelectedGradeId(g[0].id);
    }).catch(() => {});
  }, []);

  const loadTree = useCallback(() => {
    setIsLoading(true);
    contentService.getCurriculumTree(selectedGradeId || undefined)
      .then(setTree)
      .catch(() => setTree([]))
      .finally(() => setIsLoading(false));
  }, [selectedGradeId]);

  useEffect(() => { loadTree(); }, [loadTree]);

  // ── Create Grade ──────────────────────────────────────
  const openCreateGrade = () => {
    setFormName(''); setFormDescription(''); setFormError('');
    setShowCreateGrade(true);
  };

  const handleCreateGrade = async () => {
    if (!formName.trim()) { setFormError('Le nom est obligatoire.'); return; }
    setFormSaving(true); setFormError('');
    try {
      await contentService.createGradeLevel({ name: formName.trim(), slug: slugify(formName), description: formDescription.trim() || undefined });
      setShowCreateGrade(false);
      const g = await contentService.listGradeLevels();
      setGrades(g);
      loadTree();
    } catch (err: any) {
      setFormError(err?.message || 'Erreur lors de la creation.');
    } finally {
      setFormSaving(false);
    }
  };

  // ── Create Subject ────────────────────────────────────
  const openCreateSubject = () => {
    setFormName(''); setFormDescription(''); setFormGradeId(selectedGradeId); setFormError('');
    setShowCreateSubject(true);
  };

  const handleCreateSubject = async () => {
    if (!formName.trim()) { setFormError('Le nom est obligatoire.'); return; }
    setFormSaving(true); setFormError('');
    try {
      await contentService.createSubject({ name: formName.trim(), slug: slugify(formName), description: formDescription.trim() || undefined, grade_level_id: formGradeId || undefined });
      setShowCreateSubject(false);
      loadTree();
    } catch (err: any) {
      setFormError(err?.message || 'Erreur lors de la creation.');
    } finally {
      setFormSaving(false);
    }
  };

  // ── Delete Grade / Subject ──────────────────────────────
  const askDeleteGrade = (id: string, name: string) => {
    setDeleteTarget({ type: 'grade', id, name });
    setDeleteError('');
    setShowDeleteModal(true);
  };

  const askDeleteSubject = (id: string, name: string) => {
    setDeleteTarget({ type: 'subject', id, name });
    setDeleteError('');
    setShowDeleteModal(true);
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleteLoading(true);
    setDeleteError('');
    try {
      if (deleteTarget.type === 'grade') {
        await contentService.deleteGradeLevel(deleteTarget.id);
        const g = await contentService.listGradeLevels();
        setGrades(g);
        if (selectedGradeId === deleteTarget.id) setSelectedGradeId(g[0]?.id || '');
      } else {
        await contentService.deleteSubject(deleteTarget.id);
      }
      setShowDeleteModal(false);
      setDeleteTarget(null);
      loadTree();
    } catch (err: any) {
      setDeleteError(err?.message || 'Erreur lors de la suppression.');
    } finally {
      setDeleteLoading(false);
    }
  };

  // ── Curriculum Import ─────────────────────────────────
  const openCurriculumModal = () => {
    setCurriculumFile(null);
    setCurriculumPreview(null);
    setCurriculumResult(null);
    setCurriculumError('');
    setShowCurriculumModal(true);
  };

  const handleCurriculumFileChange = (file: File | null) => {
    setCurriculumFile(file);
    setCurriculumPreview(null);
    setCurriculumResult(null);
    setCurriculumError('');
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const json = JSON.parse(e.target?.result as string);
        let subjects = 0, domains = 0, skillsCount = 0, msCount = 0;
        for (const s of (json.subjects || [])) {
          subjects++;
          for (const d of (s.domains || [])) {
            domains++;
            for (const sk of (d.skills || [])) {
              skillsCount++;
              msCount += (sk.micro_skills || []).length;
            }
          }
        }
        setCurriculumPreview({ subjects, domains, skills: skillsCount, micro_skills: msCount });
      } catch {
        setCurriculumError('Fichier JSON invalide.');
      }
    };
    reader.readAsText(file);
  };

  const handleCurriculumImport = async () => {
    if (!curriculumFile) { setCurriculumError('Selectionnez un fichier JSON.'); return; }
    setCurriculumLoading(true);
    setCurriculumError('');
    setCurriculumResult(null);
    try {
      const result = await contentService.importCurriculumFile(curriculumFile);
      setCurriculumResult(result);
      // Refresh grades list + tree
      const g = await contentService.listGradeLevels();
      setGrades(g);
      loadTree();
    } catch (err: any) {
      setCurriculumError(err?.message || "Erreur lors de l'import.");
    } finally {
      setCurriculumLoading(false);
    }
  };

  // ── Curriculum Export ─────────────────────────────────
  const openExportModal = () => {
    if (tree.length === 0) return;
    const gradeData = tree[0];
    const allDomainIds = new Set<string>();
    for (const subject of gradeData.subjects) {
      for (const domain of subject.domains) {
        allDomainIds.add(domain.id);
      }
    }
    setExportCheckedDomains(allDomainIds);
    setShowExportModal(true);
  };

  const toggleExportDomain = (domainId: string) => {
    setExportCheckedDomains(prev => {
      const next = new Set(prev);
      if (next.has(domainId)) next.delete(domainId);
      else next.add(domainId);
      return next;
    });
  };

  const toggleAllExportDomains = (selectAll: boolean) => {
    if (selectAll && tree.length > 0) {
      const allDomainIds = new Set<string>();
      for (const subject of tree[0].subjects) {
        for (const domain of subject.domains) {
          allDomainIds.add(domain.id);
        }
      }
      setExportCheckedDomains(allDomainIds);
    } else {
      setExportCheckedDomains(new Set());
    }
  };

  const handleExportDownload = () => {
    if (tree.length === 0) return;
    const gradeData = tree[0];

    const exportJson = {
      schema_version: "2.0",
      grade: {
        name: gradeData.name,
        slug: gradeData.slug,
        description: gradeData.description || "",
      },
      subjects: gradeData.subjects
        .map(subject => {
          const filteredDomains = subject.domains.filter(d => exportCheckedDomains.has(d.id));
          if (filteredDomains.length === 0) return null;
          return {
            name: subject.name,
            slug: subject.slug,
            icon: subject.icon || undefined,
            color: subject.color || undefined,
            order: subject.order,
            domains: filteredDomains.map(domain => ({
              name: domain.name,
              slug: domain.slug,
              order: domain.order,
              skills: domain.skills.map(skill => ({
                external_id: skill.external_id || "",
                name: skill.name,
                order: skill.order,
                cep_frequency: skill.cep_frequency ?? undefined,
                prerequisites: skill.prerequisites || [],
                common_mistakes: skill.common_mistakes || [],
                exercise_types: skill.exercise_types || [],
                mastery_threshold: skill.mastery_threshold || undefined,
                micro_skills: skill.micro_skills.map(ms => ({
                  external_id: ms.external_id || "",
                  name: ms.name,
                  order: ms.order,
                  difficulty_index: ms.difficulty_index ?? undefined,
                  bloom_taxonomy_level: ms.bloom_taxonomy_level || undefined,
                  mastery_threshold: ms.mastery_threshold || undefined,
                  cep_frequency: ms.cep_frequency ?? undefined,
                  prerequisites: [],
                  recommended_exercise_types: [],
                  external_prerequisites: ms.external_prerequisites || [],
                })),
              })),
            })),
          };
        })
        .filter(Boolean),
    };

    const blob = new Blob([JSON.stringify(exportJson, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `curriculum-${gradeData.slug}-export.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setShowExportModal(false);
  };

  // Stats summary
  const totalSubjects = tree.reduce((acc, g) => acc + g.subjects.length, 0);
  const totalDomains = tree.reduce((acc, g) => acc + g.subjects.reduce((a, s) => a + s.domains.length, 0), 0);
  const totalSkills = tree.reduce((acc, g) => acc + g.subjects.reduce((a, s) => a + s.domains.reduce((a2, d) => a2 + d.skills.length, 0), 0), 0);
  const totalMicroSkills = tree.reduce((acc, g) => acc + g.subjects.reduce((a, s) => a + s.domains.reduce((a2, d) => a2 + d.skills.reduce((a3, sk) => a3 + sk.micro_skills.length, 0), 0), 0), 0);

  // Export computed values
  const exportGrade = tree.length > 0 ? tree[0] : null;
  let exportDomainCount = 0, exportSkillCount = 0, exportMicroSkillCount = 0, exportTotalDomains = 0;
  if (exportGrade) {
    for (const subject of exportGrade.subjects) {
      for (const domain of subject.domains) {
        exportTotalDomains++;
        if (exportCheckedDomains.has(domain.id)) {
          exportDomainCount++;
          exportSkillCount += domain.skills.length;
          for (const skill of domain.skills) {
            exportMicroSkillCount += skill.micro_skills.length;
          }
        }
      }
    }
  }
  const allExportDomainsChecked = exportTotalDomains > 0 && exportDomainCount === exportTotalDomains;

  return (
    <div className="space-y-6 h-[calc(100vh-140px)] flex flex-col overflow-hidden">
      {/* ── Header ─────────────────────────────────────── */}
      <header className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 flex-shrink-0">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900">Gestion du Contenu</h1>
          <p className="text-gray-500 text-sm">Arbre pedagogique : classes, matieres, domaines, competences et micro-competences.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant={ButtonVariant.SECONDARY} leftIcon={<Download size={18} />} onClick={openExportModal} disabled={tree.length === 0 || isLoading}>
            Exporter
          </Button>
          <Button variant={ButtonVariant.SECONDARY} leftIcon={<FileJson size={18} />} onClick={openCurriculumModal}>
            Import Programme
          </Button>
          <Button variant={ButtonVariant.SECONDARY} onClick={openCreateGrade}>
            + Classe
          </Button>
          <Button onClick={openCreateSubject}>
            + Matiere
          </Button>
        </div>
      </header>

      {/* ── Grade selector + stats ────────────────────── */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 flex-shrink-0">
        {grades.length > 0 && (
          <div className="flex items-center gap-2">
            <label className="text-sm font-bold text-gray-700">Classe :</label>
            <select
              value={selectedGradeId}
              onChange={e => setSelectedGradeId(e.target.value)}
              className="px-3 py-2 rounded-xl border border-gray-200 focus:ring-2 focus:ring-sitou-primary/20 focus:border-sitou-primary text-sm"
            >
              <option value="">Toutes les classes</option>
              {grades.map(g => <option key={g.id} value={g.id}>{g.name}</option>)}
            </select>
          </div>
        )}
        {!isLoading && (
          <div className="flex gap-3 text-xs text-gray-500">
            <span>{totalSubjects} matiere{totalSubjects > 1 ? 's' : ''}</span>
            <span>{totalDomains} domaine{totalDomains > 1 ? 's' : ''}</span>
            <span>{totalSkills} competence{totalSkills > 1 ? 's' : ''}</span>
            <span>{totalMicroSkills} micro-comp.</span>
          </div>
        )}
      </div>

      {/* ── Tree ──────────────────────────────────────── */}
      {isLoading ? (
        <Skeleton variant="rect" className="h-64" />
      ) : tree.length === 0 ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center text-gray-400">
            <BookOpen size={48} className="mx-auto mb-3 opacity-50" />
            <p className="font-medium">Aucun contenu</p>
            <p className="text-sm">Importez un programme ou creez une classe pour commencer.</p>
          </div>
        </div>
      ) : (
        <div className="flex-1 min-h-0 overflow-y-auto rounded-2xl border border-gray-100 bg-white divide-y divide-gray-50">
          {tree.map(grade => (
            <div key={grade.id}>
              {/* Grade header */}
              <div className="px-4 py-3 bg-gray-50 border-b border-gray-100 flex items-center justify-between group">
                <h2 className="text-sm font-extrabold text-gray-700 uppercase tracking-wide">
                  {grade.name}
                  {grade.description && <span className="ml-2 font-normal text-gray-400 normal-case">{grade.description}</span>}
                </h2>
                <button
                  type="button"
                  onClick={() => askDeleteGrade(grade.id, grade.name)}
                  className="p-1 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors opacity-0 group-hover:opacity-100"
                  aria-label={`Supprimer ${grade.name}`}
                  title="Supprimer cette classe"
                >
                  <Trash2 size={14} />
                </button>
              </div>
              {/* Subjects under this grade */}
              {grade.subjects.length === 0 ? (
                <div className="px-6 py-4 text-sm text-gray-400 italic">Aucune matiere dans cette classe.</div>
              ) : (
                grade.subjects.map(subject => (
                  <SubjectNode key={subject.id} subject={subject} depth={0} onDelete={askDeleteSubject} />
                ))
              )}
            </div>
          ))}
        </div>
      )}

      {/* ── Create Grade Modal ────────────────────────── */}
      <Modal isOpen={showCreateGrade} onClose={() => setShowCreateGrade(false)} title="Nouvelle Classe">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-1">Nom *</label>
            <input
              type="text"
              value={formName}
              onChange={e => setFormName(e.target.value)}
              placeholder="Ex: CM2"
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-sitou-primary/20 focus:border-sitou-primary text-sm"
            />
            {formName && <p className="text-xs text-gray-400 mt-1">Slug : {slugify(formName)}</p>}
          </div>
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-1">Description</label>
            <textarea
              value={formDescription}
              onChange={e => setFormDescription(e.target.value)}
              rows={2}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-sitou-primary/20 focus:border-sitou-primary text-sm resize-none"
            />
          </div>
          {formError && (
            <div className="flex items-center text-sm text-red-600 bg-red-50 px-4 py-2 rounded-xl">
              <AlertCircle size={16} className="mr-2 shrink-0" /> {formError}
            </div>
          )}
          <div className="flex justify-end space-x-3 pt-2">
            <Button variant={ButtonVariant.GHOST} onClick={() => setShowCreateGrade(false)}>Annuler</Button>
            <Button onClick={handleCreateGrade} isLoading={formSaving}>Creer</Button>
          </div>
        </div>
      </Modal>

      {/* ── Create Subject Modal ──────────────────────── */}
      <Modal isOpen={showCreateSubject} onClose={() => setShowCreateSubject(false)} title="Nouvelle Matiere">
        <div className="space-y-4">
          {grades.length > 0 && (
            <div>
              <label className="block text-sm font-bold text-gray-700 mb-1">Classe</label>
              <select
                value={formGradeId}
                onChange={e => setFormGradeId(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-sitou-primary/20 focus:border-sitou-primary text-sm"
              >
                <option value="">— Aucune classe —</option>
                {grades.map(g => <option key={g.id} value={g.id}>{g.name}</option>)}
              </select>
            </div>
          )}
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-1">Nom *</label>
            <input
              type="text"
              value={formName}
              onChange={e => setFormName(e.target.value)}
              placeholder="Ex: Mathematiques"
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-sitou-primary/20 focus:border-sitou-primary text-sm"
            />
            {formName && <p className="text-xs text-gray-400 mt-1">Slug : {slugify(formName)}</p>}
          </div>
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-1">Description</label>
            <textarea
              value={formDescription}
              onChange={e => setFormDescription(e.target.value)}
              rows={2}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-sitou-primary/20 focus:border-sitou-primary text-sm resize-none"
            />
          </div>
          {formError && (
            <div className="flex items-center text-sm text-red-600 bg-red-50 px-4 py-2 rounded-xl">
              <AlertCircle size={16} className="mr-2 shrink-0" /> {formError}
            </div>
          )}
          <div className="flex justify-end space-x-3 pt-2">
            <Button variant={ButtonVariant.GHOST} onClick={() => setShowCreateSubject(false)}>Annuler</Button>
            <Button onClick={handleCreateSubject} isLoading={formSaving}>Creer</Button>
          </div>
        </div>
      </Modal>

      {/* ── Delete Confirmation Modal ────────────────── */}
      <Modal isOpen={showDeleteModal} onClose={() => setShowDeleteModal(false)} title="Confirmer la suppression">
        <div className="space-y-4">
          <p className="text-sm text-gray-700">
            Supprimer <b>{deleteTarget?.type === 'grade' ? 'la classe' : 'la matiere'} "{deleteTarget?.name}"</b> ?
            {deleteTarget?.type === 'grade'
              ? ' Toutes les matieres, domaines, competences et micro-competences associees seront egalement supprimes.'
              : ' Tous les domaines, competences et micro-competences associees seront egalement supprimes.'}
          </p>
          <p className="text-xs text-red-500 font-medium">Cette action est irreversible.</p>

          {deleteError && (
            <div className="flex items-center text-sm text-red-600 bg-red-50 px-4 py-2 rounded-xl">
              <AlertCircle size={16} className="mr-2 shrink-0" /> {deleteError}
            </div>
          )}

          <div className="flex justify-end space-x-3 pt-2">
            <Button variant={ButtonVariant.GHOST} onClick={() => setShowDeleteModal(false)}>Annuler</Button>
            <Button variant={ButtonVariant.DANGER} onClick={handleDelete} isLoading={deleteLoading}>
              Supprimer
            </Button>
          </div>
        </div>
      </Modal>

      {/* ── Curriculum Import Modal ───────────────────── */}
      <Modal isOpen={showCurriculumModal} onClose={() => setShowCurriculumModal(false)} title="Importer un programme (JSON)">
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Importez un fichier JSON au format v2.0 contenant l'arbre complet : classe, matieres, domaines, competences et micro-competences.
          </p>

          <div
            className="border-2 border-dashed border-gray-200 rounded-2xl p-8 text-center cursor-pointer hover:border-sitou-primary hover:bg-sitou-primary-light/30 transition-colors"
            onClick={() => curriculumFileRef.current?.click()}
          >
            <FileJson size={32} className="mx-auto text-gray-400 mb-2" />
            {curriculumFile ? (
              <p className="text-sm font-bold text-gray-800">{curriculumFile.name}</p>
            ) : (
              <p className="text-sm text-gray-500">Cliquez pour selectionner un fichier JSON</p>
            )}
            <input
              ref={curriculumFileRef}
              type="file"
              accept=".json"
              className="hidden"
              onChange={e => handleCurriculumFileChange(e.target.files?.[0] || null)}
            />
          </div>

          {curriculumPreview && !curriculumResult && (
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
              <p className="text-sm font-bold text-blue-800 mb-2">Apercu du fichier :</p>
              <div className="grid grid-cols-2 gap-2 text-sm text-blue-700">
                <span>Matieres : <b>{curriculumPreview.subjects}</b></span>
                <span>Domaines : <b>{curriculumPreview.domains}</b></span>
                <span>Competences : <b>{curriculumPreview.skills}</b></span>
                <span>Micro-competences : <b>{curriculumPreview.micro_skills}</b></span>
              </div>
            </div>
          )}

          {curriculumResult && (
            <div className="bg-green-50 border border-green-200 rounded-xl p-4">
              <div className="flex items-center text-green-700 font-bold text-sm mb-2">
                <CheckCircle2 size={16} className="mr-2" /> Import termine
              </div>
              <div className="grid grid-cols-2 gap-1 text-sm text-green-700">
                <span>Crees : <b>{curriculumResult.created}</b></span>
                <span>Mis a jour : <b>{curriculumResult.updated}</b></span>
                <span>Matieres : {curriculumResult.subjects}</span>
                <span>Domaines : {curriculumResult.domains}</span>
                <span>Competences : {curriculumResult.skills}</span>
                <span>Micro-competences : {curriculumResult.micro_skills}</span>
              </div>
              {curriculumResult.errors.length > 0 && (
                <div className="mt-2 text-xs text-red-600 space-y-1 max-h-32 overflow-y-auto">
                  {curriculumResult.errors.map((e, i) => (
                    <p key={i}>{e.error}</p>
                  ))}
                </div>
              )}
            </div>
          )}

          {curriculumError && (
            <div className="flex items-center text-sm text-red-600 bg-red-50 px-4 py-2 rounded-xl">
              <AlertCircle size={16} className="mr-2 shrink-0" /> {curriculumError}
            </div>
          )}

          <div className="flex justify-end space-x-3 pt-2">
            <Button variant={ButtonVariant.GHOST} onClick={() => setShowCurriculumModal(false)}>Fermer</Button>
            <Button onClick={handleCurriculumImport} isLoading={curriculumLoading} disabled={!curriculumFile || curriculumLoading || !!curriculumResult}>
              Importer
            </Button>
          </div>
        </div>
      </Modal>

      {/* ── Export Modal ────────────────────────────────── */}
      <Modal isOpen={showExportModal} onClose={() => setShowExportModal(false)} title="Exporter le programme">
        <div className="space-y-4">
          {/* Grade info (read-only) */}
          {exportGrade && (
            <div className="bg-gray-50 rounded-xl px-4 py-3">
              <p className="text-sm text-gray-600">
                Classe : <b className="text-gray-900">{exportGrade.name}</b>
                {exportGrade.subjects.length > 0 && (
                  <span className="ml-2 text-gray-400">
                    — {exportGrade.subjects.map(s => s.name).join(', ')}
                  </span>
                )}
              </p>
            </div>
          )}

          {/* Toggle all link */}
          <div className="flex justify-between items-center">
            <p className="text-sm font-bold text-gray-700">Domaines a inclure</p>
            <button
              type="button"
              onClick={() => toggleAllExportDomains(!allExportDomainsChecked)}
              className="text-xs text-sitou-primary hover:underline font-medium"
            >
              {allExportDomainsChecked ? 'Tout decocher' : 'Tout cocher'}
            </button>
          </div>

          {/* Domain checkboxes per subject */}
          <div className="max-h-64 overflow-y-auto space-y-3 -mx-2 px-2">
            {exportGrade?.subjects.map(subject => (
              <div key={subject.id}>
                <p className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">{subject.name}</p>
                {subject.domains.map(domain => {
                  const skillCount = domain.skills.length;
                  const msCount = domain.skills.reduce((a, s) => a + s.micro_skills.length, 0);
                  return (
                    <label key={domain.id} className="flex items-center gap-3 px-3 py-2 hover:bg-gray-50 rounded-lg cursor-pointer">
                      <input
                        type="checkbox"
                        checked={exportCheckedDomains.has(domain.id)}
                        onChange={() => toggleExportDomain(domain.id)}
                        className="rounded border-gray-300 text-sitou-primary focus:ring-sitou-primary/20 shrink-0"
                      />
                      <span className="text-sm text-gray-800 flex-1 truncate">{domain.name}</span>
                      <span className="text-[11px] text-gray-400 shrink-0">{skillCount} comp. · {msCount} micro</span>
                    </label>
                  );
                })}
              </div>
            ))}
          </div>

          {/* Dynamic summary */}
          <div className="bg-blue-50 rounded-xl px-4 py-3 text-sm text-blue-700">
            <b>{exportDomainCount}</b> domaine{exportDomainCount > 1 ? 's' : ''}, <b>{exportSkillCount}</b> competence{exportSkillCount > 1 ? 's' : ''}, <b>{exportMicroSkillCount}</b> micro-competence{exportMicroSkillCount > 1 ? 's' : ''}
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-2">
            <Button variant={ButtonVariant.GHOST} onClick={() => setShowExportModal(false)}>Annuler</Button>
            <Button onClick={handleExportDownload} disabled={exportCheckedDomains.size === 0} leftIcon={<Download size={16} />}>
              Telecharger JSON
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
