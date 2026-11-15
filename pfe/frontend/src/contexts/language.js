// contexts/language.js
// Thin wrapper around i18next so that existing components keep working.
import { createContext } from 'react';
import { useTranslation } from 'react-i18next';

const LanguageContext = createContext();

const LanguageProvider = ({ children }) => {
  const { i18n } = useTranslation();
  const currentLanguage = i18n.resolvedLanguage === 'fr' ? 'fr' : 'en';

  const switchLanguage = () => {
    const next = currentLanguage === 'en' ? 'fr' : 'en';
    i18n.changeLanguage(next);
    try {
      localStorage.setItem('language', next);
    } catch (e) {
      // ignore
    }
  };

  return (
    <LanguageContext.Provider value={{ currentLanguage, switchLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
};

export { LanguageProvider, LanguageContext };