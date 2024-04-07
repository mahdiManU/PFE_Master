
import { header } from '../../English'
import Navbar from '../Navbar/Navbar'
import './Header.css'
import { NavLink} from 'react-router-dom'

const Header = () => {
  const { homepage, title } = header

  return (
    <header id="top" className='header center'>
      <h3>
        {homepage ? (
          <NavLink to={homepage} className='link'>
            {title}
          </NavLink>
        ) : (
          title
        )}
      </h3>
        <Navbar />
          
    </header>
  )
}

export default Header
