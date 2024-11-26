import axios from 'axios';

const BASE_URL = 'http://127.0.0.1:6060';

export const api = {
    login: async (pid, taxi, password) => {
        const formData = new FormData();
        formData.append('pid', pid);
        formData.append('taxi', taxi);
        formData.append('password', password);
        return axios.post(`${BASE_URL}/login`, formData);
    },
    
    adminLogin: async (pid, password) => {
        return axios.get(`${BASE_URL}/admlogin`, {
            params: {
                pid,
                password,
                jsonp: 'callback'
            }
        });
    },
    
    getSessions: async () => {
        return axios.get(`${BASE_URL}/session`, {
            params: {
                jsonp: 'callback'
            }
        });
    },
    
    getSOSAlerts: async () => {
        return axios.get(`${BASE_URL}/sos`, {
            params: {
                jsonp: 'callback'
            }
        });
    },

    signup: async (userData) => {
        return axios.post(`${BASE_URL}/user`, {
            headers: {
                'Content-Type': 'application/json'
            },
            data: userData
        });
    }
};
