import React, { useState } from 'react';
import axios from 'axios';

const CreateProjectForm = ({ onSuccess }) => {
  const [formData, setFormData] = useState({ name: '', description: '' });
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };


  const createProject = async (projectData) => {

    try {
        const accessToken = localStorage.getItem('access');
        console.log(accessToken)
        if (!accessToken) {
            throw new Error('Access token not found.');
        }

        const response = await axios.get('http://127.0.0.1:8000/api/projects/', projectData, {
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        });


          return response.data;

    } catch (error) {
        setError(error.message || 'Failed');
    }

};

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {

      console.log('Project created:', createProject(formData));
      // Call the onSuccess callback if provided
      if (onSuccess) {
        onSuccess(createProject(formData));
      }
      // Clear the form fields after successful project creation
      setFormData({ name: '', description: '' });
    } catch (error) {
      console.error('Error creating project:', error);
      // You can handle errors (e.g., display an error message)
    }
  };

  return (
    <div>
      <h3>Create New Project</h3>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="name">Name:</label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label htmlFor="description">Description:</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            required
          />
        </div>
        <button type="submit">Create Project</button>
      </form>
    </div>
  );
};

export default CreateProjectForm;
