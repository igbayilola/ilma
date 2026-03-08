import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Cards';
import { ButtonVariant } from '../../types';
import { ArrowLeft, BookOpen, Lightbulb, CheckCircle2 } from 'lucide-react';
import { contentService, LessonDTO } from '../../services/contentService';

export const MicroLessonPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const location = useLocation();
    const [lesson, setLesson] = useState<LessonDTO | null>(null);
    const [understood, setUnderstood] = useState(false);

    const returnPath = (location.state as any)?.returnPath || '/app/student/dashboard';

    useEffect(() => {
        if (!id) return;
        contentService.getSkillWithLessons(id)
            .then(({ lessons }) => {
                if (lessons.length > 0) setLesson(lessons[0]);
            })
            .catch(() => setLesson(null));
    }, [id]);

    if (!lesson) return <div className="p-8 text-center">Chargement de la leçon...</div>;

    // Parse contentHtml or use as plain text
    const paragraphs = lesson.contentHtml
        ? lesson.contentHtml.split(/<\/p>|<br\s*\/?>|\n/).filter(Boolean).map(p => p.replace(/<[^>]+>/g, '').trim()).filter(Boolean)
        : ['Contenu de la leçon'];

    return (
        <div className="min-h-screen bg-ilma-surface md:bg-white flex flex-col max-w-3xl mx-auto md:shadow-xl md:min-h-0 md:h-screen">
            <header className="p-4 bg-white border-b border-gray-100 sticky top-0 z-20 flex items-center justify-between">
                <button onClick={() => navigate(returnPath)} className="flex items-center text-gray-500 font-bold text-sm hover:text-ilma-primary">
                    <ArrowLeft size={20} className="mr-1" /> Retour à l'exercice
                </button>
                <div className="flex items-center text-ilma-primary font-bold bg-amber-50 px-3 py-1 rounded-full text-xs">
                    <BookOpen size={14} className="mr-2" />
                    Micro-leçon • {lesson.durationMinutes} min
                </div>
            </header>

            <main className="flex-1 overflow-y-auto p-6 md:p-10">
                <h1 className="text-2xl md:text-3xl font-extrabold text-gray-900 mb-6">{lesson.title}</h1>

                <div className="prose prose-blue max-w-none mb-8 text-gray-700 leading-relaxed text-lg">
                    {paragraphs.map((paragraph, idx) => (
                        <p key={idx} className="mb-4">{paragraph}</p>
                    ))}
                </div>

                {lesson.summary && (
                    <Card className="bg-yellow-50 border-yellow-100 mb-8 overflow-hidden relative">
                        <div className="absolute top-0 right-0 p-4 opacity-10">
                            <Lightbulb size={100} className="text-yellow-500" />
                        </div>
                        <div className="relative z-10">
                            <h3 className="text-lg font-bold text-yellow-800 mb-2 flex items-center">
                                <Lightbulb size={20} className="mr-2 fill-yellow-500 text-yellow-600" />
                                Résumé
                            </h3>
                            <p className="text-gray-800 font-medium text-lg">{lesson.summary}</p>
                        </div>
                    </Card>
                )}

                <div
                    className={`border-2 rounded-2xl p-4 cursor-pointer transition-all ${understood ? 'border-green-200 bg-green-50' : 'border-gray-200 bg-white hover:border-amber-200'}`}
                    onClick={() => setUnderstood(!understood)}
                >
                    <div className="flex items-center">
                        <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center mr-3 transition-colors ${understood ? 'border-green-500 bg-green-500' : 'border-gray-300'}`}>
                            {understood && <CheckCircle2 size={16} className="text-white" />}
                        </div>
                        <span className={`font-bold ${understood ? 'text-green-800' : 'text-gray-600'}`}>
                            J'ai compris cette notion
                        </span>
                    </div>
                </div>
            </main>

            <footer className="p-4 md:p-6 border-t border-gray-100 bg-white sticky bottom-0 z-20">
                <Button
                    fullWidth
                    size="lg"
                    onClick={() => navigate(returnPath)}
                    variant={understood ? ButtonVariant.PRIMARY : ButtonVariant.SECONDARY}
                    className="h-14 text-lg shadow-lg"
                >
                    {understood ? "Reprendre l'exercice" : "Retour"}
                </Button>
            </footer>
        </div>
    );
};
