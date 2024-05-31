import { useContext, useState } from 'react'
import Brightness2Icon from '@material-ui/icons/Brightness2'
import WbSunnyRoundedIcon from '@material-ui/icons/WbSunnyRounded'
import MenuIcon from '@material-ui/icons/Menu'
import CloseIcon from '@material-ui/icons/Close'
import { ThemeContext } from '../../contexts/theme'
import { LanguageContext } from '../../contexts/language';
import * as EnglishContent from '../../English';
import * as FrenchContent from '../../Frensh';

import './Navbar.css'
import { Link } from 'react-router-dom';



const Navbar = () => {
  const [{ themeName, toggleTheme }] = useContext(ThemeContext)
  const [showNavList, setShowNavList] = useState(false)
  const { currentLanguage, switchLanguage } = useContext(LanguageContext);

  const { navbar, projects, skills, contact } = currentLanguage === 'en' ? EnglishContent : FrenchContent;



  const toggleNavList = () => setShowNavList(!showNavList)

  return (
    <nav className='center nav'>
      <ul
        style={{ display: showNavList ? 'flex' : null }}
        className='nav__list'
      >
        {projects.length ? (
          <li className='nav__list-item'>
            <a
              href='#samples'
              onClick={toggleNavList}
              className='link link--nav'
            >
              {navbar.one}
            </a>
          </li>
        ) : null}

        {skills.length ? (
          <li className='nav__list-item'>
          <Link
            to="/login" // Link to the login page
            onClick={toggleNavList}
            className='link link--nav'
          >
            {navbar.two}
          </Link>
        </li>
        ) : null}

        {contact.email ? (
          <li className='nav__list-item'>
            <a
              href='#contact'
              onClick={toggleNavList}
              className='link link--nav'
            >
              {navbar.three}
            </a>
          </li>
        ) : null}
      </ul>

      <button
        type='button'
        onClick={toggleNavList}
        className='btn btn--icon nav__hamburger'
        aria-label='toggle navigation'
      >
        {showNavList ? <CloseIcon /> : <MenuIcon />}
      </button>
      <div className="language-switcher" onClick={switchLanguage}>
        {currentLanguage === 'en' ? 'EN' : 'FR'}
      </div>

      <button
        type='button'
        onClick={toggleTheme}
        className='btn btn--icon nav__theme'
        aria-label='toggle theme'
      >
        {themeName === 'dark' ? <WbSunnyRoundedIcon /> : <Brightness2Icon />}
      </button>

      
    </nav>
  )
}

export default Navbar
