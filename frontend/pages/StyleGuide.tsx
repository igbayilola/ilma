import React from 'react';
import { Button } from '../components/ui/Button';
import { Card, Badge } from '../components/ui/Cards';
import { SmartScoreMeter, XPBar, StreakWidget } from '../components/ilma/Gamification';
import { ButtonVariant } from '../types';
import { AlertCircle, Check, Play } from 'lucide-react';

export const StyleGuide: React.FC = () => {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-gray-900 mb-2">Design System Sitou</h1>
        <p className="text-gray-500">Tokens, Composants et Widgets pour le frontend.</p>
      </div>

      <section>
        <h2 className="text-xl font-bold mb-4 border-b pb-2">Couleurs</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="h-20 rounded-xl bg-sitou-primary flex items-end p-2 text-white font-mono text-xs shadow-lg">primary #D97706</div>
          <div className="h-20 rounded-xl bg-sitou-primary-light flex items-end p-2 text-sitou-primary font-mono text-xs border border-amber-200">light #FEF3C7</div>
          <div className="h-20 rounded-xl bg-sitou-green flex items-end p-2 text-white font-mono text-xs shadow-lg">green #22C55E</div>
          <div className="h-20 rounded-xl bg-sitou-orange flex items-end p-2 text-white font-mono text-xs shadow-lg">orange #F97316</div>
        </div>
      </section>

      <section>
        <h2 className="text-xl font-bold mb-4 border-b pb-2">Boutons</h2>
        <div className="flex flex-wrap gap-4 items-center">
            <Button variant={ButtonVariant.PRIMARY}>Commencer</Button>
            <Button variant={ButtonVariant.SECONDARY}>Retour</Button>
            <Button variant={ButtonVariant.GHOST}>Ignorer</Button>
            <Button variant={ButtonVariant.DANGER}>Supprimer</Button>
            <Button variant={ButtonVariant.PRIMARY} leftIcon={<Play size={18} />}>Continuer</Button>
            <Button isLoading>Chargement</Button>
            <Button disabled>Désactivé</Button>
        </div>
      </section>

      <section>
        <h2 className="text-xl font-bold mb-4 border-b pb-2">Widgets Sitou</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="flex flex-col items-center justify-center space-y-4">
                <span className="text-sm text-gray-400 font-bold uppercase">Smart Score</span>
                <div className="flex space-x-4">
                    <SmartScoreMeter score={92} />
                    <SmartScoreMeter score={65} />
                    <SmartScoreMeter score={30} />
                </div>
            </Card>
            <Card className="flex flex-col justify-center space-y-4">
                <span className="text-sm text-gray-400 font-bold uppercase">XP & Level</span>
                <XPBar current={450} max={1000} level={5} />
                <XPBar current={950} max={1000} level={12} />
            </Card>
            <Card className="flex flex-col items-center justify-center space-y-4">
                 <span className="text-sm text-gray-400 font-bold uppercase">Badges & Streak</span>
                 <div className="flex space-x-2">
                     <Badge label="Maths" color="blue" />
                     <Badge label="Terminé" color="green" />
                     <Badge label="Difficile" color="red" />
                 </div>
                 <StreakWidget days={14} active={true} />
            </Card>
        </div>
      </section>
      
       <section>
        <h2 className="text-xl font-bold mb-4 border-b pb-2">Alertes & Cartes</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-red-50 border border-red-100 rounded-2xl flex items-start">
                <AlertCircle className="text-sitou-red mt-0.5 mr-3 flex-shrink-0" />
                <div>
                    <h4 className="font-bold text-sitou-red">Erreur de connexion</h4>
                    <p className="text-sm text-red-700 mt-1">Impossible de charger le contenu. Vérifiez votre réseau.</p>
                </div>
            </div>
            <div className="p-4 bg-green-50 border border-green-100 rounded-2xl flex items-start">
                <Check className="text-sitou-green mt-0.5 mr-3 flex-shrink-0" />
                <div>
                    <h4 className="font-bold text-sitou-green">Exercice terminé !</h4>
                    <p className="text-sm text-green-700 mt-1">Tu as gagné +20 XP.</p>
                </div>
            </div>
        </div>
      </section>
    </div>
  );
};