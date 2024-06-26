// src/components/Dashboard/Dashboard.jsx
import React, { useContext, useState } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';
import ProjectListPage from './ProjectListPage';
import { LanguageContext } from '../../contexts/language';

const Dashboard = () => {
  const { currentLanguage } = useContext(LanguageContext);
  const { userInfo } = useSelector((state) => state.auth);
  const navigate = useNavigate();
  
  const content = currentLanguage === 'en' ? {
    welcome: 'Welcome',
    annotations: 'Annotations',
    verifyDiagram: 'Verify Diagram',
    manageUsers: 'Manage Users'
  } : {
    welcome: 'Bienvenue',
    annotations: 'Annotations',
    verifyDiagram: 'Vérifier le diagramme',
    manageUsers: 'Gérer les utilisateurs'
  };

  const handleManageUsersClick = () => {
    navigate('/dashboard/user-management');
  };

  return (
    <div>
      <div className="container">
        <div className="main-body">
          <div className="promo_card">
            <h1>{content.welcome},<span className='about__name'>{userInfo.first_name}</span></h1>
            <ProjectListPage />
            {userInfo.email === 'imenerabahi25@gmail.com' && (
              <button onClick={handleManageUsersClick}>{content.manageUsers}</button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
