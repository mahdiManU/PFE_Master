import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { login, reset, getUserInfo } from '../../features/authSlice';
import './Login.css';

const Login = () => {
  const { t, i18n } = useTranslation();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user, isError } = useSelector((state) => state.auth);
  const location = useLocation();

  const [formData, setFormData] = useState({ email: '', password: '' });
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [userError, setUserError] = useState('');
  const { email, password } = formData;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear the error of the edited field and the general error.
    if (name === 'email') setEmailError('');
    if (name === 'password') setPasswordError('');
    setUserError('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!email) return setEmailError(t('login.errors.emailRequired'));
    if (!password) return setPasswordError(t('login.errors.passwordRequired'));
    dispatch(login({ email, password }));
  };

  useEffect(() => {
    if (isError) setUserError(t('login.errors.invalidCredentials'));
    if (user) {
      dispatch(getUserInfo()); // loads first name / email for the dashboard
      navigate('/dashboard');
    }
    dispatch(reset());
  }, [isError, user, navigate, dispatch, t, i18n.language]);

  return (
    <div className={`login ${i18n.language}`}>
      <button type='button' className='btn btn--outline reset-button'
        onClick={() => { setFormData({ email: '', password: '' }); setEmailError(''); setPasswordError(''); setUserError(''); }}>
        X
      </button>
      <h2>{t('login.title')}</h2>
      <form onSubmit={handleSubmit}>
        {location.state?.registered && <span className="success">{t('login.registered')}</span>}
        {userError && <span className='error'>{userError}</span>}
        <label htmlFor='email'>{t('login.email')}</label>
        <input type='email' id='email' name='email' onChange={handleChange} value={email} required />
        {emailError && <span className='error'>{emailError}</span>}
        <label htmlFor='password'>{t('login.password')}</label>
        <input type='password' id='password' name='password' onChange={handleChange}
          value={password} required autoComplete='current-password' />
        {passwordError && <span className='error'>{passwordError}</span>}
        <button type='submit'>{t('login.signIn')}</button>
        <p style={{ marginTop: '1em' }}>
          {t('login.noAccount')} <Link to="/register" className="link">{t('register.title')}</Link>
        </p>
      </form>
    </div>
  );
};

export default Login;