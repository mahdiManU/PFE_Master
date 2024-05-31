import axios from 'axios';
import Cookies from 'js-cookie';

const fetchCsrfToken = async () => {
    try {
        const response = await axios.get('http://127.0.0.1:8000/api/csrf-token/', { withCredentials: true });
        Cookies.set('csrftoken', response.data.csrfToken);
        console.log('Fetched CSRF token:', response.data.csrfToken);
        return response.data.csrfToken;
    } catch (error) {
        console.error('Error fetching CSRF token:', error);
        throw error;
    }
};

export default fetchCsrfToken;