// src/components/Dashboard/Dashboard.jsx
import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { getUserInfo } from '../../features/authSlice';
import ProjectListPage from './ProjectListPage';
import './Dashboard.css';

/** Home of the logged-in area: welcome message, projects, admin shortcut. */
const Dashboard = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { userInfo } = useSelector((state) => state.auth);

  // After a page reload the user info is empty: load it again.
  useEffect(() => {
    if (!userInfo.id) dispatch(getUserInfo());
  }, [userInfo.id, dispatch]);

  return (
    <div className="container">
      <div className="main-body">
        <div className="promo_card">
          <h1>{t('dashboard.welcome')}, <span className="about__name">{userInfo.first_name}</span></h1>
          <ProjectListPage />
          {userInfo.is_staff && (
            <button onClick={() => navigate('/dashboard/user-management')}>
              {t('dashboard.manageUsers')}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;