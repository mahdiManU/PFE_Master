import React, { useContext} from 'react'
import { useSelector} from 'react-redux'
import './Dashboard.css'
import ProjectListPage from './ProjectListPage';
import { LanguageContext } from '../../contexts/language';




const Dashboard = () => {
    const { currentLanguage } = useContext(LanguageContext);
    const { userInfo } = useSelector((state) => state.auth)
   // const [annotations, setAnnotations] = useState([]);

    const content = currentLanguage === 'en' ? {
        welcome: 'Welcome',
        annotations: 'Annotations',
        verifyDiagram: 'Verify Diagram'
      } : {
        welcome: 'Bienvenue',
        annotations: 'Annotations',
        verifyDiagram: 'Vérifier le diagramme'
      };

    return (
        <div>
      <div className="container">
        <div className="main-body">
          <div className="promo_card">
            <h1>{content.welcome},<span className='about__name'>{userInfo.first_name}</span></h1>
            <ProjectListPage/>
          </div>
        </div>
        
      </div>
    </div>
    )
}

export default Dashboard
