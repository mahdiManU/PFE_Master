// DashboardLayout.js
import React from 'react';
import NavDash from '../NavDash/NavDash';
import Sidebar from '../Sidebar/Sidebar';

const DashboardLayout = ({ children }) => {
  return (
    <div>
      <NavDash />
      <div className="container">
        <div className="main-body">
          {children}
        </div>
        <Sidebar />
      </div>
    </div>
  );
};

export default DashboardLayout;

