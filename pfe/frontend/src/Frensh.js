const header = {
    // all the properties are optional - can be left empty or deleted
    homepage: '/',
    title: 'Verif-BPMN.',
  }
  
  const about = {
    // all the properties are optional - can be left empty or deleted
    name:'Commencer à, Verifier ',
    role: 'Détection des erreurs juridiques dans les processus administratifs.',
    description:
      'Le but principal est de créer une solution capable d\'identifier et de mettre en évidence les incohérences ou erreurs juridiques dans les modèles de processus administratifs. L\'outil est conçu pour améliorer la qualité et la fiabilité des processus administratifs juridiques en fournissant un mécanisme de détection automatique des erreurs, garantissant la conformité aux exigences légales et minimisant le risque de problèmes juridiques dans les procédures administratives.',
    resume: 'https://drive.google.com/file/d/1lptHKG35TLhTgnnzbZpk5fm1iLYGb_3T/view?usp=sharing',
    memoire:'Consulter mémoire'
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
    one : 'exemples processus',
    two : 'se connecter',
    three : 'contact',
  }

  
  
  export { header, about, projects, skills, contact , navbar}
  