import React, { useContext } from 'react';
import { useEffect, useState } from "react"
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate , Link} from "react-router-dom"
import { login, reset, getUserInfo } from '../../features/authSlice'
import './Login.css'; 
import { LanguageContext } from '../../contexts/language';




const Login = () => {
  const { currentLanguage } = useContext(LanguageContext);
  const content = currentLanguage === 'en' ? {
    login: 'Login',
    emailLabel: 'E-mail',
    passwordLabel: 'Password',
    forgetPasswordLink: 'Forget Password ?',
    signInButton: 'Sign In',
    errors: {
      emailRequired: 'Please provide your email.',
      passwordRequired: 'Please provide your password.',
      invalidCredentials: 'Invalid email or password. Please try again.'
    }
  } : {
    login: 'Se Connecter',
    emailLabel: 'E-mail',
    passwordLabel: 'Mot de passe',
    forgetPasswordLink: 'Mot de passe oublié ?',
    signInButton: 'Connexion',
    errors: {
      emailRequired: 'Veuillez fournir votre adresse e-mail.',
      passwordRequired: 'Veuillez fournir votre mot de passe.',
      invalidCredentials: 'E-mail ou mot de passe incorrect. Veuillez réessayer.'
    }
  };

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
    e.preventDefault();
    // Validate email and password
    if (!email) {
        setEmailError(content.errors.emailRequired);
        return;
    }
    if (!password) {
        setPasswordError(content.errors.passwordRequired);
        return;
    }
    const userData = {
        email,
        password,
    };
    // Dispatch the login action
    dispatch(login(userData))
    
  };

  useEffect(() => {
    if (isError) {
      setUserError(content.errors.invalidCredentials)
    }

    if (isSuccess || user) {
        navigate("/dashboard")
    }

    dispatch(reset())
    dispatch(getUserInfo())

}, [isError, isSuccess, user, message, navigate, dispatch, content.errors.invalidCredentials])

  return (
     <div className={`login ${currentLanguage} `}>
      {/* Reset button for clearing form fields */}
      <button type='button' className='btn btn--outline reset-button' onClick={() => {
  setFormData({ email: '', password: '' });
  setEmailError('');
  setPasswordError('');
  setUserError('');
}}>
  X
</button>
       <h2>{content.login}</h2>
         <form >
         {userError && <span className="error">{userError}</span>}
            <label htmlFor='email'>{content.emailLabel}</label>
            <input type='text' id='email' name='email' onChange={handleChange}
                        value={email} required  />
                        {emailError && <span className="error">{emailError}</span>}
    
            <label htmlFor='password'>{content.passwordLabel}</label>
            <input type='password' id='password' name='password' onChange={handleChange}
                         value={password} required autoComplete="off"  />
                         {passwordError && <span className="error">{passwordError}</span>}
                          
            <Link to="/reset-password">{content.forgetPasswordLink}</Link>            
    
            <button type='submit' onClick={handleSubmit}>{content.signInButton}</button>
          </form>
      </div>
      
  );
}

export default Login;