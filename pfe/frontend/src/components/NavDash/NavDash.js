import { useContext, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { NavLink, Link, useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { FaMoon, FaSun, FaBars, FaTimes } from 'react-icons/fa';
import { ThemeContext } from '../../contexts/theme';
import { LanguageContext } from '../../contexts/language';
import { logout, reset } from '../../features/authSlice';
import './NavDash.css';

/** Navigation bar of the logged-in area. */
const NavDash = () => {
  const { t } = useTranslation();
  const [{ themeName, toggleTheme }] = useContext(ThemeContext);
  const { currentLanguage, switchLanguage } = useContext(LanguageContext);
  const [showNavList, setShowNavList] = useState(false);
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const handleLogout = () => {
    dispatch(logout());
    dispatch(reset());
    navigate('/');
  };

  return (
    <header id='top' className='header center'>
      <h3>
        <NavLink to='/dashboard' className='link'>{t('nav.dashboard')}</NavLink>
      </h3>
      <nav className='center nav'>
        <ul style={{ display: showNavList ? 'flex' : null }} className='nav__list'>
          <li className='nav__list-item'>
            <a href='#my-projects' onClick={() => setShowNavList(false)} className='link link--nav'>
              {t('nav.projects')}
            </a>
          </li>
          <li className='nav__list-item'>
            <a href='#create-project' onClick={() => setShowNavList(false)} className='link link--nav'>
              {t('nav.newProject')}
            </a>
          </li>
          <li className='nav__list-item'>
            <Link to='/' onClick={handleLogout} className='link link--nav'>
              {t('nav.logout')}
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
    </header>
  );
};

export default NavDash;