import { NavLink } from 'react-router-dom';
import Navbar from '../Navbar/Navbar';
import iconImage from '../../icon.png';
import './Header.css';

/** Top bar of the public pages: application name, logo and navigation. */
const Header = () => (
  <header id='top' className='header center'>
    <div className='header-content'>
      <h3>
        <NavLink to='/' className='link'>LegProV</NavLink>
      </h3>
      <img src={iconImage} alt='' className='header-icon' />
    </div>
    <Navbar />
  </header>
);

export default Header;