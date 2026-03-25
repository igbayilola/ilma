import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card } from '../../components/ui/Cards';
import { Tabs } from '../../components/ui/Tabs';
import { Modal } from '../../components/ui/Modal';
import { Input } from '../../components/ui/Input';
import { Skeleton } from '../../components/ui/Skeleton';
import {
  teacherService,
  ClassroomDetailDTO,
  AssignmentDTO,
  ClassroomOverviewDTO,
} from '../../services/teacherService';
import {
  Copy,
  Check,
  UserMinus,
  Plus,
  Eye,
  AlertTriangle,
  ArrowLeft,
  Users,
  Calendar,
} from 'lucide-react';

const TABS = [
  { id: 'students', label: 'Élèves' },
  { id: 'assignments', label: 'Devoirs' },
  { id: 'overview', label: "Vue d'ensemble" },
];

export const ClassroomDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [classroom, setClassroom] = useState<ClassroomDetailDTO | null>(null);
  const [assignments, setAssignments] = useState<AssignmentDTO[]>([]);
  const [overview, setOverview] = useState<ClassroomOverviewDTO | null>(null);
  const [activeTab, setActiveTab] = useState('students');
  const [isLoading, setIsLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  // Create assignment modal state
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [assignForm, setAssignForm] = useState({
    title: '',
    skill_id: '',
    deadline: '',
    question_count: '',
  });
  const [assignError, setAssignError] = useState('');
  const [assignCreating, setAssignCreating] = useState(false);

  // Confirm remove student
  const [removingStudent, setRemovingStudent] = useState<string | null>(null);

  const loadClassroom = useCallback(async () => {
    if (!id) return;
    try {
      const data = await teacherService.getClassroom(id);
      setClassroom(data);
    } catch {
      // handle error silently
    }
  }, [id]);

  const loadAssignments = useCallback(async () => {
    if (!id) return;
    try {
      const data = await teacherService.listAssignments(id);
      setAssignments(data);
    } catch {
      setAssignments([]);
    }
  }, [id]);

  const loadOverview = useCallback(async () => {
    if (!id) return;
    try {
      const data = await teacherService.getOverview(id);
      setOverview(data);
    } catch {
      setOverview(null);
    }
  }, [id]);

  useEffect(() => {
    Promise.all([loadClassroom(), loadAssignments(), loadOverview()]).finally(
      () => setIsLoading(false)
    );
  }, [loadClassroom, loadAssignments, loadOverview]);

  const handleCopyCode = () => {
    if (!classroom) return;
    navigator.clipboard.writeText(classroom.invite_code).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const handleRemoveStudent = async (profileId: string) => {
    if (!id) return;
    try {
      await teacherService.removeStudent(id, profileId);
      setClassroom((prev) =>
        prev
          ? {
              ...prev,
              students: prev.students.filter(
                (s) => s.profile_id !== profileId
              ),
              student_count: prev.student_count - 1,
            }
          : prev
      );
    } catch {
      // handle error silently
    }
    setRemovingStudent(null);
  };

  const handleCreateAssignment = async () => {
    if (!assignForm.title.trim()) {
      setAssignError('Le titre est requis.');
      return;
    }
    if (!assignForm.skill_id.trim()) {
      setAssignError("L'identifiant de la compétence est requis.");
      return;
    }
    if (!id) return;

    setAssignCreating(true);
    setAssignError('');
    try {
      const created = await teacherService.createAssignment(id, {
        title: assignForm.title.trim(),
        skill_id: assignForm.skill_id.trim(),
        deadline: assignForm.deadline || undefined,
        question_count: assignForm.question_count
          ? parseInt(assignForm.question_count, 10)
          : undefined,
      });
      setAssignments((prev) => [...prev, created]);
      setShowAssignModal(false);
      setAssignForm({ title: '', skill_id: '', deadline: '', question_count: '' });
    } catch (err: any) {
      setAssignError(err?.message || 'Erreur lors de la création.');
    } finally {
      setAssignCreating(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton variant="text" className="w-48 h-8" />
        <Skeleton variant="rect" className="h-24" />
        <Skeleton variant="rect" className="h-64" />
      </div>
    );
  }

  if (!classroom) {
    return (
      <div className="text-center py-20">
        <p className="text-gray-500 font-medium">Classe introuvable.</p>
        <button
          onClick={() => navigate('/app/teacher/dashboard')}
          className="mt-4 text-sitou-primary font-bold hover:underline"
        >
          Retour au dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back + Header */}
      <button
        onClick={() => navigate('/app/teacher/dashboard')}
        className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 font-medium"
      >
        <ArrowLeft size={16} className="mr-1" />
        Retour
      </button>

      <Card>
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-extrabold text-gray-900">
              {classroom.name}
            </h1>
            <p className="text-gray-500 text-sm mt-1">
              {classroom.student_count || 0} élève
              {(classroom.student_count || 0) !== 1 ? 's' : ''}
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <span className="text-sm text-gray-500">Code d'invitation :</span>
            <button
              onClick={handleCopyCode}
              className="inline-flex items-center space-x-2 bg-gray-100 hover:bg-gray-200 transition-colors px-4 py-2 rounded-xl font-mono font-bold text-gray-800"
            >
              <span>{classroom.invite_code}</span>
              {copied ? (
                <Check size={16} className="text-green-600" />
              ) : (
                <Copy size={16} className="text-gray-400" />
              )}
            </button>
          </div>
        </div>
      </Card>

      {/* Tabs */}
      <Tabs tabs={TABS} activeTab={activeTab} onChange={setActiveTab} />

      {/* Students Tab */}
      {activeTab === 'students' && (
        <div>
          {classroom.students.length === 0 ? (
            <Card className="text-center py-12">
              <Users size={48} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-500 font-medium">Aucun élève inscrit.</p>
              <p className="text-sm text-gray-400 mt-1">
                Partagez le code d'invitation pour que les élèves rejoignent la
                classe.
              </p>
            </Card>
          ) : (
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm divide-y divide-gray-100">
              {classroom.students.map((student) => (
                <div
                  key={student.profile_id}
                  className="flex items-center justify-between px-6 py-4"
                >
                  <div className="flex items-center space-x-3">
                    {student.avatar_url ? (
                      <img
                        src={student.avatar_url}
                        alt=""
                        className="w-10 h-10 rounded-full object-cover"
                      />
                    ) : (
                      <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-500 font-bold text-sm">
                        {student.display_name?.charAt(0)?.toUpperCase() || '?'}
                      </div>
                    )}
                    <div>
                      <p className="font-bold text-gray-800">
                        {student.display_name}
                      </p>
                      <p className="text-xs text-gray-400">
                        Inscrit le{' '}
                        {new Date(student.joined_at).toLocaleDateString(
                          'fr-FR'
                        )}
                      </p>
                    </div>
                  </div>

                  {removingStudent === student.profile_id ? (
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-gray-500">Confirmer ?</span>
                      <button
                        onClick={() =>
                          handleRemoveStudent(student.profile_id)
                        }
                        className="px-3 py-1.5 bg-red-500 text-white text-xs font-bold rounded-lg hover:bg-red-600 transition-colors"
                      >
                        Retirer
                      </button>
                      <button
                        onClick={() => setRemovingStudent(null)}
                        className="px-3 py-1.5 bg-gray-100 text-gray-600 text-xs font-bold rounded-lg hover:bg-gray-200 transition-colors"
                      >
                        Annuler
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() =>
                        setRemovingStudent(student.profile_id)
                      }
                      className="p-2 rounded-lg hover:bg-red-50 text-gray-400 hover:text-red-500 transition-colors"
                      title="Retirer l'élève"
                    >
                      <UserMinus size={18} />
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Assignments Tab */}
      {activeTab === 'assignments' && (
        <div>
          <div className="flex justify-end mb-4">
            <button
              onClick={() => setShowAssignModal(true)}
              className="inline-flex items-center px-4 py-2 rounded-xl gradient-hero text-white font-bold text-sm shadow-clay-sm hover:shadow-clay-hover transition-shadow"
            >
              <Plus size={16} className="mr-2" />
              Nouveau devoir
            </button>
          </div>

          {assignments.length === 0 ? (
            <Card className="text-center py-12">
              <Calendar size={48} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-500 font-medium">
                Aucun devoir pour le moment.
              </p>
            </Card>
          ) : (
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm divide-y divide-gray-100">
              {assignments.map((a) => (
                <div
                  key={a.id}
                  className="flex items-center justify-between px-6 py-4"
                >
                  <div>
                    <p className="font-bold text-gray-800">{a.title}</p>
                    <p className="text-sm text-gray-500">
                      {a.skill_name || `Compétence ${a.skill_id}`}
                      {a.deadline &&
                        ` — Échéance : ${new Date(a.deadline).toLocaleDateString('fr-FR')}`}
                    </p>
                  </div>
                  <button
                    onClick={() =>
                      navigate(`/app/teacher/assignments/${a.id}/results`)
                    }
                    className="inline-flex items-center px-3 py-1.5 bg-sitou-primary-light text-sitou-primary-dark text-sm font-bold rounded-lg hover:bg-amber-200 transition-colors"
                  >
                    <Eye size={14} className="mr-1.5" />
                    Voir résultats
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <p className="text-sm font-bold text-gray-500 uppercase tracking-wide">
                Score moyen
              </p>
              <p className="text-3xl font-extrabold text-gray-900 mt-1">
                {overview?.avg_score ?? '—'}%
              </p>
            </Card>
            <Card>
              <p className="text-sm font-bold text-gray-500 uppercase tracking-wide">
                Élèves actifs
              </p>
              <p className="text-3xl font-extrabold text-gray-900 mt-1">
                {overview?.active_students ?? '—'}
              </p>
            </Card>
            <Card>
              <p className="text-sm font-bold text-gray-500 uppercase tracking-wide">
                En difficulté
              </p>
              <p className="text-3xl font-extrabold text-orange-500 mt-1">
                {overview?.students_in_difficulty?.length ?? 0}
              </p>
            </Card>
          </div>

          {overview?.students_in_difficulty &&
            overview.students_in_difficulty.length > 0 && (
              <section>
                <h3 className="font-bold text-gray-800 mb-3 flex items-center">
                  <AlertTriangle
                    size={18}
                    className="mr-2 text-orange-500"
                  />
                  Élèves en difficulté
                </h3>
                <div className="bg-white rounded-2xl border border-gray-200 shadow-sm divide-y divide-gray-100">
                  {overview.students_in_difficulty.map((s, i) => (
                    <div
                      key={`${s.profile_id}-${i}`}
                      className="flex items-center justify-between px-6 py-4"
                    >
                      <p className="font-medium text-gray-800">
                        {s.display_name}
                      </p>
                      <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-bold">
                        {s.avg_score}%
                      </span>
                    </div>
                  ))}
                </div>
              </section>
            )}
        </div>
      )}

      {/* Create Assignment Modal */}
      <Modal
        isOpen={showAssignModal}
        onClose={() => {
          setShowAssignModal(false);
          setAssignError('');
          setAssignForm({
            title: '',
            skill_id: '',
            deadline: '',
            question_count: '',
          });
        }}
        title="Nouveau devoir"
      >
        <div className="space-y-4">
          <Input
            label="Titre"
            placeholder="Ex : Exercice fractions"
            value={assignForm.title}
            onChange={(e) =>
              setAssignForm((f) => ({ ...f, title: e.target.value }))
            }
          />
          <Input
            label="Compétence (ID)"
            placeholder="Identifiant de la compétence"
            value={assignForm.skill_id}
            onChange={(e) =>
              setAssignForm((f) => ({ ...f, skill_id: e.target.value }))
            }
          />
          <Input
            label="Date limite (optionnel)"
            type="date"
            value={assignForm.deadline}
            onChange={(e) =>
              setAssignForm((f) => ({ ...f, deadline: e.target.value }))
            }
          />
          <Input
            label="Nombre de questions (optionnel)"
            type="number"
            placeholder="10"
            value={assignForm.question_count}
            onChange={(e) =>
              setAssignForm((f) => ({
                ...f,
                question_count: e.target.value,
              }))
            }
          />
          {assignError && (
            <p className="text-sm text-red-500 font-medium">{assignError}</p>
          )}
          <button
            onClick={handleCreateAssignment}
            disabled={assignCreating}
            className="w-full py-3 rounded-xl gradient-hero text-white font-bold shadow-clay-sm hover:shadow-clay-hover transition-shadow disabled:opacity-50"
          >
            {assignCreating ? 'Création...' : 'Créer le devoir'}
          </button>
        </div>
      </Modal>
    </div>
  );
};
