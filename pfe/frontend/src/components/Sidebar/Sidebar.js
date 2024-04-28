import React, {useState} from 'react'
import './Sidebar.css'


 const Sidebar = ({ annotations }) => {
    const [openSidebarToggle] = useState(false)


  return (

        <div  id="sidebar" className={openSidebarToggle ? "sidebar-responsive": ""}>
            <h2>Annotations</h2>
            <ul>
                {annotations.map((annotation, index) => (
                    <li key={index}>{annotation}</li>
                ))}
            </ul>
        </div>
    );
};


export default Sidebar