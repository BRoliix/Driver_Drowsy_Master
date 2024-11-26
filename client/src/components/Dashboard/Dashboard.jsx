import React, { useState } from 'react';
import SOSAlerts from '../SOSAlerts/SOSAlerts';

export default function Dashboard() {
    const [activeTab, setActiveTab] = useState('alerts');

    return (
        <div className="min-h-screen bg-gray-50">
            <nav className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16">
                        <div className="flex">
                            <div className="flex-shrink-0 flex items-center">
                                <h1 className="text-xl font-bold text-gray-900">
                                    Driver Monitoring System
                                </h1>
                            </div>
                        </div>
                    </div>
                </div>
            </nav>

            <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                <div className="px-4 py-6 sm:px-0">
                    <div className="border-b border-gray-200">
                        <nav className="-mb-px flex space-x-8">
                            <button
                                onClick={() => setActiveTab('alerts')}
                                className={`${
                                    activeTab === 'alerts'
                                        ? 'border-indigo-500 text-indigo-600'
                                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
                            >
                                SOS Alerts
                            </button>
                            <button
                                onClick={() => setActiveTab('sessions')}
                                className={`${
                                    activeTab === 'sessions'
                                        ? 'border-indigo-500 text-indigo-600'
                                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
                            >
                                Active Sessions
                            </button>
                        </nav>
                    </div>

                    <div className="mt-6">
                        {activeTab === 'alerts' && <SOSAlerts />}
                        {activeTab === 'sessions' && <div>Sessions Component</div>}
                    </div>
                </div>
            </div>
        </div>
    );
}