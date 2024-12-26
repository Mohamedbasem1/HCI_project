import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import io from 'socket.io-client';
import DoctorDashboard from './components/Doctor/DoctorDashboard';
import PatientDashboard from './components/Patient/PatientDashboard';
import PatientExerciseDashboard from './components/Patient/PatientExerciseDashboard';
import KidExerciseDashboard from './components/Kid/KidExerciseDashboard';
import KidPerformExercise from './components/Kid/KidPerformExercise';
import HomeScreen from './components/HomeScreen';
import Login from './components/Login';
import GestureControl from './components/GestureControl';

const socket = io('http://localhost:5000');

function App() {
  const [tuioData, setTuioData] = useState(null);

  useEffect(() => {
    socket.on('connect', () => {
      console.log('Connected to TUIO server');
    });

    socket.on('tuio_event', (data) => {
      console.log('Received TUIO message:', data);
      setTuioData(data);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<HomeScreen />} />
          <Route path="/doctor" element={<DoctorDashboard />} />
          <Route path="/patient-dashboard" element={<PatientDashboard />} />
          <Route path="/patient-exercise-dashboard" element={<PatientExerciseDashboard />} />
          <Route path="/patient/exercises/:id" element={<PatientExerciseDashboard />} />
          <Route path="/kid/exercises/:id" element={<KidExerciseDashboard />} />
          <Route path="/kid/perform-exercise" element={<KidPerformExercise />} />
          <Route path="/login" element={<Login />} />
        </Routes>
      </div>
      <GestureControl />
    </Router>
  );
}

export default App;
