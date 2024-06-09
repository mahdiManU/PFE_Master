const header = {
    // all the properties are optional - can be left empty or deleted
    homepage: '/',
    title: 'LegProV',
  }
  
  const about = {
    // all the properties are optional - can be left empty or deleted
    name:'Start, Verifying ',
    role: 'A tool for detecting legal errors in administrative processes',
    description:
      'The primary goal is to create a solution that can identify and highlight any legal inconsistencies or errors within administrative process models. The tool is designed to enhance the quality and reliability of legal administrative processes by providing a mechanism for automated error detection, ensuring compliance with legal requirements and minimizing the risk of legal issues in administrative procedures..',
    resume: 'https://drive.google.com/file/d/1lptHKG35TLhTgnnzbZpk5fm1iLYGb_3T/view?usp=sharing',
    memoire:'view memoire'
  }
  
  const projects = [
    // projects can be added an removed
    // if there are no projects, Projects section won't show up
    {
      name: 'Diagram 1',
      description:
        'C\'est juste un description temporaire elle sera modifer une fois on met des vrai exemples ',
      stack: ['BPMN.io', 'Python', 'Django', 'React'],
      livePreview: 'https://github.com',
    },
    {
      name: 'Diagram 2',
      description:
        'C\'est juste un description temporaire elle sera modifer une fois on met des vrai exemples ',
      stack: ['BPMN.io', 'Python', 'Django', 'React'],
      livePreview: 'https://github.com',
    },
    {
      name: 'Diagram 3',
      description:
        'C\'est juste un description temporaire elle sera modifer une fois on met des vrai exemples ',
      stack: ['BPMN.io', 'Python', 'Django', 'React'],
      livePreview: 'https://github.com',
    },
  ]
  
  const skills = [
    // skills can be added or removed
    // if there are no skills, Skills section won't show up
    'HTML',
    'CSS',
    'JavaScript',
    'TypeScript',
    'React',
    'Redux',
    'SASS',
    'Material UI',
    'Git',
    'CI/CD',
    'Jest',
    'Enzyme',
  ]
  
  const contact = {
    // email is optional - if left empty Contact section won't show up
    email: 'imenerabahi25@mail.com',
  }
  
  const navbar={
    one : 'sample workflows',
    two : 'login',
    three : 'contact',
  }
  

  export { header, about, projects, skills, contact, navbar }
  