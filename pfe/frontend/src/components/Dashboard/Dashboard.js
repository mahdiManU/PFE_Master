import React, {useState} from 'react'
import { useSelector } from 'react-redux'
import NavDash from '../NavDash/NavDash'
import './Dashboard.css'


const Dashboard = () => {

    const { userInfo } = useSelector((state) => state.auth)


    return (
        <div>
            <NavDash />
            <div className="container">
                <nav>
                    <div className="side_navbar">
                        <span>Main Menu</span>
                        <a href='#' className="active">Dashboard</a>
                        <a href="#">Projects</a>
                        <a href="#">New Project</a>
                        <a href="#">Profile</a>
                        <div className="links">
                        
                        </div>
                    </div>
                </nav>
                <div className="main-body">
                    <div className="promo_card">
                        <h1>Welcome, {userInfo.first_name} </h1>
                        
                        <input type="file" name="document" />
                        <button > Verify diagram</button>
                        
                    </div>
                   
                </div>
    
            </div>
            
        </div>
    )
}

export default Dashboard