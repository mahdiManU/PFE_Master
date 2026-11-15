import { useTranslation } from 'react-i18next';
import { SAMPLES } from '../../samples';
import ProjectContainer from '../ProjectContainer/ProjectContainer';
import './Projects.css';

/** Grid of the example diagrams on the home page (data in src/samples.js). */
const Projects = () => {
  const { t } = useTranslation();
  return (
    <section id='samples' className='section projects'>
      <h2 className='section__title'>{t('home.samplesTitle')}</h2>
      <div className='projects__grid'>
        {SAMPLES.map((sample) => (
          <ProjectContainer key={sample.id} sample={sample} />
        ))}
      </div>
    </section>
  );
};

export default Projects;