import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';

export default function Sessions() {
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchSessions = async () => {
            try {
                const response = await api.getSessions();
                setSessions(response.data);
            } catch (error) {
                console.error('Failed to fetch sessions:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchSessions();
        const interval = setInterval(fetchSessions, 30000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="space-y-4">
            <h2 className="text-2xl font-bold text-gray-900">Active Sessions</h2>
            {loading ? (
                <div className="flex justify-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                </div>
            ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {sessions.map((session) => (
                        <div key={session._id} className="bg-white rounded-lg shadow p-6">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center">
                                    <div className="ml-3">
                                        <p className="text-sm font-medium text-gray-900">
                                            {session.FirstName} {session.LastName}
                                        </p>
                                        <p className="text-sm text-gray-500">
                                            Taxi: {session.TaxiNumber}
                                        </p>
                                    </div>
                                </div>
                                <span className={`px-2 py-1 text-xs font-semibold rounded-full 
                                    ${session.Status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                    {session.Status}
                                </span>
                            </div>
                            <div className="text-sm text-gray-500">
                                <p>Start: {new Date(session.StartTime).toLocaleString()}</p>
                                <p>End: {new Date(session.EndTime).toLocaleString()}</p>
                            </div>
                        </div>
                    ))}
                    {sessions.length === 0 && (
                        <p className="text-center text-gray-500">No active sessions</p>
                    )}
                </div>
            )}
        </div>
    );
}