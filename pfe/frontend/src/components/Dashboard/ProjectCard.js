import React from 'react';
import './CardAndPage.css';

const ProjectCard = ({ project }) => {
  return (
    <div className="project-card">
      <h3>{project.name}</h3>
      <p>{project.description}</p>
      <p>Number of diagrams: 0</p>
    </div>
  );
};

export default ProjectCard;
