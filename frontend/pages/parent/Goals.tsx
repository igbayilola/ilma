import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card } from '../../components/ui/Cards';
import { Button } from '../../components/ui/Button';
import { Target, Clock, BookOpen, Save } from 'lucide-react';
import { ButtonVariant } from '../../types';
import { parentService } from '../../services/parentService';

export const ParentGoalsPage: React.FC = () => {
    const { childId } = useParams<{ childId: string }>();
    const navigate = useNavigate();
    const [saving, setSaving] = useState(false);

    const [goals, setGoals] = useState({
        weeklyTime: 180,
        weeklyExercises: 15,
    });

    const handleSave = async () => {
        if (!childId) return;
        setSaving(true);
        try {
            await parentService.setWeeklyGoal(childId, goals.weeklyTime);
            navigate(-1);
        } catch (err) {
            console.error('Failed to save goals', err);
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="space-y-6 max-w-2xl mx-auto">
             <header>
                <h1 className="text-2xl md:text-3xl font-extrabold text-gray-900 mb-2">Objectifs</h1>
                <p className="text-gray-500">Définissez des cibles pour motiver votre enfant.</p>
            </header>

            <Card>
                <div className="flex items-center mb-6">
                    <div className="p-2 bg-red-100 rounded-lg mr-3 text-red-600">
                        <Target size={24} />
                    </div>
                    <h2 className="text-lg font-bold text-gray-900">Objectifs Hebdomadaires</h2>
                </div>

                <div className="space-y-6">
                    <div>
                        <label className="block text-sm font-bold text-gray-700 mb-2">Temps d'écran éducatif (minutes/semaine)</label>
                        <div className="flex items-center space-x-4">
                            <Clock className="text-gray-400" />
                            <input
                                type="range"
                                min="60"
                                max="600"
                                step="30"
                                value={goals.weeklyTime}
                                onChange={(e) => setGoals({...goals, weeklyTime: parseInt(e.target.value)})}
                                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                            />
                            <span className="font-bold text-ilma-primary w-16 text-right">{goals.weeklyTime}m</span>
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-bold text-gray-700 mb-2">Exercices complétés (par semaine)</label>
                        <div className="flex items-center space-x-4">
                            <BookOpen className="text-gray-400" />
                            <input
                                type="range"
                                min="5"
                                max="50"
                                step="1"
                                value={goals.weeklyExercises}
                                onChange={(e) => setGoals({...goals, weeklyExercises: parseInt(e.target.value)})}
                                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                            />
                            <span className="font-bold text-ilma-primary w-16 text-right">{goals.weeklyExercises}</span>
                        </div>
                    </div>
                </div>
            </Card>

            <div className="flex justify-end space-x-4">
                <Button variant={ButtonVariant.GHOST} onClick={() => navigate(-1)}>Annuler</Button>
                <Button leftIcon={<Save size={18} />} onClick={handleSave} disabled={saving}>
                    {saving ? 'Enregistrement...' : 'Enregistrer'}
                </Button>
            </div>
        </div>
    );
};
