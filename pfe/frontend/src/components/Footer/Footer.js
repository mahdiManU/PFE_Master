import { useTranslation } from 'react-i18next';
import { REPO_URL } from '../../config';
import './Footer.css';

const Footer = () => {
  const { t } = useTranslation();
  return (
    <footer className='footer'>
      <a href={REPO_URL} className='link footer__link' target='_blank' rel='noopener noreferrer'>
        {`${t('footer.createdBy')} RABAHI & BADAOUI`}
      </a>
    </footer>
  );
};

export default Footer;