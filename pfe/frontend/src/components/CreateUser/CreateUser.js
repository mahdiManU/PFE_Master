import React, { useState, useContext } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { createUser } from '../../features/authSlice';
import './CreateUser.css'; // Import the CSS file
import { LanguageContext } from '../../contexts/language';

const CreateUser = () => {
  const { currentLanguage } = useContext(LanguageContext);
  const content = currentLanguage === 'en' ? {
    createUser: 'Create User',
    firstNameLabel: 'First Name',
    lastNameLabel: 'Last Name',
    emailLabel: 'E-mail Address',
    passwordLabel: 'Password',
    rePasswordLabel: 'Re-enter Password',
    createButton: 'Create',
    successMessage: 'User created successfully.',
    errors: {
      firstNameRequired: 'Please provide a first name.',
      lastNameRequired: 'Please provide a last name.',
      emailRequired: 'Please provide an email address.',
      passwordRequired: 'Please provide a password.',
      rePasswordRequired: 'Please re-enter the password.',
      passwordMismatch: 'Passwords do not match.',
      invalidEmail: 'Invalid email format.',
    }
  } : {
    createUser: 'Créer un utilisateur',
    firstNameLabel: 'Prénom',
    lastNameLabel: 'Nom de famille',
    emailLabel: 'Adresse e-mail',
    passwordLabel: 'Mot de passe',
    rePasswordLabel: 'Confirmer le mot de passe',
    createButton: 'Créer',
    successMessage: 'Utilisateur créé avec succès.',
    errors: {
      firstNameRequired: 'Veuillez fournir un prénom.',
      lastNameRequired: 'Veuillez fournir un nom de famille.',
      emailRequired: 'Veuillez fournir une adresse e-mail.',
      passwordRequired: 'Veuillez fournir un mot de passe.',
      rePasswordRequired: 'Veuillez confirmer le mot de passe.',
      passwordMismatch: 'Les mots de passe ne correspondent pas.',
      invalidEmail: 'Format d\'e-mail invalide.',
    }
  };

  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    rePassword: "",
  });

  const { firstName, lastName, email, password, rePassword } = formData;

  const dispatch = useDispatch();
  const { isSuccess, message } = useSelector((state) => state.auth);

  const [firstNameError, setFirstNameError] = useState('');
  const [lastNameError, setLastNameError] = useState('');
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [rePasswordError, setRePasswordError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false); // State to manage modal visibility

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
    if (e.target.name === 'firstName') setFirstNameError('');
    if (e.target.name === 'lastName') setLastNameError('');
    if (e.target.name === 'email') setEmailError('');
    if (e.target.name === 'password') setPasswordError('');
    if (e.target.name === 'rePassword') setRePasswordError('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!firstName) {
      setFirstNameError(content.errors.firstNameRequired);
      return;
    }
    if (!lastName) {
      setLastNameError(content.errors.lastNameRequired);
      return;
    }
    if (!email) {
      setEmailError(content.errors.emailRequired);
      return;
    }
    if (!password) {
      setPasswordError(content.errors.passwordRequired);
      return;
    }
    if (!rePassword) {
      setRePasswordError(content.errors.rePasswordRequired);
      return;
    }
    if (password !== rePassword) {
      setRePasswordError(content.errors.passwordMismatch);
      return;
    }
    const userData = {
      firstName,
      lastName,
      email,
      password,
    };
    dispatch(createUser(userData));
  };

  return (
    <div>
      <button onClick={() => setIsModalOpen(true)} className='open-modal-button'>{content.createUser}</button>
      {isModalOpen && (
        <div className='modal-overlay'>
          <div className='modal-content'>
            <button onClick={() => setIsModalOpen(false)} className='close-modal-button'>X</button>
            <h2>{content.createUser}</h2>
            <form onSubmit={handleSubmit}>
              <label htmlFor='firstName'>{content.firstNameLabel}</label>
              <input type='text' id='firstName' name='firstName' onChange={handleChange}
                value={firstName} required />
              {firstNameError && <span className="error">{firstNameError}</span>}
              <label htmlFor='lastName'>{content.lastNameLabel}</label>
              <input type='text' id='lastName' name='lastName' onChange={handleChange}
                value={lastName} required />
              {lastNameError && <span className="error">{lastNameError}</span>}
              <label htmlFor='email'>{content.emailLabel}</label>
              <input type='email' id='email' name='email' onChange={handleChange}
                value={email} required />
              {emailError && <span className="error">{emailError}</span>}
              <label htmlFor='password'>{content.passwordLabel}</label>
              <input type='password' id='password' name='password' onChange={handleChange}
                value={password} required autoComplete="off" />
              {passwordError && <span className="error">{passwordError}</span>}
              <label htmlFor='rePassword'>{content.rePasswordLabel}</label>
              <input type='password' id='rePassword' name='rePassword' onChange={handleChange}
                value={rePassword} required autoComplete="off" />
              {rePasswordError && <span className="error">{rePasswordError}</span>}
              <button type='submit' className='create-button'>{content.createButton}</button>
              {isSuccess && <span className="success">{content.successMessage}</span>}
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default CreateUser;
