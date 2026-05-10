import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, FileText } from 'lucide-react';

export const TermsPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 px-4 py-8 max-w-3xl mx-auto">
      <Link to="/" className="inline-flex items-center gap-2 text-sitou-primary mb-6 text-sm font-medium">
        <ArrowLeft size={16} /> Retour
      </Link>

      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-sitou-primary/10 rounded-xl text-sitou-primary">
          <FileText size={28} />
        </div>
        <h1 className="text-2xl font-extrabold text-gray-900">Conditions Générales d'Utilisation</h1>
      </div>

      <div className="bg-white rounded-2xl shadow-sm p-6 space-y-6 text-sm text-gray-700 leading-relaxed">

        <section>
          <h2 className="text-lg font-bold text-gray-900 mb-2">1. Objet</h2>
          <p>
            Les présentes CGU régissent l'utilisation de SITOU, service d'apprentissage en ligne
            destiné aux élèves du cycle primaire en République du Bénin.
          </p>
        </section>

        <section>
          <h2 className="text-lg font-bold text-gray-900 mb-2">2. Acceptation</h2>
          <p>
            L'utilisation de SITOU implique l'acceptation pleine et entière des présentes CGU et
            de la <Link to="/legal/privacy" className="text-sitou-primary underline">Politique de Confidentialité</Link>.
          </p>
        </section>

        <section>
          <h2 className="text-lg font-bold text-gray-900 mb-2">3. Inscription et compte</h2>
          <ul className="list-disc pl-5 space-y-1">
            <li>L'inscription est ouverte aux parents, tuteurs, enseignants et administrateurs scolaires.</li>
            <li>Un enfant mineur n'accède au service qu'après recueil du consentement parental vérifié (OTP SMS).</li>
            <li>Chaque utilisateur est responsable de la confidentialité de ses identifiants.</li>
            <li>Un compte est strictement personnel et incessible.</li>
          </ul>
        </section>

        <section>
          <h2 className="text-lg font-bold text-gray-900 mb-2">4. Services proposés</h2>
          <ul className="list-disc pl-5 space-y-1">
            <li>Catalogue d'exercices et de micro-leçons alignés sur le programme MEMP.</li>
            <li>Suivi de la progression de l'élève (SmartScore 0-100).</li>
            <li>Examens blancs CEP et score prédictif (Premium).</li>
            <li>Tableau de bord parent et enseignant.</li>
            <li>Notifications par SMS et push.</li>
          </ul>
        </section>

        <section>
          <h2 className="text-lg font-bold text-gray-900 mb-2">5. Offre gratuite et Premium</h2>
          <p>
            L'offre gratuite donne accès à un sous-ensemble du catalogue (1 examen blanc par matière,
            exercices limités). L'offre Premium déverrouille l'intégralité. Paiement par Mobile Money
            (MTN, Moov), KKiaPay ou FedaPay. Sans engagement, résiliable à tout moment, non
            remboursable au prorata.
          </p>
        </section>

        <section>
          <h2 className="text-lg font-bold text-gray-900 mb-2">6. Engagements de l'utilisateur</h2>
          <ul className="list-disc pl-5 space-y-1">
            <li>Fournir des informations exactes lors de l'inscription.</li>
            <li>Ne pas tenter de contourner les mesures de sécurité.</li>
            <li>Ne pas utiliser le service à des fins illicites.</li>
            <li>Respecter les autres utilisateurs (pas de pseudonyme injurieux, pas de tricherie organisée).</li>
            <li>Signaler tout contenu inapproprié via les outils intégrés.</li>
          </ul>
        </section>

        <section>
          <h2 className="text-lg font-bold text-gray-900 mb-2">7. Propriété intellectuelle</h2>
          <p>
            Le contenu pédagogique est la propriété de SITOU ou de ses partenaires éducatifs (MEMP).
            L'utilisateur conserve la propriété de ses propres données. Toute reproduction ou
            diffusion non autorisée est interdite.
          </p>
        </section>

        <section>
          <h2 className="text-lg font-bold text-gray-900 mb-2">8. Disponibilité et responsabilité</h2>
          <p>
            SITOU s'efforce d'assurer une disponibilité maximale, sans garantir 100%. SITOU est un
            outil d'accompagnement scolaire, non un substitut à l'enseignement officiel. La
            responsabilité de SITOU est limitée aux dommages directs et prouvés.
          </p>
        </section>

        <section>
          <h2 className="text-lg font-bold text-gray-900 mb-2">9. Suppression et résiliation</h2>
          <p>
            L'utilisateur peut résilier à tout moment via les paramètres. Une période de grâce de
            30 jours permet la récupération du compte. SITOU peut suspendre un compte en cas de
            violation grave des CGU, après notification.
          </p>
        </section>

        <section>
          <h2 className="text-lg font-bold text-gray-900 mb-2">10. Données personnelles</h2>
          <p>
            Le traitement des données personnelles est régi par la <Link to="/legal/privacy" className="text-sitou-primary underline">Politique de Confidentialité</Link>.
            Contact DPO : <strong>dpo@sitou.bj</strong>.
          </p>
        </section>

        <section>
          <h2 className="text-lg font-bold text-gray-900 mb-2">11. Loi applicable</h2>
          <p>
            Les présentes CGU sont régies par le droit béninois. Tout litige sera soumis aux
            tribunaux compétents de Cotonou, après tentative de résolution amiable via le DPO.
          </p>
        </section>

        <p className="text-xs text-gray-400 pt-4 border-t">
          Dernière mise à jour : mai 2026
        </p>
      </div>
    </div>
  );
};
