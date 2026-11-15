import { useTranslation } from 'react-i18next';
import { CONTACT_EMAIL } from '../../config';
import './Contact.css';

const Contact = () => {
  const { t } = useTranslation();
  return (
    <section className='section contact center' id='contact'>
      <h2 className='section__title'>{t('home.contactTitle')}</h2>
      <a href={`mailto:${CONTACT_EMAIL}`}>
        <span className='btn btn--outline'>{t('home.emailMe')}</span>
      </a>
    </section>
  );
};

export default Contact;