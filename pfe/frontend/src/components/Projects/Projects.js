import uniqid from 'uniqid'
import { projects } from '../../Portfolio'
import ProjectContainer from '../ProjectContainer/ProjectContainer'
import './Projects.css'

const Projects = () => {
  if (!projects.length) return null

  return (
    <section id='samples' className='section projects'>
      <h2 className='section__title'>Sample Workflows</h2>

      <div className='projects__grid'>
        {projects.map((project) => (
          <ProjectContainer key={uniqid()} project={project} />
        ))}
      </div>
    </section>
  )
}

export default Projects
