import uniqid from 'uniqid'
import { FaGithub, FaExternalLinkAlt } from 'react-icons/fa';
import './ProjectContainer.css'
import { Link } from 'react-router-dom';

const ProjectContainer = ({ project }) => (
  <div className='project'>
    <h3>{project.name}</h3>

    <p className='project__description'>{project.description}</p>
    {project.stack && (
      <ul className='project__stack'>
        {project.stack.map((item) => (
          <li key={uniqid()} className='project__stack-item'>
            {item}
          </li>
        ))}
      </ul>
    )}

    {project.sourceCode && (
      <a
        href={project.sourceCode}
        aria-label='source code'
        className='link link--icon'
      >
        <FaGithub />
      </a>
    )}

    {project.livePreview && (
      <Link
      to={project.livePreview}
      aria-label='live preview'
      className='link link--icon'
    >
      <FaExternalLinkAlt />
    </Link>
    )}
  </div>
)

export default ProjectContainer
