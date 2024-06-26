import React, { useEffect, useState, useContext } from 'react';
import { useSelector } from 'react-redux';
import axios from 'axios';
import './UserManagement.css'; // Import CSS file for styling
import { LanguageContext } from '../../contexts/language';

const UserManagement = () => {
  const { currentLanguage } = useContext(LanguageContext);
  const { token } = useSelector((state) => state.auth);
  const [users, setUsers] = useState([]);

  const content = currentLanguage === 'en' ? {
    manag: 'User Management',
    listmail: 'Email',
    listname :'First Name',
    listsurname: 'Last Name',
    projet : 'Projects',
    projetcomp : 'Completed Projects',
    delete : 'Delete',
    creat : 'Create New User',
    mail: 'Email',
    name :'First Name',
    surname: 'Last Name',
    password : 'Password',
    repeat : 'Confirm Password',
    btncree: 'Create User'

  } : {
    manag: 'Gestion des Utilisateurs',
    listmail: 'Email',
    listname: 'Prénom',
    listsurname: 'Nom de famille',
    projet: 'Projets',
    projetcomp: 'Projets terminés',
    delete: 'Supprimer',
    creat: 'Créer un nouvel utilisateur',
    mail: 'Email',
    name: 'Prénom',
    surname: 'Nom de famille',
    password: 'Mot de passe',
    repeat: 'Confirmer le mot de passe',
    btncree: 'Créer utilisateur'
  };

  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  useEffect(() => {
    fetchUsers();
  }, [token]);

  const fetchUsers = () => {
    const accessToken = localStorage.getItem('access');
    axios.get('http://127.0.0.1:8000/api/users/', {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    })
    .then(response => {
      setUsers(response.data);
    })
    .catch(error => {
      console.error('There was an error fetching the users!', error);
    });
  };

  const deleteUser = (userId) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      const accessToken = localStorage.getItem('access');
      axios.delete(`http://127.0.0.1:8000/api/users/${userId}/`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      })
      .then(response => {
        setUsers(users.filter(user => user.id !== userId));
      })
      .catch(error => {
        console.error('There was an error deleting the user!', error);
      });
    }
  };

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const accessToken = localStorage.getItem('access');
    axios.post('http://127.0.0.1:8000/api/users/', formData, {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    })
    .then(response => {
      fetchUsers(); // Refresh the user list after successful creation
      setFormData({
        firstName: '',
        lastName: '',
        email: '',
        password: '',
        confirmPassword: ''
      });
    })
    .catch(error => {
      console.error('There was an error creating the user!', error);
    });
  };

  return (
    <div className='container'>
      <div className='main-body'>
        <div className='user-list'>
          <h1>{content.manag}</h1>
          <table className='user-table'>
            <thead>
              <tr>
                <th>{content.listmail}</th>
                <th>{content.listname}</th>
                <th>{content.listsurname}</th>
                <th>{content.projet}</th>
                <th>{content.projetcomp}</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {users.map(user => (
                <tr key={user.id}>
                  <td>{user.email}</td>
                  <td>{user.first_name}</td>
                  <td>{user.last_name}</td>
                  <td>{user.num_projects}</td>
                  <td>{user.num_completed_projects}</td>
                  <td>
                    <button className='action-button' onClick={() => deleteUser(user.id)}>{content.delete}</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className='create-user-form'>
          <h2>{content.creat}</h2>
          <form onSubmit={handleSubmit}>
            <input
              type='text'
              name='firstName'
              placeholder={content.name}
              value={formData.firstName}
              onChange={handleInputChange}
              required
            />
            <input
              type='text'
              name='lastName'
              placeholder={content.surname}
              value={formData.lastName}
              onChange={handleInputChange}
              required
            />
            <input
              type='email'
              name='email'
              placeholder={content.mail}
              value={formData.email}
              onChange={handleInputChange}
              required
            />
            <input
              type='password'
              name='password'
              placeholder={content.password}
              value={formData.password}
              onChange={handleInputChange}
              required
            />
            <input
              type='password'
              name='confirmPassword'
              placeholder={content.repeat}
              value={formData.confirmPassword}
              onChange={handleInputChange}
              required
            />
            <button type='submit'>{content.btncree}</button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default UserManagement;
