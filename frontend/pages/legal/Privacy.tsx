
import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Shield } from 'lucide-react';

export const PrivacyPolicyPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 px-4 py-8 max-w-3xl mx-auto">
      <Link to="/" className="inline-flex items-center gap-2 text-sitou-primary mb-6 text-sm font-medium">
        <ArrowLeft size={16} /> Retour
      </Link>

      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-sitou-primary/10 rounded-xl text-sitou-primary">
          <Shield size={28} />
        </div>
        <h1 className="text-2xl font-extrabold text-gray-900">Politique de Confidentialité</h1>
      </div>

      <div className="bg-white rounded-2xl shadow-sm p-6 space-y-6 text-sm text-gray-700 leading-relaxed">

        <section>
          <h2 className="text-lg font-bold text-gray-900 mb-2">Responsable du traitement</h2>
          <p>
            SITOU — Application éducative pour le cycle primaire au Bénin.<br />
            Contact : <strong>dpo@sitou.bj</strong>
          </p>
        </section>

        <section>
          <h2 className="text-lg font-bold text-gray-900 mb-2">Données collectées</h2>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>Authentification :</strong> email ou numéro de téléphone, mot de passe (stocké sous forme hashée).</li>
            <li><strong>Profil :</strong> nom complet, prénom de l'enfant, avatar, niveau scolaire.</li>
            <li><strong>Données pédagogiques :</strong> scores, progression, exercices complétés, badges obtenus.</li>
            <li><strong>Données techniques :</strong> adresse IP et type de navigateur (journaux de sécurité uniquement).</li>
          </ul>
        </section>

        <section>
          <h2 className="text-lg font-bold text-gray-900 mb-2">Finalités du traitement</h2>
          <ul className="list-disc pl-5 space-y-1">
            <li>Fournir un service d'apprentissage personnalisé aux élèves.</li>
            <li>Permettre aux parents de suivre la progression de leurs enfants.</li>
            <li>Permettre aux enseignants de suivre leur classe.</li>
            <li>Améliorer la qualité du contenu pédagogique.</li>
          </ul>
        </section>

        <section>
          <h2 className="text-lg font-bold text-gray-900 mb-2">Protection des données des mineurs</h2>
          <p>
            Sitou traite des données d'enfants dans un cadre éducatif. Conformément à la
            Directive APDP n°2020-001, le consentement du représentant légal (parent ou tuteur)
            est recueilli lors de l'inscription. Seules les données strictement nécessaires à
            l'apprentissage sont collectées.
          </p>
        </section>

        <section>
          <h2 className="text-lg font-bold text-gray-900 mb-2">Durées de conservation</h2>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>Compte actif :</strong> durée de vie du compte.</li>
            <li><strong>Compte supprimé :</strong> 30 jours puis suppression définitive.</li>
            <li><strong>Journaux de sécurité :</strong> 90 jours.</li>
            <li><strong>Données analytiques :</strong> 18 mois, anonymisées après 6 mois.</li>
          </ul>
        </section>

        <section>
          <h2 className="text-lg font-bold text-gray-900 mb-2">Vos droits</h2>
          <p>Conformément aux articles 355 à 360 du Code du numérique (Loi n°2017-20), vous disposez des droits suivants :</p>
          <ul className="list-disc pl-5 space-y-1 mt-2">
            <li><strong>Accès :</strong> obtenir une copie de vos données.</li>
            <li><strong>Rectification :</strong> corriger des informations inexactes.</li>
            <li><strong>Suppression :</strong> demander l'effacement de vos données.</li>
            <li><strong>Opposition :</strong> vous opposer au traitement de vos données.</li>
          </ul>
          <p className="mt-2">
            Pour exercer ces droits, contactez : <strong>dpo@sitou.bj</strong>
          </p>
        </section>

        <section>
          <h2 className="text-lg font-bold text-gray-900 mb-2">Réclamation</h2>
          <p>
            Si vous estimez que vos droits ne sont pas respectés, vous pouvez introduire
            une réclamation auprès de l'Autorité de Protection des Données à caractère
            Personnel (APDP) du Bénin.
          </p>
        </section>

        <p className="text-xs text-gray-400 pt-4 border-t">
          Dernière mise à jour : avril 2026
        </p>
      </div>
    </div>
  );
};
