import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../../components/ui/Cards';
import { Modal } from '../../components/ui/Modal';
import { Input } from '../../components/ui/Input';
import { Skeleton } from '../../components/ui/Skeleton';
import { useAuthStore } from '../../store/authStore';
import {
  teacherService,
  ClassroomDTO,
  AlertStudentDTO,
} from '../../services/teacherService';
import { ClassInviteShare } from '../../components/teacher/ClassInviteShare';
import {
  Users,
  School,
  AlertTriangle,
  Plus,
  ChevronRight,
} from 'lucide-react';

const StatCard = ({
  title,
  value,
  icon,
  color,
}: {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
}) => (
  <Card className="flex flex-col justify-between h-32 relative overflow-hidden">
    <div className="flex justify-between items-start z-10">
      <div>
        <p className="text-sm font-bold text-gray-500 uppercase tracking-wide">
          {title}
        </p>
        <h3 className="text-2xl font-extrabold text-gray-900 mt-1">{value}</h3>
      </div>
      <div className={`p-2 rounded-lg ${color} text-white shadow-md`}>
        {icon}
      </div>
    </div>
    <div
      className={`absolute -bottom-4 -right-4 w-24 h-24 rounded-full opacity-10 ${color}`}
    />
  </Card>
);

export const TeacherDashboard: React.FC = () => {
  const { user } = useAuthStore();
  const navigate = useNavigate();

  const [classrooms, setClassrooms] = useState<ClassroomDTO[]>([]);
  const [alerts, setAlerts] = useState<AlertStudentDTO[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newClassName, setNewClassName] = useState('');
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState('');

  useEffect(() => {
    Promise.all([
      teacherService.listClassrooms().catch(() => [] as ClassroomDTO[]),
      teacherService.getAlerts().catch(() => [] as AlertStudentDTO[]),
    ])
      .then(([cls, al]) => {
        setClassrooms(cls);
        setAlerts(al);
      })
      .finally(() => setIsLoading(false));
  }, []);

  const totalStudents = classrooms.reduce(
    (sum, c) => sum + (c.student_count || 0),
    0
  );
  const studentsInDifficulty = alerts.length;

  const handleCreate = async () => {
    if (!newClassName.trim()) {
      setCreateError('Le nom de la classe est requis.');
      return;
    }
    setCreating(true);
    setCreateError('');
    try {
      const created = await teacherService.createClassroom({
        name: newClassName.trim(),
      });
      setClassrooms((prev) => [...prev, created]);
      setShowCreateModal(false);
      setNewClassName('');
    } catch (err: any) {
      setCreateError(err?.message || 'Erreur lors de la création.');
    } finally {
      setCreating(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-8">
        <Skeleton variant="text" className="w-64 h-8" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} variant="rect" className="h-32" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-2xl font-extrabold text-gray-900">
          Bonjour, {user?.name || 'Enseignant'}
        </h1>
        <p className="text-gray-500">
          Bienvenue dans votre espace enseignant.
        </p>
      </header>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          title="Mes classes"
          value={classrooms.length}
          icon={<School size={20} />}
          color="bg-blue-600"
        />
        <StatCard
          title="Total élèves"
          value={totalStudents}
          icon={<Users size={20} />}
          color="bg-green-600"
        />
        <StatCard
          title="Élèves en difficulté"
          value={studentsInDifficulty}
          icon={<AlertTriangle size={20} />}
          color="bg-orange-500"
        />
      </div>

      {/* Classrooms */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-800">Mes classes</h2>
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center px-4 py-2 rounded-xl gradient-hero text-white font-bold text-sm shadow-clay-sm hover:shadow-clay-hover transition-shadow"
          >
            <Plus size={16} className="mr-2" />
            Créer une classe
          </button>
        </div>

        {classrooms.length === 0 ? (
          <Card className="text-center py-12">
            <School size={48} className="mx-auto text-gray-300 mb-4" />
            <p className="text-gray-500 font-medium">
              Aucune classe pour le moment.
            </p>
            <p className="text-sm text-gray-400 mt-1">
              Créez votre première classe pour commencer.
            </p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {classrooms.map((c) => (
              <Card
                key={c.id}
                interactive
                onClick={() => navigate(`/app/teacher/classrooms/${c.id}`)}
                className="flex flex-col justify-between"
              >
                <div>
                  <h3 className="font-bold text-gray-900 text-lg mb-1">
                    {c.name}
                  </h3>
                  <p className="text-sm text-gray-500 mb-3">
                    {c.student_count || 0} élève
                    {(c.student_count || 0) !== 1 ? 's' : ''}
                  </p>
                </div>
                <div className="flex items-center justify-between">
                  <ClassInviteShare className={c.name} inviteCode={c.invite_code} variant="sm" />
                  <ChevronRight size={18} className="text-gray-300" />
                </div>
              </Card>
            ))}
          </div>
        )}
      </section>

      {/* Alerts */}
      {alerts.length > 0 && (
        <section>
          <h2 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
            <AlertTriangle
              size={20}
              className="mr-2 text-orange-500"
            />
            Alertes — Élèves en difficulté
          </h2>
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm divide-y divide-gray-100">
            {alerts.map((a, i) => (
              <div
                key={`${a.profile_id}-${i}`}
                className="flex items-center justify-between px-6 py-4"
              >
                <div>
                  <p className="font-bold text-gray-800">
                    {a.display_name}
                  </p>
                  <p className="text-sm text-gray-500">
                    {a.classroom_name}
                    {a.skill_name ? ` — ${a.skill_name}` : ''}
                  </p>
                </div>
                <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-bold">
                  {a.avg_score}%
                </span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Create Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false);
          setCreateError('');
          setNewClassName('');
        }}
        title="Créer une classe"
      >
        <div className="space-y-4">
          <Input
            label="Nom de la classe"
            placeholder="Ex : CE2 - Groupe A"
            value={newClassName}
            onChange={(e) => setNewClassName(e.target.value)}
            error={createError}
          />
          <button
            onClick={handleCreate}
            disabled={creating}
            className="w-full py-3 rounded-xl gradient-hero text-white font-bold shadow-clay-sm hover:shadow-clay-hover transition-shadow disabled:opacity-50"
          >
            {creating ? 'Création...' : 'Créer'}
          </button>
        </div>
      </Modal>
    </div>
  );
};
