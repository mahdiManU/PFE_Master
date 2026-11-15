import { useTranslation } from 'react-i18next';
import { THESIS_URL } from '../../config';
import './About.css';

/** Presentation block of the home page. */
const About = () => {
  const { t } = useTranslation();
  return (
    <div className='about center'>
      <h1>
        {t('home.title')}<span className='about__name'>{t('home.highlight')}</span>
      </h1>
      <h2 className='about__role'>{t('home.role')}.</h2>
      <p className='about__desc'>{t('home.description')}</p>
      <div className='about__contact center'>
        <a href={THESIS_URL} target='_blank' rel='noopener noreferrer'>
          <span className='btn btn--outline'>{t('home.thesis')}</span>
        </a>
      </div>
    </div>
  );
};

export default About;