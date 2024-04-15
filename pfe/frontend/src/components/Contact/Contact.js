import React, { useContext } from 'react';
import { LanguageContext } from '../../contexts/language';
import { contact as EnglishContact } from '../../English';
import { contact as FrenchContact } from '../../Frensh';
import './Contact.css';

const Contact = () => {
  const { currentLanguage } = useContext(LanguageContext);
  const contactInfo = currentLanguage === 'en' ? EnglishContact : FrenchContact;

  if (!contactInfo.email) return null;

  return (
    <section className='section contact center' id='contact'>
      <h2 className='section__title'>
        {currentLanguage === 'en' ? 'Contact' : 'Contactez Nous'}
      </h2>
      <a href={`mailto:${contactInfo.email}`}>
        <span type='button' className='btn btn--outline'>
          {currentLanguage === 'en' ? 'Email me' : 'Envoyez un email'}
        </span>
      </a>
    </section>
  );
}

export default Contact;
