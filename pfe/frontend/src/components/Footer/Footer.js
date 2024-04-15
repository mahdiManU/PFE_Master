import React, { useContext } from 'react';
import { LanguageContext } from '../../contexts/language';
import './Footer.css';

const Footer = () => {
  const { currentLanguage } = useContext(LanguageContext);
  const createdByText = currentLanguage === 'en' ? 'Created By' : 'Créé Par';

  return (
    <footer className='footer'>
      <a
        href='https://github.com/mahdiManU/PFE_Master'
        className='link footer__link'
      >
        {`${createdByText} RABAHI & BADAOUI`}
      </a>
    </footer>
  );
}

export default Footer;
