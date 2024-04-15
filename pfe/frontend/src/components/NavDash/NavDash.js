import { useContext, useState } from 'react'
import Brightness2Icon from '@material-ui/icons/Brightness2'
import WbSunnyRoundedIcon from '@material-ui/icons/WbSunnyRounded'
import MenuIcon from '@material-ui/icons/Menu'
import CloseIcon from '@material-ui/icons/Close'
import { ThemeContext } from '../../contexts/theme'
import { LanguageContext } from '../../contexts/language'
import './NavDash.css'
import { NavLink, Link, useNavigate } from 'react-router-dom';
import { useDispatch} from 'react-redux'
import { logout, reset} from '../../features/authSlice'



const NavDash = () => {
  const [{ themeName, toggleTheme }] = useContext(ThemeContext)
  const [showNavList, setShowNavList] = useState(false)

  const { currentLanguage, switchLanguage } = useContext(LanguageContext);


  const navigate = useNavigate()
  const dispatch = useDispatch()

    

    const handleLogout = () => {
        dispatch(logout())
        dispatch(reset())
        navigate("/")
    }

  const toggleNavList = () => setShowNavList(!showNavList)

  return (
    <div>
        <header id="top" className='header center'>
      <h3>
          <NavLink to='/dashboard' className='link'>
          {currentLanguage === 'en' ? 'Dashboard' : 'Accueil'}
          </NavLink>

      </h3>
    <nav className='center nav'>
      <ul
        style={{ display: showNavList ? 'flex' : null }}
        className='nav__list'
      >

          <li className='nav__list-item'>
          <Link
            to="" 
            onClick={toggleNavList}
            className='link link--nav'
          >
            {currentLanguage === 'en' ? 'Projects' : 'Projets'}
          </Link>
        </li>

          <li className='nav__list-item'>
            <Link
              to='/'
              onClick={handleLogout}
              className='link link--nav'
            >
              {currentLanguage === 'en' ? 'Logout' : 'Déconnexion'}
            </Link>
          </li>

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
      <div className="language-switcher" onClick={switchLanguage}>
        {currentLanguage === 'en' ? 'EN' : 'FR'}
      </div>
    </nav>
    </header>
    </div>
    
  )
}

export default NavDash
