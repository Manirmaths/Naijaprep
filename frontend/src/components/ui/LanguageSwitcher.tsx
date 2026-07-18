import { useLanguage } from '../../context/LanguageContext';
import { LANGUAGES } from '../../i18n/translations';

// Compact EN/HA toggle -- deliberately just two buttons, not a full <select>,
// since there are only two languages and this needs to fit in a sidebar
// footer / header without much room.
export default function LanguageSwitcher() {
  const { language, setLanguage } = useLanguage();

  return (
    <div className="inline-flex rounded-lg border border-ink-200 p-0.5 text-xs font-semibold" role="group" aria-label="Language">
      {LANGUAGES.map((l) => (
        <button
          key={l.value}
          type="button"
          onClick={() => setLanguage(l.value)}
          aria-pressed={language === l.value}
          className={`px-2.5 py-1 rounded-md transition-colors ${
            language === l.value ? 'bg-brand-500 text-white' : 'text-ink-500 hover:text-ink-900'
          }`}
        >
          {l.value.toUpperCase()}
        </button>
      ))}
    </div>
  );
}
