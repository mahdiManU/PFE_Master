import React, { useContext } from 'react';
import { LanguageContext } from '../../contexts/language';
import { projects as EnglishProjects } from '../../English';
import { projects as FrenchProjects } from '../../Frensh';
import ProjectContainer from '../ProjectContainer/ProjectContainer';
import './Projects.css';

const Projects = () => {
  const { currentLanguage } = useContext(LanguageContext);
  const projects = currentLanguage === 'en' ? EnglishProjects : FrenchProjects;

  if (!projects.length) return null;

  return (
    <section id='samples' className='section projects'>
      <h2 className='section__title'>
        {currentLanguage === 'en' ? 'Sample Workflows' : 'Exemples de processus'}
      </h2>

      <div className='projects__grid'>
        {projects.map((project) => (
          <ProjectContainer key={project.name} project={project} />
        ))}
      </div>
    </section>
  );
}

export default Projects;
