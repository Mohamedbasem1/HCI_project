import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  Container, Typography, Card, CardContent, CardMedia, Button, Grid, Box, AppBar, Toolbar, Snackbar, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle
} from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import MuiAlert from '@mui/material/Alert';
import { styled } from '@mui/material/styles';
import io from 'socket.io-client';
import GestureControl from '../GestureControl';
import GestureFeedback from '../GestureFeedback';

const StyledCard = styled(Card)(({ theme }) => ({
  transition: 'box-shadow 0.3s',
  '&:hover': {
    boxShadow: theme.shadows[6],
  },
}));

const StyledButton = styled(Button)(({ theme }) => ({
  borderRadius: 20,
  transition: 'background-color 0.3s, transform 0.3s',
  '&:hover': {
    backgroundColor: theme.palette.primary.dark,
    transform: 'scale(1.05)',
  },
}));

const PatientExerciseDashboard = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [patient, setPatient] = useState(location.state?.patient || JSON.parse(localStorage.getItem('patient'))); // Retrieve patient data from state or local storage
  const [exercises, setExercises] = useState([]);
  const [currentExerciseIndex, setCurrentExerciseIndex] = useState(0);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('success');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [exerciseResult, setExerciseResult] = useState('');
  const [currentGesture, setCurrentGesture] = useState(null);

  useEffect(() => {
    if (patient && patient._id) {
      // Fetch patient's exercises data from the server
      axios.get(`http://localhost:5000/api/patients/${patient._id}/exercises`)
        .then(response => {
          setExercises(response.data);
        })
        .catch(error => {
          console.error('Error fetching exercises:', error);
        });
    }
  }, [patient]);

  useEffect(() => {
    // Establish WebSocket connection
    const socket = io('http://localhost:5000');

    socket.on('login_event', (data) => {
      console.log('Received login event:', data);
      if (data.patient) {
        console.log('Navigating to patient exercises:', data.patient._id);
        navigate(`/patient/exercises/${data.patient._id}`);
      } else if (data.doctor) {
        console.log('Navigating to doctor dashboard');
        navigate(`/doctor/dashboard`);
      }
    });

    return () => {
      socket.disconnect();
      console.log("Socket disconnected");
    };
  }, [navigate]);

  const handleNextExercise = () => {
    if (currentExerciseIndex < exercises.length - 1) {
      setCurrentExerciseIndex(currentExerciseIndex + 1);
      setSnackbarMessage('Next exercise');
      setSnackbarSeverity('info');
      setSnackbarOpen(true);
    }
  };

  const handlePreviousExercise = () => {
    if (currentExerciseIndex > 0) {
      setCurrentExerciseIndex(currentExerciseIndex - 1);
      setSnackbarMessage('Previous exercise');
      setSnackbarSeverity('info');
      setSnackbarOpen(true);
    }
  };

  const handlePerformExercise = () => {
    setDialogOpen(false); // Close the dialog window
    setExerciseResult('Performing exercise...'); // Set initial result message
    axios.post('http://localhost:5000/api/start_exercise')
      .then(response => {
        console.log('Exercise response:', response.data);  // Add this line for debugging
        setSnackbarMessage(`Exercise completed successfully. Output: ${response.data.output}`);
        setSnackbarSeverity('success');
        setSnackbarOpen(true);
        setExerciseResult(`Exercise completed successfully. Output: ${response.data.output}`); // Set the exercise result
      })
      .catch(error => {
        console.error('Error performing exercise:', error);  // Add this line for debugging
        setSnackbarMessage('Error performing exercise');
        setSnackbarSeverity('error');
        setSnackbarOpen(true);
        setExerciseResult('Error performing exercise'); // Set error message
      });
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  const handleDialogOpen = () => {
    setDialogOpen(true);
  };

  const handleDialogClose = () => {
    setDialogOpen(false);
  };

  if (!patient) {
    return (
      <Container maxWidth="md">
        <Typography variant="h4" component="h1" gutterBottom>
          No patient data available. Please log in again.
        </Typography>
      </Container>
    );
  }

  return (
    <Box display="flex" flexDirection="column" height="100vh">
      <AppBar position="static" style={{ background: '#5c67f2' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Patient Exercise Dashboard
          </Typography>
          <StyledButton
            variant="contained"
            color="secondary"
            startIcon={<HomeIcon />}
            onClick={() => navigate('/')}
          >
            Home
          </StyledButton>
        </Toolbar>
      </AppBar>
      
      <Container maxWidth="md" sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <Box my={4} flexGrow={1}>
          <Typography variant="h4" gutterBottom>
            {patient.name}'s Exercise Plan
          </Typography>
          <Typography variant="h6" gutterBottom>
            Injury: {patient.injury}
          </Typography>
          <Typography variant="h6" gutterBottom>
            You have {exercises.length} exercise{exercises.length !== 1 && 's'} today
          </Typography>
          {exercises.length > 0 && (
            <Grid container spacing={4} sx={{ flexGrow: 1 }}>
              <Grid item xs={12} sx={{ flexGrow: 1 }}>
                <StyledCard sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardMedia
                    component="video"
                    controls
                    muted
                    src={`http://localhost:5000/${exercises[currentExerciseIndex].video_url}`}
                    title={exercises[currentExerciseIndex].name}
                    sx={{ flexGrow: 1 }}
                  />
                  <CardContent>
                    <Typography variant="h5" component="div">
                      {exercises[currentExerciseIndex].name}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {exercises[currentExerciseIndex].description}
                    </Typography>
                    <Typography variant="body1" component="div">
                      Sets: {exercises[currentExerciseIndex].sets}
                    </Typography>
                    <Typography variant="body1" component="div">
                      Reps: {exercises[currentExerciseIndex].reps}
                    </Typography>
                    <Box mt={2}>
                      <StyledButton variant="contained" color="primary" onClick={handlePerformExercise}>
                        Perform Exercise
                      </StyledButton>
                      {exerciseResult && (
                        <Typography variant="body1" mt={2}>
                          Result: {exerciseResult}
                        </Typography>
                      )}
                    </Box>
                  </CardContent>
                </StyledCard>
              </Grid>
              <Grid item xs={12} display="flex" justifyContent="space-between">
                <StyledButton
                  variant="contained"
                  color="primary"
                  disabled={currentExerciseIndex === 0}
                  onClick={handlePreviousExercise}
                >
                  Previous
                </StyledButton>
                <StyledButton
                  variant="contained"
                  color="primary"
                  disabled={currentExerciseIndex === exercises.length - 1}
                  onClick={handleNextExercise}
                >
                  Next
                </StyledButton>
              </Grid>
            </Grid>
          )}
        </Box>
      </Container>

      {/* Gesture Control Integration */}
      <GestureControl 
        onNextExercise={handleNextExercise}
        onPreviousExercise={handlePreviousExercise}
        onPerformExercise={handlePerformExercise}
        onNavigateHome={() => navigate('/')}
        onGestureDetected={setCurrentGesture}
      />
      <GestureFeedback gesture={currentGesture} />
      
      {/* Gesture Guide */}
      <Box 
        position="fixed" 
        bottom={20} 
        right={20} 
        p={2} 
        bgcolor="rgba(0,0,0,0.1)" 
        borderRadius={2}
        sx={{ 
          backdropFilter: 'blur(10px)',
          zIndex: 1000,
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
          border: '1px solid rgba(255,255,255,0.1)'
        }}
      >
        <Typography variant="body2" sx={{ fontWeight: 500 }}>
          Gesture Controls:
          <br />
          Thumbs Up: Next Exercise
          <br />
          Thumbs Down: Previous Exercise
          <br />
          Swipe Right: Perform Exercise
          <br />
          Swipe Left: Return Home
        </Typography>
      </Box>

      <Dialog open={dialogOpen} onClose={handleDialogClose}>
        <DialogTitle>Perform Exercise</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Click the button below to start performing the exercise.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <StyledButton onClick={handleDialogClose} color="primary">
            Cancel
          </StyledButton>
          <StyledButton onClick={handlePerformExercise} color="primary">
            Perform Exercise
          </StyledButton>
        </DialogActions>
      </Dialog>

      <Snackbar open={snackbarOpen} autoHideDuration={6000} onClose={handleSnackbarClose}>
        <MuiAlert 
          elevation={6} 
          variant="filled" 
          onClose={handleSnackbarClose} 
          severity={snackbarSeverity} 
          sx={{ width: '100%' }}
        >
          {snackbarMessage}
        </MuiAlert>
      </Snackbar>
    </Box>
  );
};

export default PatientExerciseDashboard;
