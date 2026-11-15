import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { FaExternalLinkAlt } from 'react-icons/fa';
import './ProjectContainer.css';

/** Card of one example diagram. `sample` = { id, stack } from src/samples.js. */
const ProjectContainer = ({ sample }) => {
  const { t } = useTranslation();
  return (
    <div className='project'>
      <h3>{t(`samples.${sample.id}.name`)}</h3>
      <p className='project__description'>{t(`samples.${sample.id}.description`)}</p>
      <ul className='project__stack'>
        {sample.stack.map((item) => (
          <li key={item} className='project__stack-item'>{item}</li>
        ))}
      </ul>
      <Link to={`/diagrams/${sample.id}`} aria-label={t('common.view')} className='link link--icon'>
        <FaExternalLinkAlt />
      </Link>
    </div>
  );
};

export default ProjectContainer;