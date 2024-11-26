// src/components/Login/Login.jsx
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../../services/api';

export default function Login() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        pid: '',
        taxi: '',
        password: ''
    });
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await api.login(formData.pid, formData.taxi, formData.password);
            if (response.data.status === 'success') {
                navigate('/dashboard');
            }
        } catch (err) {
            setError(err.response?.data?.error || 'Login failed');
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-100 to-white flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8 bg-white p-10 rounded-xl shadow-lg">
                <div>
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                        Driver Login
                    </h2>
                </div>
                {error && (
                    <div className="bg-red-100 text-red-700 p-3 rounded">
                        {error}
                    </div>
                )}
                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    <div className="rounded-md shadow-sm -space-y-px">
                        <div>
                            <input
                                type="text"
                                required
                                className="appearance-none rounded-none relative block w-full px-3 py-2 border 
                                border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none 
                                focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                                placeholder="Driver ID"
                                value={formData.pid}
                                onChange={(e) => setFormData({...formData, pid: e.target.value})}
                            />
                        </div>
                        <div>
                            <input
                                type="text"
                                required
                                className="appearance-none rounded-none relative block w-full px-3 py-2 border 
                                border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none 
                                focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                                placeholder="Taxi Number"
                                value={formData.taxi}
                                onChange={(e) => setFormData({...formData, taxi: e.target.value})}
                            />
                        </div>
                        <div>
                            <input
                                type="password"
                                required
                                className="appearance-none rounded-none relative block w-full px-3 py-2 border 
                                border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none 
                                focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                                placeholder="Password"
                                value={formData.password}
                                onChange={(e) => setFormData({...formData, password: e.target.value})}
                            />
                        </div>
                    </div>

                    <div>
                        <button
                            type="submit"
                            className="group relative w-full flex justify-center py-2 px-4 border border-transparent 
                            text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 
                            focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                        >
                            Sign in
                        </button>
                    </div>
                </form>
                
                <div className="text-center mt-4">
                    <p className="text-sm text-gray-600">
                        Don't have an account?{' '}
                        <Link 
                            to="/signup" 
                            className="font-medium text-indigo-600 hover:text-indigo-500"
                        >
                            Sign up here
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}