import React from 'react';
import { useEffect, useState } from "react"
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate , Link} from "react-router-dom"
import { login, reset, getUserInfo } from '../../features/authSlice'
import './Login.css'; 


const Login = () => {

  const [formData, setFormData] = useState({
    "email": "",
    "password": "",
  })

  const { email, password } = formData

    const dispatch = useDispatch()
    const navigate = useNavigate()

    const { user, isError, isSuccess, message } = useSelector((state) => state.auth)

    // State variables to hold inline error messages
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [userError, setUserError]=useState('');
 
  const handleChange = (e) => {
    setFormData((prev) => ({
        ...prev,
        [e.target.name]: e.target.value
    })
    )
    // Clear inline error messages when user starts typing in the fields
    if (e.target.name === 'email') setEmailError(''); setUserError('');
    if (e.target.name === 'password') setPasswordError(''); setUserError('');
  }


  const handleSubmit = (e) => {
    e.preventDefault()
    // Validate email and password
    if (!email) {
      setEmailError('Please provide your email.');
      return;
    }
    if (!password) {
      setPasswordError('Please provide your password.');
      return;
    }
    const userData = {
      email,
      password,
  }
  dispatch(login(userData))

  }

  useEffect(() => {
    if (isError) {
      setUserError('Invalid email or password. Please try again.')
    }

    if (isSuccess || user) {
        navigate("/dashboard")
    }

    dispatch(reset())
    dispatch(getUserInfo())

}, [isError, isSuccess, user,message, navigate, dispatch])

  return (
     <div className='login center'>
       <h2>Login</h2>
         <form >
         {userError && <span className="error">{userError}</span>}
            <label htmlFor='email'>E-mail</label>
            <input type='text' id='email' name='email' onChange={handleChange}
                        value={email} required />
                        {emailError && <span className="error">{emailError}</span>}
    
            <label htmlFor='password'>Password</label>
            <input type='password' id='password' name='password' onChange={handleChange}
                         value={password} required />
                         {passwordError && <span className="error">{passwordError}</span>}
                          
            <Link to="/reset-password">Forget Password ?</Link>            
    
            <button type='submit' onClick={handleSubmit}>Sign In</button>
          </form>
          
          <button type='button' className='btn btn--outline'  >
            X
          </button>
      </div>
  );
}

export default Login;