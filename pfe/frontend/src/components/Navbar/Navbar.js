import { useContext, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation } from 'react-router-dom';
import { FaMoon, FaSun, FaBars, FaTimes } from 'react-icons/fa';
import { ThemeContext } from '../../contexts/theme';
import { LanguageContext } from '../../contexts/language';
import './Navbar.css';

/** Navigation bar of the public pages (home, login). */
const Navbar = () => {
  const { t } = useTranslation();
  const [{ themeName, toggleTheme }] = useContext(ThemeContext);
  const { currentLanguage, switchLanguage } = useContext(LanguageContext);
  const { pathname } = useLocation();
  const [showNavList, setShowNavList] = useState(false);

  // On the home page, scroll to the section; from another page, go home first.
  const goToSection = (hash) => {
    if (pathname === '/') {
      document.querySelector(hash)?.scrollIntoView({ behavior: 'smooth' });
    } else {
      window.location.href = '/';
    }
    setShowNavList(false);
  };

  return (
    <nav className='center nav'>
      <ul style={{ display: showNavList ? 'flex' : null }} className='nav__list'>
        <li className='nav__list-item'>
          <Link to='/' onClick={() => goToSection('#projects')} className='link link--nav'>
            {t('nav.samples')}
          </Link>
        </li>
        <li className='nav__list-item'>
          <Link to='/login' onClick={() => setShowNavList(false)} className='link link--nav'>
            {t('nav.login')}
          </Link>
        </li>
        <li className='nav__list-item'>
          <Link to='/' onClick={() => goToSection('#contact')} className='link link--nav'>
            {t('nav.contact')}
          </Link>
        </li>
      </ul>

      <button type='button' onClick={() => setShowNavList(!showNavList)}
        className='btn btn--icon nav__hamburger' aria-label={t('nav.toggleNav')}>
        {showNavList ? <FaTimes /> : <FaBars />}
      </button>

      <div className='language-switcher' onClick={switchLanguage}>
        {currentLanguage === 'en' ? 'EN' : 'FR'}
      </div>

      <button type='button' onClick={toggleTheme}
        className='btn btn--icon nav__theme' aria-label={t('nav.toggleTheme')}>
        {themeName === 'dark' ? <FaSun /> : <FaMoon />}
      </button>
    </nav>
  );
};

export default Navbar;