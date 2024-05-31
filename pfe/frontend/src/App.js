import { useContext} from 'react'
import { ThemeContext } from './contexts/theme'
import MainLayout from "./MainLayout";
import Login from './components/Login/Login'
import './App.css'
import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import HomePage from './HomePage'
import Principale from './components/Dashboard/Principale'
import axios from 'axios';



const App = () => {
 
  
  const [{ themeName }] = useContext(ThemeContext)

  return (
    <div id='top' className={`${themeName} app`}>
      <Router>
        <Routes>
          <Route path="/" element={<MainLayout><HomePage /></MainLayout>} />
          <Route path="/login" element={<MainLayout><Login /></MainLayout>} />
          <Route path="/dashboard/*" element={<Principale />} />
        </Routes>
      </Router>
    </div>
  )
}

export default App

