import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';

export default function AdminDashboard() {
    const [sosAlerts, setSOSAlerts] = useState([]);
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [alertsRes, sessionsRes] = await Promise.all([
                    api.getSOSAlerts(),
                    api.getSessions()
                ]);
                setSOSAlerts(alertsRes.data);
                setSessions(sessionsRes.data);
            } catch (err) {
                setError('Failed to fetch data');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds
        return () => clearInterval(interval);
    }, []);

    if (loading) return <div className="text-center p-8">Loading...</div>;
    if (error) return <div className="text-red-600 p-8">{error}</div>;

    return (
        <div className="container mx-auto p-8">
            <h1 className="text-2xl font-bold mb-8">Admin Dashboard</h1>
            
            <div className="mb-8">
                <h2 className="text-xl font-semibold mb-4">Active SOS Alerts</h2>
                <div className="grid gap-4">
                    {sosAlerts.map((alert) => (
                        <div key={alert._id} className="bg-red-50 p-4 rounded-lg">
                            <p className="font-medium">Driver ID: {alert.driverid}</p>
                            <p>Status: {alert.status}</p>
                            <p>Details: {alert.details}</p>
                            <p className="text-sm text-gray-500">
                                Created: {new Date(alert.createdtime).toLocaleString()}
                            </p>
                        </div>
                    ))}
                </div>
            </div>
            
            <div>
                <h2 className="text-xl font-semibold mb-4">Active Sessions</h2>
                <div className="grid gap-4">
                    {sessions.map((session) => (
                        <div key={session._id} className="bg-white shadow p-4 rounded-lg">
                            <p>Taxi: {session.TaxiNumber}</p>
                            <p>Driver: {session.FirstName} {session.LastName}</p>
                            <p>Status: {session.Status}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}