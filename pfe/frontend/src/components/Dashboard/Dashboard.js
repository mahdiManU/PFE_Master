import React, { useContext, useState } from 'react';
import { useSelector } from 'react-redux';
import './Dashboard.css';
import ProjectListPage from './ProjectListPage';
import { LanguageContext } from '../../contexts/language';
import CreateUser from '../CreateUser/CreateUser'; // Import the CreateUser component

const Dashboard = () => {
  const { currentLanguage } = useContext(LanguageContext);
  const { userInfo } = useSelector((state) => state.auth);
  const [showCreateUser, setShowCreateUser] = useState(false); // State to toggle CreateUser component

  const content = currentLanguage === 'en' ? {
    welcome: 'Welcome',
    annotations: 'Annotations',
    verifyDiagram: 'Verify Diagram',
    createUser: 'Create User'
  } : {
    welcome: 'Bienvenue',
    annotations: 'Annotations',
    verifyDiagram: 'Vérifier le diagramme',
    createUser: 'Créer un utilisateur'
  };

  return (
    <div>
      <div className="container">
        <div className="main-body">
          <div className="promo_card">
            <h1>{content.welcome},<span className='about__name'>{userInfo.first_name}</span></h1>
            <ProjectListPage />
            {userInfo.email === 'imenerabahi25@gmail.com' && (
              <>
                <button onClick={() => setShowCreateUser(!showCreateUser)}>{content.createUser}</button>
                {showCreateUser && <CreateUser />}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
