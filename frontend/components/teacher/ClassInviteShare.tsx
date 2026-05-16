import React, { useState } from 'react';
import { Copy, Check, MessageCircle, Share2 } from 'lucide-react';

/**
 * Pre-formatted invitation text. Exported so we can unit-test the message
 * shape (the whole user journey of A6.6 hangs on this string being clear
 * enough that a parent knows what to do after they read it in WhatsApp).
 */
export function buildInviteShareText(className: string, inviteCode: string): string {
  return (
    `Bonjour, je vous invite à rejoindre la classe « ${className} » sur Sitou.\n\n` +
    `1. Téléchargez l'app Sitou (ou ouvrez sitou.bj)\n` +
    `2. Dans le dashboard parent, choisissez « Rejoindre une classe »\n` +
    `3. Entrez le code : ${inviteCode.toUpperCase()}`
  );
}

interface ClassInviteShareProps {
  className: string;
  inviteCode: string;
  /** Size variant: 'sm' for inline (teacher dashboard cards), 'md' for the
   * detail page header. */
  variant?: 'sm' | 'md';
}

export const ClassInviteShare: React.FC<ClassInviteShareProps> = ({
  className: classroomName,
  inviteCode,
  variant = 'md',
}) => {
  const [copied, setCopied] = useState(false);
  const text = buildInviteShareText(classroomName, inviteCode);

  const handleCopy = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(inviteCode).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const handleWhatsApp = (e: React.MouseEvent) => {
    e.stopPropagation();
    // wa.me opens WhatsApp's contact picker on mobile, or web.whatsapp.com on desktop
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank', 'noopener,noreferrer');
  };

  const handleSms = (e: React.MouseEvent) => {
    e.stopPropagation();
    // sms: URI scheme works on iOS + Android. Question mark separator for body
    // works on iOS too. On desktop browsers this opens the default mail/SMS app
    // or fails silently — acceptable.
    window.location.href = `sms:?body=${encodeURIComponent(text)}`;
  };

  const buttonClass = variant === 'sm'
    ? 'p-1.5 rounded-lg'
    : 'p-2 rounded-xl';
  const iconSize = variant === 'sm' ? 14 : 16;

  return (
    <div className="inline-flex items-center gap-1.5" onClick={e => e.stopPropagation()}>
      <button
        type="button"
        onClick={handleCopy}
        title="Copier le code"
        aria-label="Copier le code d'invitation"
        className={`${buttonClass} bg-gray-100 hover:bg-gray-200 text-gray-700 transition-colors inline-flex items-center gap-1.5`}
      >
        <span className="font-mono font-bold text-sm">{inviteCode}</span>
        {copied ? <Check size={iconSize} className="text-green-600" /> : <Copy size={iconSize} className="text-gray-500" />}
      </button>
      <button
        type="button"
        onClick={handleWhatsApp}
        title="Partager par WhatsApp"
        aria-label="Partager le code d'invitation par WhatsApp"
        className={`${buttonClass} bg-green-50 hover:bg-green-100 text-green-700 transition-colors`}
      >
        <MessageCircle size={iconSize} />
      </button>
      <button
        type="button"
        onClick={handleSms}
        title="Partager par SMS"
        aria-label="Partager le code d'invitation par SMS"
        className={`${buttonClass} bg-blue-50 hover:bg-blue-100 text-blue-700 transition-colors`}
      >
        <Share2 size={iconSize} />
      </button>
    </div>
  );
};
