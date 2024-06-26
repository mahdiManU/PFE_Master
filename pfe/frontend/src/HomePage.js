import About from './components/About/About'
import Projects from './components/Projects/Projects'
import Contact from './components/Contact/Contact'


const HomePage = () => {
  return (
    <div>
      <section id="about">
        <About />
      </section>
      <section id="projects">
        <Projects />
      </section>
      <section id="contact">
        <Contact />
      </section>
    </div>
  )
}

export default HomePage
