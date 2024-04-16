import React from 'react';
import './App.css';
import Session from './pages/session';
import SOS from './pages/sos';
import TEST from './pages/test';
import { BrowserRouter as Router, Routes, Route }
	from 'react-router-dom';
import Navbar from './components/Navbar';

function App() {
	return (
		<Router>
			<Navbar />
			<div align={'center'}>
			<Routes>
				<Route path='/session' element={<Session/>} />
				<Route path='/sos' element={<SOS/>} />
				<Route path='/test' element={<TEST/>} />

			</Routes>
			</div>

		</Router>
	);
}

export default App
