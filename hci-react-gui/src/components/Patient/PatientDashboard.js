import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Typography, Box, Card, CardContent, List, ListItem, ListItemText } from '@mui/material';

const PatientDashboard = () => {
  const [plan, setPlan] = useState(null);
  const patient = JSON.parse(localStorage.getItem('patient'));

  useEffect(() => {
    if (patient) {
      // Fetch patient's plan data from the server
      axios.get(`http://localhost:5000/api/patient/plan?patient_id=${patient._id}`)
        .then(response => {
          setPlan(response.data);
        })
        .catch(error => {
          console.error('Error fetching plan:', error);
        });
    }
  }, [patient]);

  return (
    <Container maxWidth="md">
      <Box my={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          Patient Dashboard
        </Typography>
        {plan ? (
          <Card>
            <CardContent>
              <Typography variant="h5" component="h2">
                {plan.name}'s Plan
              </Typography>
              <Typography variant="body1" component="p">
                Code: {plan.code}
              </Typography>
              <Typography variant="body1" component="p">
                Injury: {plan.injury}
              </Typography>
              <Typography variant="h6" component="h3" gutterBottom>
                Exercises:
              </Typography>
              <List>
                {plan.exercises.map((exercise, index) => (
                  <ListItem key={index}>
                    <ListItemText
                      primary={exercise.name}
                      secondary={`Sets: ${exercise.sets}, Reps: ${exercise.reps}`}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        ) : (
          <Typography variant="body1" component="p">
            Loading plan...
          </Typography>
        )}
      </Box>
    </Container>
  );
};

export default PatientDashboard;