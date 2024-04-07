import React, {useState} from 'react'
import './Sidebar.css'
import 
{BsCart3, BsGrid1X2Fill, BsFillArchiveFill, BsFillGrid3X3GapFill, BsPeopleFill, 
  BsListCheck, BsMenuButtonWideFill, BsFillGearFill}
 from 'react-icons/bs'

 const Sidebar = ({ annotations }) => {
    const [openSidebarToggle, setOpenSidebarToggle] = useState(false)

  const OpenSidebar = () => {
    setOpenSidebarToggle(!openSidebarToggle)
  }
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