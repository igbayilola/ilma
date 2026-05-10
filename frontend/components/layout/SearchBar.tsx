import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, X, BookOpen, HelpCircle, FolderOpen, FileText } from 'lucide-react';
import { contentService, SearchResultDTO } from '../../services/contentService';

const TYPE_META: Record<string, { icon: React.ReactNode; label: string }> = {
  skill: { icon: <BookOpen size={14} />, label: 'Compétence' },
  question: { icon: <HelpCircle size={14} />, label: 'Question' },
  domain: { icon: <FolderOpen size={14} />, label: 'Domaine' },
  lesson: { icon: <FileText size={14} />, label: 'Leçon' },
};

export const SearchBar: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResultDTO[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(undefined);
  const navigate = useNavigate();

  const doSearch = useCallback(async (q: string) => {
    if (q.length < 2) {
      setResults([]);
      return;
    }
    setIsLoading(true);
    try {
      const data = await contentService.search(q, 10);
      setResults(data);
    } catch {
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setQuery(val);
    setIsOpen(true);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => doSearch(val), 300);
  };

  const handleClear = () => {
    setQuery('');
    setResults([]);
    setIsOpen(false);
    inputRef.current?.focus();
  };

  const navigateToResult = (r: SearchResultDTO) => {
    setIsOpen(false);
    setQuery('');
    setResults([]);

    switch (r.type) {
      case 'skill':
        navigate(`/app/student/exercise/${r.id}`);
        break;
      case 'question':
        if (r.skillId) navigate(`/app/student/exercise/${r.skillId}`);
        break;
      case 'domain':
        // Navigate to domain's skills — we need the subject id which we don't have,
        // so navigate to subjects and let the user drill down
        navigate('/app/student/subjects');
        break;
      case 'lesson':
        if (r.skillId) navigate(`/app/student/lesson/${r.skillId}`);
        break;
    }
  };

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  // Keyboard shortcut: Ctrl+K / Cmd+K to focus
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
        setIsOpen(true);
      }
      if (e.key === 'Escape') {
        setIsOpen(false);
        inputRef.current?.blur();
      }
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, []);

  return (
    <div ref={containerRef} className="relative flex-1 max-w-md hidden md:block">
      <div className="relative">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleChange}
          onFocus={() => { if (query.length >= 2) setIsOpen(true); }}
          placeholder="Rechercher une compétence, question..."
          className="w-full pl-9 pr-9 py-2 text-sm rounded-xl border border-gray-200 bg-gray-50 focus:bg-white focus:border-sitou-primary focus:ring-2 focus:ring-amber-200 outline-none transition-all"
          aria-label="Rechercher dans le contenu"
          role="combobox"
          aria-expanded={isOpen && results.length > 0}
          aria-autocomplete="list"
        />
        {query && (
          <button onClick={handleClear} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600" aria-label="Effacer la recherche">
            <X size={14} />
          </button>
        )}
        {!query && (
          <kbd className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-gray-400 border border-gray-200 rounded px-1.5 py-0.5 font-mono">
            Ctrl+K
          </kbd>
        )}
      </div>

      {isOpen && (query.length >= 2) && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden z-50 max-h-80 overflow-y-auto" role="listbox">
          {isLoading && (
            <div className="p-4 text-center text-sm text-gray-400">Recherche...</div>
          )}
          {!isLoading && results.length === 0 && (
            <div className="p-4 text-center text-sm text-gray-400">Aucun résultat pour « {query} »</div>
          )}
          {!isLoading && results.map((r) => {
            const meta = TYPE_META[r.type] || TYPE_META.skill;
            return (
              <button
                key={`${r.type}-${r.id}`}
                onClick={() => navigateToResult(r)}
                className="w-full text-left px-4 py-3 hover:bg-amber-50 transition-colors flex items-start gap-3 border-b border-gray-50 last:border-0"
                role="option"
              >
                <span className="mt-0.5 p-1 rounded-lg bg-gray-100 text-gray-500 flex-shrink-0">
                  {meta.icon}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="text-sm font-medium text-gray-800 truncate">{r.title}</div>
                  {r.subtitle && <div className="text-xs text-gray-400 truncate mt-0.5">{r.subtitle}</div>}
                </div>
                <span className="text-[10px] text-gray-400 bg-gray-50 rounded px-1.5 py-0.5 flex-shrink-0 mt-0.5">
                  {meta.label}
                </span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};
