import React, { useState } from 'react';
import axios from 'axios';
import { Container, Typography, Button, Box, Snackbar } from '@mui/material';
import MuiAlert from '@mui/material/Alert';

const PerformExercise = () => {
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('success');

  const handlePerformExercise = () => {
    axios.post('http://localhost:5000/api/start_exercise')
      .then(response => {
        setSnackbarMessage(`Exercise completed successfully. Output: ${response.data.output}`);        setSnackbarSeverity('success');
        setSnackbarOpen(true);
      })
      .catch(error => {
        const errorMessage = error.response?.data?.output || 'Error starting exercise';
        setSnackbarMessage(errorMessage);
        setSnackbarSeverity('error');
        setSnackbarOpen(true);
      });
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Perform Exercise
      </Typography>
      <Typography variant="body1" gutterBottom>
        Click the button below to start performing the exercise.
      </Typography>
      <Box mt={2}>
        <Button variant="contained" color="secondary" onClick={handlePerformExercise}>
          Perform Exercise
        </Button>
      </Box>
      <Snackbar open={snackbarOpen} autoHideDuration={6000} onClose={handleSnackbarClose}>
        <MuiAlert onClose={handleSnackbarClose} severity={snackbarSeverity} sx={{ width: '100%' }}>
          {snackbarMessage}
        </MuiAlert>
      </Snackbar>
    </Container>
  );
};

export default PerformExercise;