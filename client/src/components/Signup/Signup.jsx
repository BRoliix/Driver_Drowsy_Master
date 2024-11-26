import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../services/api';

export default function Signup() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        firstname: '',
        lastname: '',
        code: '',
        password: ''
    });

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await api.signup(formData);
            navigate('/login');
        } catch (err) {
            console.error('Signup failed:', err);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="max-w-md w-full p-6 bg-white rounded-lg shadow-md">
                <h2 className="text-2xl font-bold mb-6">Create Account</h2>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <input
                        type="text"
                        placeholder="First Name"
                        className="w-full p-2 border rounded"
                        value={formData.firstname}
                        onChange={(e) => setFormData({...formData, firstname: e.target.value})}
                    />
                    <input
                        type="text"
                        placeholder="Last Name"
                        className="w-full p-2 border rounded"
                        value={formData.lastname}
                        onChange={(e) => setFormData({...formData, lastname: e.target.value})}
                    />
                    <input
                        type="text"
                        placeholder="Code"
                        className="w-full p-2 border rounded"
                        value={formData.code}
                        onChange={(e) => setFormData({...formData, code: e.target.value})}
                    />
                    <input
                        type="password"
                        placeholder="Password"
                        className="w-full p-2 border rounded"
                        value={formData.password}
                        onChange={(e) => setFormData({...formData, password: e.target.value})}
                    />
                    <button 
                        type="submit"
                        className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
                    >
                        Sign Up
                    </button>
                </form>
            </div>
        </div>
    );
}