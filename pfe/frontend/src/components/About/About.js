import React, { useContext } from 'react';
import { LanguageContext } from '../../contexts/language';
import * as EnglishContent from '../../English';
import * as FrenchContent from '../../Frensh';
import './About.css'

const About = () => {
  const { currentLanguage } = useContext(LanguageContext);

  const cont = currentLanguage === 'en' ? {
    verif: 'Verification'
  } : {
    verif: 'Vérification'
  };
  // Dynamically select the content based on the current language
  const content = currentLanguage === 'en' ? EnglishContent : FrenchContent;
  const {name, role, description, resume, memoire } = content.about;

  return (
    <div className='about center'>
      {name && (
        <h1>
          {name}<span className='about__name'>{cont.verif}</span>
        </h1>
      )}

      {role && <h2 className='about__role'>{role}.</h2>}
      <p className='about__desc'>{description && description}</p>

      <div className='about__contact center'>
        {resume && (
          <a href={resume} target="_blank">
            <span type='button' className='btn btn--outline'>
            {memoire}
            </span>
          </a>
        )}
      </div>
    </div>
  )
}

export default About