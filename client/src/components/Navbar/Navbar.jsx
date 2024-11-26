import React from 'react';
import { Link } from 'react-router-dom';

export default function Navbar() {
    return (
        <nav className="bg-indigo-600">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    <div className="flex items-center">
                        <Link to="/" className="text-white font-bold text-xl">
                            DrowsinessGuard
                        </Link>
                        <div className="hidden md:block ml-10">
                            <div className="flex space-x-4">
                                <Link to="/dashboard" 
                                      className="text-white hover:bg-indigo-700 px-3 py-2 rounded-md">
                                    Dashboard
                                </Link>
                                <Link to="/alerts" 
                                      className="text-white hover:bg-indigo-700 px-3 py-2 rounded-md">
                                    Alerts
                                </Link>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    );
}