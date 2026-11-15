/**
 * i18n/index.js - translation setup (react-i18next).
 *
 * All texts of the interface live in src/i18n/locales/en.json and fr.json.
 * To change a sentence, edit it there. To add a language, create a new JSON
 * file and register it in `resources` below.
 */
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './locales/en.json';
import fr from './locales/fr.json';

// The chosen language is remembered between visits.
let savedLanguage = 'en';
try {
  savedLanguage = localStorage.getItem('language') || 'en';
} catch (e) {
  // localStorage unavailable: keep the default
}

i18n.use(initReactI18next).init({
  resources: { en: { translation: en }, fr: { translation: fr } },
  lng: savedLanguage,
  fallbackLng: 'en',
  interpolation: { escapeValue: false }, // React already escapes
});

export default i18n;