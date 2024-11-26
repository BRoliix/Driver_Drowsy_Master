import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';

export default function SOSAlerts() {
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAlerts = async () => {
            try {
                const response = await api.getSOSAlerts();
                setAlerts(response.data);
            } catch (error) {
                console.error('Failed to fetch alerts:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchAlerts();
        const interval = setInterval(fetchAlerts, 10000); // Refresh every 10 seconds
        return () => clearInterval(interval);
    }, []);

    if (loading) return (
        <div className="flex justify-center items-center h-48">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
        </div>
    );

    return (
        <div className="p-6">
            <h2 className="text-2xl font-bold mb-4">SOS Alerts</h2>
            <div className="grid gap-4">
                {alerts.map((alert) => (
                    <div key={alert._id} 
                         className="bg-red-50 border border-red-200 rounded-lg p-4 shadow-sm">
                        <div className="flex justify-between items-start">
                            <div>
                                <p className="font-semibold">Alert ID: {alert._id}</p>
                                <p>Driver ID: {alert.driverid}</p>
                                <p>Taxi ID: {alert.taxiid}</p>
                                <p>Details: {alert.details}</p>
                                <p>Status: {alert.status}</p>
                            </div>
                            <div className="text-sm text-gray-500">
                                <p>Created: {new Date(alert.createdtime).toLocaleString()}</p>
                                {alert.actionedtime && (
                                    <p>Actioned: {new Date(alert.actionedtime).toLocaleString()}</p>
                                )}
                            </div>
                        </div>
                    </div>
                ))}
                {alerts.length === 0 && (
                    <p className="text-gray-500 text-center">No active alerts</p>
                )}
            </div>
        </div>
    );
}