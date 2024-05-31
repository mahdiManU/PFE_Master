import React from 'react';
import './CardAndPage.css';
import { LanguageContext } from '../../contexts/language'
import { useContext } from 'react'
import './CardAndPage.css'
import { Link } from 'react-router-dom';

const ProjectCard = ({ project }) => {
  const { currentLanguage} = useContext(LanguageContext);
  return (
    <div className="project-card">
      <h3 className='project__description'>{project.name}</h3>
      <p>{project.description}</p>
      <p className='diag_number'>{currentLanguage === 'en' ? 'Number of Diagrams :' : 'Totale Diagrames :'} {project.num_diagrams}</p>
      <Link to={`/dashboard/project/${project.id}`} className="btn-details">
    {currentLanguage === 'en' ? 'Details' : 'Détails'}
</Link>
    </div>
  );
};

export default ProjectCard;
