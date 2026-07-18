import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import { translations, type Language } from '../i18n/translations';

const STORAGE_KEY = 'naijaprep_lang';

interface LanguageContextValue {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextValue | null>(null);

function readInitialLanguage(): Language {
  if (typeof window === 'undefined') return 'en';
  const stored = window.localStorage.getItem(STORAGE_KEY);
  return stored === 'ha' ? 'ha' : 'en';
}

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<Language>(readInitialLanguage);

  const setLanguage = useCallback((lang: Language) => {
    setLanguageState(lang);
    try {
      window.localStorage.setItem(STORAGE_KEY, lang);
    } catch {
      // Private browsing / storage disabled -- language choice just won't
      // persist across reloads, not worth failing over.
    }
  }, []);

  // Falls back to English for any key not yet translated -- this is
  // intentional given the current first-pass, partial Hausa coverage (see
  // i18n/translations.ts), not a bug to "fix" by adding more fallback logic.
  const t = useCallback(
    (key: string) => translations[language][key] ?? translations.en[key] ?? key,
    [language]
  );

  return <LanguageContext.Provider value={{ language, setLanguage, t }}>{children}</LanguageContext.Provider>;
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error('useLanguage must be used within a LanguageProvider');
  return ctx;
}
