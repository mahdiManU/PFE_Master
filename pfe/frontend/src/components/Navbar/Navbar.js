import { useContext, useState } from 'react'
import Brightness2Icon from '@material-ui/icons/Brightness2'
import WbSunnyRoundedIcon from '@material-ui/icons/WbSunnyRounded'
import MenuIcon from '@material-ui/icons/Menu'
import CloseIcon from '@material-ui/icons/Close'
import { ThemeContext } from '../../contexts/theme'
import * as EnglishContent from '../../English';
import * as FrenchContent from '../../Frensh';

import './Navbar.css'
import { Link } from 'react-router-dom';



const Navbar = () => {
  const [{ themeName, toggleTheme }] = useContext(ThemeContext)
  const [showNavList, setShowNavList] = useState(false)
  const [currentLanguage, setCurrentLanguage] = useState('en');

  const { navbar, projects, skills, contact } = currentLanguage === 'en' ? EnglishContent : FrenchContent;

  const switchLanguage = () => {
    setCurrentLanguage(currentLanguage === 'en' ? 'fr' : 'en');
  };

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
        onClick={toggleTheme}
        className='btn btn--icon nav__theme'
        aria-label='toggle theme'
      >
        {themeName === 'dark' ? <WbSunnyRoundedIcon /> : <Brightness2Icon />}
      </button>

      <button
        type='button'
        onClick={toggleNavList}
        className='btn btn--icon nav__hamburger'
        aria-label='toggle navigation'
      >
        {showNavList ? <CloseIcon /> : <MenuIcon />}
      </button>
      <button onClick={switchLanguage}>Switch</button>
    </nav>
  )
}

export default Navbar
