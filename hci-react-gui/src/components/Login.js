import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Typography, Button, Box, Snackbar, Grid, Card, CardContent, CardActions, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, TextField, AppBar, Toolbar, Paper } from '@mui/material';
import MuiAlert from '@mui/material/Alert';
import { useNavigate } from 'react-router-dom';
import HomeIcon from '@mui/icons-material/Home';
import { io } from 'socket.io-client';

const Login = () => {
  const [tuioIds, setTuioIds] = useState([]);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('success');
  const [open, setOpen] = useState(false);
  const [selectedTuioId, setSelectedTuioId] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch TUIO IDs from the server
    axios.get('http://localhost:5000/api/tuio_ids')
      .then(response => {
        setTuioIds(response.data);
      })
      .catch(error => {
        console.error('Error fetching TUIO IDs:', error);
      });

    // Establish WebSocket connection
    const socket = io('http://localhost:5000');

    socket.on('login_event', (data) => {
      const { patient } = data;
      console.log('Received login_event:', patient);  // Add this line for debugging
      localStorage.setItem('patient', JSON.stringify(patient));
      setSnackbarMessage('Login successful');
      setSnackbarSeverity('success');
      setSnackbarOpen(true);
      navigate('/patient-exercise-dashboard', { state: { patient } });
    });

    return () => {
      socket.disconnect();
      console.log("Socket disconnected");
    };
  }, [navigate]); // Add navigate dependency

  const handleLogin = () => {
    axios.post('http://localhost:5000/api/verify_tuio_id', { tuio_id: selectedTuioId })
      .then(response => {
        if (response.data.valid) {
          axios.post('http://localhost:5000/api/patients/login', { tuio_id: selectedTuioId })
            .then(response => {
              localStorage.setItem('patient', JSON.stringify(response.data.patient));
              setSnackbarMessage('Login successful');
              setSnackbarSeverity('success');
              setSnackbarOpen(true);
              navigate('/patient-exercise-dashboard', { state: { patient: response.data.patient } });
            })
            .catch(() => {
              axios.post('http://localhost:5000/api/doctors/login', { tuio_id: selectedTuioId })
                .then(response => {
                  localStorage.setItem('doctor', JSON.stringify(response.data.doctor));
                  setSnackbarMessage('Login successful');
                  setSnackbarSeverity('success');
                  setSnackbarOpen(true);
                  navigate('/doctor-dashboard', { state: { doctor: response.data.doctor } });
                })
                .catch(error => {
                  setSnackbarMessage('Invalid TUIO ID');
                  setSnackbarSeverity('error');
                  setSnackbarOpen(true);
                });
            });
        } else {
          setSnackbarMessage('Invalid TUIO ID');
          setSnackbarSeverity('error');
          setSnackbarOpen(true);
        }
      })
      .catch(error => {
        console.error('Error verifying TUIO ID:', error);
        setSnackbarMessage('Error verifying TUIO ID');
        setSnackbarSeverity('error');
        setSnackbarOpen(true);
      });
  };

  const handleFaceLogin = () => {
    axios.post('http://localhost:5000/api/face_login')
      .then(response => {
        if (response.data.success) {
          localStorage.setItem('patient', JSON.stringify(response.data.patient));
          setSnackbarMessage('Face login successful');
          setSnackbarSeverity('success');
          setSnackbarOpen(true);
          navigate('/patient-exercise-dashboard', { state: { patient: response.data.patient } });
        } else {
          setSnackbarMessage(response.data.message);
          setSnackbarSeverity('error');
          setSnackbarOpen(true);
        }
      })
      .catch(error => {
        console.error('Error during face login:', error);
        setSnackbarMessage('Error during face login');
        setSnackbarSeverity('error');
        setSnackbarOpen(true);
      });
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  const handleClickOpen = (tuioId) => {
    setSelectedTuioId(tuioId);
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  return (
    <Box display="flex" flexDirection="column" height="100vh">
      <AppBar position="static" style={{ background: '#5c67f2' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Recovery Hub
          </Typography>
          <Button
            variant="contained"
            color="secondary"
            startIcon={<HomeIcon />}
            onClick={() => navigate('/')}
            sx={{ borderRadius: 20 }}
          >
            Home
          </Button>
        </Toolbar>
      </AppBar>
      <Container maxWidth="sm" sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <Paper elevation={3} sx={{ padding: 4, borderRadius: 2 }}>
          <Box display="flex" flexDirection="column" alignItems="center">
            <Typography variant="h4" component="h1" gutterBottom>
              Login
            </Typography>
            <Typography variant="h6" component="h2" gutterBottom>
              Please show your ID to access your recovery plan
            </Typography>
            <Dialog open={open} onClose={handleClose}>
              <DialogTitle>Login</DialogTitle>
              <DialogContent>
                <DialogContentText>
                  Please confirm your TUIO ID to access your recovery plan.
                </DialogContentText>
                <TextField
                  autoFocus
                  margin="dense"
                  label="TUIO ID"
                  type="text"
                  fullWidth
                  value={selectedTuioId}
                  onChange={(e) => setSelectedTuioId(e.target.value)}
                />
              </DialogContent>
              <DialogActions>
                <Button onClick={handleClose} color="primary">
                  Cancel
                </Button>
                <Button onClick={handleLogin} color="primary">
                  Login
                </Button>
              </DialogActions>
            </Dialog>
            <Button variant="contained" color="primary" onClick={handleFaceLogin} sx={{ mt: 2 }}>
              Login with Face Recognition
            </Button>
            <Snackbar open={snackbarOpen} autoHideDuration={6000} onClose={handleSnackbarClose}>
              <MuiAlert onClose={handleSnackbarClose} severity={snackbarSeverity} sx={{ width: '100%' }}>
                {snackbarMessage}
              </MuiAlert>
            </Snackbar>
          </Box>
        </Paper>
      </Container>
      <Box component="footer" py={2} textAlign="center" bgcolor="#5c67f2" color="white">
        <Typography variant="body2">
          &copy; {new Date().getFullYear()} Recovery Hub. All rights reserved.
        </Typography>
      </Box>
    </Box>
  );
};

export default Login;
