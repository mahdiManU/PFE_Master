import React, { useContext } from 'react';
import { LanguageContext } from '../../contexts/language'; 
import { header as EnglishContent } from '../../English';
import { header as FrenchContent } from '../../Frensh';
import Navbar from '../Navbar/Navbar';
import './Header.css';
import iconImage from '../../icon.png'; // Import your icon image
import { NavLink } from 'react-router-dom';

const Header = () => {
  const { currentLanguage } = useContext(LanguageContext);
  
  // Dynamically select the header object based on the current language
  const header = currentLanguage === 'en' ? EnglishContent : FrenchContent;

  return (
    <header id="top" className='header center'>
      <div className="header-content">
        <h3>
          {header.homepage ? (
            <NavLink to='/' className='link'>
              {header.title}
            </NavLink>
          ) : (
            header.title
          )}
        </h3>
        <img src={iconImage} alt="Icon" className="header-icon" /> {/* Display the icon image */}
      </div>
      <Navbar />
    </header>
  );
}

export default Header;
