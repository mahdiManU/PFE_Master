import React, { useContext } from 'react';
import { LanguageContext } from '../../contexts/language'; 
import { header as EnglishContent}  from '../../English'
import { header as FrenchContent }from '../../Frensh'
import Navbar from '../Navbar/Navbar'
import './Header.css'
import { NavLink} from 'react-router-dom'

const Header = () => {
  const { currentLanguage } = useContext(LanguageContext);
  
  // Dynamically select the header object based on the current language
  const header = currentLanguage === 'en' ? EnglishContent : FrenchContent;


  return (
    <header id="top" className='header center'>
      <h3>
        {header.homepage ? (
          <NavLink to='/' className='link'>
            {header.title}
          </NavLink>
        ) : (
          header.title
        )}
      </h3>
        <Navbar />
          
    </header>
  )
}

export default Header
