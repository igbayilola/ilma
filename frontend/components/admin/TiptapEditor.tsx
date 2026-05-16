import React, { useCallback } from 'react';
import { useEditor, EditorContent, Editor } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Link from '@tiptap/extension-link';
import { Bold, Italic, List, ListOrdered, Heading3, Link as LinkIcon, Unlink, Undo, Redo, Eraser } from 'lucide-react';

export interface TiptapEditorProps {
  value: string;
  onChange: (html: string) => void;
  placeholder?: string;
  minHeightClass?: string;
  ariaLabel?: string;
}

function ToolbarButton({
  active = false,
  onClick,
  disabled = false,
  title,
  children,
}: {
  active?: boolean;
  onClick: () => void;
  disabled?: boolean;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onMouseDown={e => e.preventDefault() /* keep editor focus */}
      onClick={onClick}
      disabled={disabled}
      aria-pressed={active}
      title={title}
      className={
        'p-1.5 rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed ' +
        (active
          ? 'bg-sitou-primary text-white'
          : 'text-gray-600 hover:text-sitou-primary hover:bg-blue-50')
      }
    >
      {children}
    </button>
  );
}

function Toolbar({ editor }: { editor: Editor }) {
  const promptLink = useCallback(() => {
    const previous = editor.getAttributes('link').href || '';
    const url = window.prompt('URL du lien (laisse vide pour retirer) :', previous);
    if (url === null) return; // cancel
    if (url === '') {
      editor.chain().focus().extendMarkRange('link').unsetLink().run();
      return;
    }
    editor.chain().focus().extendMarkRange('link').setLink({ href: url }).run();
  }, [editor]);

  return (
    <div className="flex items-center gap-0.5 px-2 py-1.5 border-b border-gray-200 bg-gray-50 rounded-t-xl flex-wrap">
      <ToolbarButton
        active={editor.isActive('bold')}
        onClick={() => editor.chain().focus().toggleBold().run()}
        title="Gras"
      >
        <Bold size={15} />
      </ToolbarButton>
      <ToolbarButton
        active={editor.isActive('italic')}
        onClick={() => editor.chain().focus().toggleItalic().run()}
        title="Italique"
      >
        <Italic size={15} />
      </ToolbarButton>
      <ToolbarButton
        active={editor.isActive('heading', { level: 3 })}
        onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
        title="Sous-titre"
      >
        <Heading3 size={15} />
      </ToolbarButton>
      <span className="w-px h-5 bg-gray-300 mx-1" aria-hidden />
      <ToolbarButton
        active={editor.isActive('bulletList')}
        onClick={() => editor.chain().focus().toggleBulletList().run()}
        title="Liste à puces"
      >
        <List size={15} />
      </ToolbarButton>
      <ToolbarButton
        active={editor.isActive('orderedList')}
        onClick={() => editor.chain().focus().toggleOrderedList().run()}
        title="Liste numérotée"
      >
        <ListOrdered size={15} />
      </ToolbarButton>
      <span className="w-px h-5 bg-gray-300 mx-1" aria-hidden />
      <ToolbarButton
        active={editor.isActive('link')}
        onClick={promptLink}
        title="Lien"
      >
        <LinkIcon size={15} />
      </ToolbarButton>
      {editor.isActive('link') && (
        <ToolbarButton
          onClick={() => editor.chain().focus().unsetLink().run()}
          title="Retirer le lien"
        >
          <Unlink size={15} />
        </ToolbarButton>
      )}
      <span className="w-px h-5 bg-gray-300 mx-1" aria-hidden />
      <ToolbarButton
        onClick={() => editor.chain().focus().unsetAllMarks().clearNodes().run()}
        title="Effacer la mise en forme"
      >
        <Eraser size={15} />
      </ToolbarButton>
      <span className="ml-auto flex items-center gap-0.5">
        <ToolbarButton
          onClick={() => editor.chain().focus().undo().run()}
          disabled={!editor.can().undo()}
          title="Annuler"
        >
          <Undo size={15} />
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().redo().run()}
          disabled={!editor.can().redo()}
          title="Rétablir"
        >
          <Redo size={15} />
        </ToolbarButton>
      </span>
    </div>
  );
}

/**
 * Rich-text editor for admin authoring (explanations, lesson sections, etc.).
 * Emits HTML strings via `onChange`. Backwards-compatible with plain-text
 * values already stored in the database — Tiptap parses them as paragraphs.
 */
export const TiptapEditor: React.FC<TiptapEditorProps> = ({
  value,
  onChange,
  placeholder,
  minHeightClass = 'min-h-[120px]',
  ariaLabel = 'Éditeur de texte enrichi',
}) => {
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: { levels: [3] },
      }),
      Link.configure({
        openOnClick: false,
        HTMLAttributes: { class: 'text-sitou-primary underline' },
      }),
    ],
    content: value || '',
    onUpdate({ editor }) {
      const html = editor.getHTML();
      // Tiptap returns "<p></p>" for empty content. Normalise to '' so empty
      // explanations don't accidentally become a non-null saved field.
      onChange(html === '<p></p>' ? '' : html);
    },
    editorProps: {
      attributes: {
        class:
          'prose prose-sm max-w-none px-4 py-3 focus:outline-none ' + minHeightClass,
        'aria-label': ariaLabel,
      },
    },
  });

  // Sync external value changes (e.g. when loading a different question)
  React.useEffect(() => {
    if (!editor) return;
    const current = editor.getHTML();
    const incoming = value || '';
    if (current !== incoming && current !== '<p></p>') return; // user is editing
    if (current === incoming) return;
    editor.commands.setContent(incoming, { emitUpdate: false });
  }, [value, editor]);

  if (!editor) {
    return (
      <div className="w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-400">
        Chargement de l'éditeur…
      </div>
    );
  }

  return (
    <div className="w-full rounded-xl border border-gray-200 bg-white focus-within:ring-2 focus-within:ring-sitou-primary/20 focus-within:border-sitou-primary transition-colors">
      <Toolbar editor={editor} />
      <EditorContent editor={editor} placeholder={placeholder} />
    </div>
  );
};
