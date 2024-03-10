import React from 'react';
import './Login.css'; // We'll create this file shortly


const Login = () => {

      return (
        <div className='login center'>
          <h2>Login</h2>
          <form onSubmit={handleSubmit}>
            <label htmlFor='username'>Username</label>
            <input type='text' id='username' name='username' required />
    
            <label htmlFor='password'>Password</label>
            <input type='password' id='password' name='password' required />
    
            <button type='submit'>Sign In</button>
          </form>
    
          <button type='button' className='btn btn--outline' onClick={onClose}>
            Close
          </button>
        </div>
      );
}

export default Login;