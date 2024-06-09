import React from 'react';
import NavDash from '../NavDash/NavDash';
import Dashboard from './Dashboard';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ProjectDetailsPage from './ProjectDetailsPage';
import VerifFront from '../VerifFront/VerifFront';

const Principale = () => {
    return (
        <div>
            <NavDash />
            <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/project/:projectId" element={<ProjectDetailsPage />} />
                <Route path="/project/:projectId/verify/:diagramId" element={<VerifFront />} />
            </Routes>
        </div>
    );
};

export default Principale;
