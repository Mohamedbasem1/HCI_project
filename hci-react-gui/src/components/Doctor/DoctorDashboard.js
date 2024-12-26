import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Container, Typography, TextField, Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle,
  MenuItem, Select, InputLabel, FormControl, Snackbar, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Grid, AppBar, Toolbar, Box
} from '@mui/material';
import MuiAlert from '@mui/material/Alert';
import AddIcon from '@mui/icons-material/Add'; // Correct import statement
import HomeIcon from '@mui/icons-material/Home'; // Import Home icon
import { styled } from '@mui/material/styles';
import Autocomplete from '@mui/material/Autocomplete'; // Import Autocomplete
import { useNavigate } from 'react-router-dom'; // Import useNavigate
import MoreVertIcon from '@mui/icons-material/MoreVert'; // Import MoreVert icon
import CircularMenu from '../CircularMenu'; // Import CircularMenu
import io from 'socket.io-client'; // Add this import

const hoverAndSelectedColor = '#ff9800'; // Change to a different color (e.g., orange)
const brighterBorderColor = '#ffcc80'; // Adjust the brighter border color accordingly
const buttonHoverColor = '#ff5722'; // Change to a different hover color (e.g., deep orange)
const animationDuration = '0.3s'; // Define animation duration
const hoverBorderColor = '#42a5f5'; // Define a light blue hover border color
const strongHoverColor = '#ff7043'; // Define a strong hover color

const StyledTableRow = styled(TableRow)(({ theme }) => ({
  '&:nth-of-type(odd)': {
    backgroundColor: theme.palette.action.hover,
  },
  '&:nth-of-type(even)': {
    backgroundColor: theme.palette.background.default,
  },
  '&:hover': {
    backgroundColor: theme.palette.action.selected,
    border: `2px solid ${hoverBorderColor}`, // Light blue border color for hovered row
    transition: `border ${animationDuration} ease-in-out`, // Add animation
  },
  '&.Mui-selected': {
    backgroundColor: theme.palette.action.selected,
    border: `2px solid ${hoverAndSelectedColor}`, // Border for selected row
  },
  '&.Mui-hovered, &.Mui-focused': { // Add hover and focus color
    backgroundColor: strongHoverColor, // Use strong hover color
    border: `2px solid ${hoverBorderColor}`, // Light blue border color for hovered row
    transition: `border ${animationDuration} ease-in-out`, // Add animation
  },
}));

const StyledButton = styled(Button)(({ theme }) => ({
  backgroundColor: theme.palette.primary.main,
  '&:hover': {
    backgroundColor: buttonHoverColor, // More suitable hover color for buttons
    border: `2px solid ${hoverBorderColor}`, // Light blue border color for hovered button
    transition: `border ${animationDuration} ease-in-out`, // Add animation
  },
  '&.Mui-selected': {
    backgroundColor: hoverAndSelectedColor, // Highlight selected button
    border: `2px solid ${hoverBorderColor}`, // Light blue border color for selected button
    transition: `border ${animationDuration} ease-in-out`, // Add animation
  },
  '&.Mui-hovered, &.Mui-focused': {
    backgroundColor: strongHoverColor, // Use strong hover color
    border: `2px solid ${hoverBorderColor}`,
    transition: `border ${animationDuration} ease-in-out`,
  },
}));

const DoctorDashboard = () => {
  const [patients, setPatients] = useState([]);
  const [currentPatientId, setCurrentPatientId] = useState(null);
  const [newPatient, setNewPatient] = useState({ name: '', injury: '', exercises: [], type: '' }); // Add type field
  const [injuries, setInjuries] = useState([]);
  const [filteredExercises, setFilteredExercises] = useState([]);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('success');
  const [selectedRow, setSelectedRow] = useState(null); // Initialize selectedRow to null
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false); // State for delete confirmation dialog
  const [patientToDelete, setPatientToDelete] = useState(null); // State for patient to delete
  const navigate = useNavigate(); // Initialize useNavigate
  const [menuOpen, setMenuOpen] = useState(false); // State for menu visibility
  const [currentSection, setCurrentSection] = useState('table'); // Set default section to 'table'
  const [hoveredRow, setHoveredRow] = useState(null); // Add state for hovered row
  const [selectedElement, setSelectedElement] = useState('home'); // State for selected element
  const [selectedMenuButton, setSelectedMenuButton] = useState(0); // State for selected menu button
  const [selectedFormElement, setSelectedFormElement] = useState('injury'); // State for selected form element, start with 'injury'
  const [filteredPatients, setFilteredPatients] = useState([]); // Define filteredPatients state
  const [selectedPatient, setSelectedPatient] = useState(null); // Define selectedPatient state
  const [open, setOpen] = useState(false); // Define open state
  const [isEditing, setIsEditing] = useState(false); // Define isEditing state
  const [imageFile, setImageFile] = useState(null); // Add state for image file

  useEffect(() => {
    // Fetch patients data from the server
    axios.get('http://localhost:5000/api/patients')
      .then(response => {
        setPatients(response.data);
        setFilteredPatients(response.data); // Initialize filtered patients
      })
      .catch(error => {
        console.error('Error fetching patients:', error);
        if (error.response) {
          console.error('Error response:', error.response);
        }
      });

    // Fetch injuries data from the server
    axios.get('http://localhost:5000/api/injuries')
      .then(response => {
        // console.log('Fetched injuries:', response.data);
        setInjuries(response.data);
      })
      .catch(error => {
        console.error('Error fetching injuries:', error);
        if (error.response) {
          console.error('Error response:', error.response);
        }
      });

    // Remove WebSocket connection
  }, []); // Remove filteredPatients.length dependency

  useEffect(() => {
    if (currentSection === 'home') {
      navigate('/');
    } else if (currentSection === 'addPatient') {
      handleClickOpen();
    } else if (currentSection === 'table') {
      // Focus on the table
      document.getElementById('patients-table').scrollIntoView({ behavior: 'smooth' });
    }
  }, [currentSection, navigate]); // Remove 'sections' from dependency array

  useEffect(() => {
    const handleRotateEvent = (event) => {
      const { direction } = event.detail;
      if (direction === 'rotate_left') {
        if (selectedElement === 'home') {
          setSelectedElement('table');
        } else if (selectedElement === 'addPatient') {
          setSelectedElement('home');
        } else if (selectedElement === 'table') {
          if (selectedRow === 0) {
            setSelectedElement('addPatient');
          } else {
            setSelectedRow((prevRow) => (prevRow > 0 ? prevRow - 1 : filteredPatients.length - 1));
          }
        }
      } else if (direction === 'rotate_right') {
        if (selectedElement === 'home') {
          setSelectedElement('addPatient');
        } else if (selectedElement === 'addPatient') {
          setSelectedElement('table');
        } else if (selectedElement === 'table') {
          setSelectedRow((prevRow) => (prevRow < filteredPatients.length - 1 ? prevRow + 1 : 0));
        }
      }
    };

    window.addEventListener('rotate_event', handleRotateEvent);

    return () => {
      window.removeEventListener('rotate_event', handleRotateEvent);
    };
  }, [selectedElement, filteredPatients.length, selectedRow]);

  useEffect(() => {
    const handleRotateEvent = (event) => {
      const { direction } = event.detail;
      console.log(`Received rotate event: ${direction}`); // Add this line
      if (direction === 'rotate_left') {
        if (selectedElement === 'home') {
          setSelectedElement('table');
        } else if (selectedElement === 'addPatient') {
          setSelectedElement('home');
        } else if (selectedElement === 'table') {
          setSelectedElement('addPatient');
        }
      } else if (direction === 'rotate_right') {
        if (selectedElement === 'home') {
          setSelectedElement('addPatient');
        } else if (selectedElement === 'addPatient') {
          setSelectedElement('table');
        } else if (selectedElement === 'table') {
          setSelectedElement('home');
        }
      }
    };

    window.addEventListener('rotate_event', handleRotateEvent);

    return () => {
      window.removeEventListener('rotate_event', handleRotateEvent);
    };
  }, [selectedElement]);

  useEffect(() => {
    console.log(`Selected element: ${selectedElement}`);
    if (selectedElement === 'home') {
      document.getElementById('home-button').focus();
    } else if (selectedElement === 'addPatient') {
      document.getElementById('add-patient-button').focus();
    } else if (selectedElement === 'table') {
      document.getElementById('patients-table').scrollIntoView({ behavior: 'smooth' });
    }
  }, [selectedElement]);

  useEffect(() => {
    // Establish WebSocket connection
    const socket = io('http://localhost:5000');

    socket.on('rotate_event', (data) => {
      console.log(`Received rotate event: ${data.direction}`);
      if (menuOpen) {
        // Control the circular menu
        if (data.direction === 'rotate_right') {
          setSelectedMenuButton((prevButton) => (prevButton + 1) % 3);
        } else if (data.direction === 'rotate_left') {
          setSelectedMenuButton((prevButton) => (prevButton - 1 + 3) % 3);
        }
      } else {
        // Control the main dashboard
        if (data.direction === 'rotate_right') {
          if (selectedElement === 'home') {
            setSelectedElement('addPatient');
          } else if (selectedElement === 'addPatient') {
            setSelectedElement('table');
          } else if (selectedElement === 'table') {
            setSelectedRow((prevRow) => (prevRow < filteredPatients.length - 1 ? prevRow + 1 : 0));
          }
        } else if (data.direction === 'rotate_left') {
          if (selectedElement === 'table') {
            if (selectedRow === 0) {
              setSelectedElement('addPatient');
            } else {
              setSelectedRow((prevRow) => (prevRow > 0 ? prevRow - 1 : filteredPatients.length - 1));
            }
          } else if (selectedElement === 'addPatient') {
            setSelectedElement('home');
          } else if (selectedElement === 'home') {
            setSelectedElement('table');
          }
        }
      }
    });

    socket.on('click_event', () => {
      console.log('Received click event');
      if (menuOpen) {
        // Handle click in circular menu
        if (selectedMenuButton === 0) {
          handleEditPatient(selectedPatient);
        } else if (selectedMenuButton === 1) {
          handleMenuClose();
        } else if (selectedMenuButton === 2) {
          handleDeletePatient(selectedPatient._id); // Directly delete the patient
        }
      } else {
        // Handle click in main dashboard
        if (selectedElement === 'home') {
          navigate('/');
        } else if (selectedElement === 'addPatient') {
          handleClickOpen();
        } else if (selectedElement === 'table' && selectedRow !== null) {
          const selectedPatient = filteredPatients[selectedRow];
          handleMenuOpen(selectedPatient);
        }
      }
    });

    return () => {
      socket.disconnect();
      console.log("Socket disconnected");
    };
  }, [selectedElement, filteredPatients.length, menuOpen, selectedMenuButton, selectedRow]);

  useEffect(() => {
    console.log(`Selected element: ${selectedElement}`);
    if (selectedElement === 'home') {
      document.getElementById('home-button').focus();
    } else if (selectedElement === 'addPatient') {
      document.getElementById('add-patient-button').focus();
    } else if (selectedElement === 'table') {
      document.getElementById('patients-table').scrollIntoView({ behavior: 'smooth' });
    }
  }, [selectedElement]);

  useEffect(() => {
    const handleRotateEvent = (event) => {
      const { direction } = event.detail;
      if (open) { // Only handle rotation events if the form is open
        if (direction === 'rotate_left') {
          if (selectedFormElement === 'injury') {
            setSelectedFormElement('add');
          } else if (selectedFormElement === 'exercises') {
            setSelectedFormElement('injury');
          } else if (selectedFormElement === 'cancel') {
            setSelectedFormElement('exercises');
          } else if (selectedFormElement === 'add') {
            setSelectedFormElement('cancel');
          }
        } else if (direction === 'rotate_right') {
          if (selectedFormElement === 'injury') {
            setSelectedFormElement('exercises');
          } else if (selectedFormElement === 'exercises') {
            setSelectedFormElement('cancel');
          } else if (selectedFormElement === 'cancel') {
            setSelectedFormElement('add');
          } else if (selectedFormElement === 'add') {
            setSelectedFormElement('injury');
          }
        }
      } else {
        if (direction === 'rotate_left') {
          if (selectedElement === 'home') {
            setSelectedElement('table');
          } else if (selectedElement === 'addPatient') {
            setSelectedElement('home');
          } else if (selectedElement === 'table') {
            if (selectedRow === 0) {
              setSelectedElement('addPatient');
            } else {
              setSelectedRow((prevRow) => (prevRow > 0 ? prevRow - 1 : filteredPatients.length - 1));
            }
          }
        } else if (direction === 'rotate_right') {
          if (selectedElement === 'home') {
            setSelectedElement('addPatient');
          } else if (selectedElement === 'addPatient') {
            setSelectedElement('table');
          } else if (selectedElement === 'table') {
            setSelectedRow((prevRow) => (prevRow < filteredPatients.length - 1 ? prevRow + 1 : 0));
          }
        }
      }
    };

    window.addEventListener('rotate_event', handleRotateEvent);

    return () => {
      window.removeEventListener('rotate_event', handleRotateEvent);
    };
  }, [selectedElement, selectedFormElement, filteredPatients.length, selectedRow, open]);

  const handleSearchChange = (event, value) => {
    if (value) {
      const filtered = patients.filter(patient => patient.name.toLowerCase().includes(value.toLowerCase()));
      setFilteredPatients(filtered);
    } else {
      setFilteredPatients(patients);
    }
  };

  const handleSearchSelect = (event, value) => {
    if (value) {
      const selectedPatient = patients.find(patient => patient.name === value);
      if (selectedPatient) {
        setFilteredPatients([selectedPatient]); // Show only the selected patient
        setSelectedRow(0); // Reset selected row
        setSelectedPatient(selectedPatient); // Set the selected patient
      }
    } else {
      setFilteredPatients(patients); // Show all patients if no selection
      setSelectedPatient(null); // Clear the selected patient
    }
  };

  const handleClickOpen = () => {
    axios.get('http://localhost:5000/api/generate_patient_details')
      .then(response => {
        setNewPatient({
          name: response.data.name,
          tuio_id: response.data.tuio_id,
          injury: '',
          exercises: [],
          type: '' // Add type field
        });
        setOpen(true);
        setSelectedFormElement('injury'); // Set initial form element to 'injury'
      })
      .catch(error => {
        console.error('Error generating patient details:', error);
        setSnackbarMessage('Failed to generate patient details');
        setSnackbarSeverity('error');
        setSnackbarOpen(true);
      });
  };

  const handleClose = () => {
    setOpen(false);
    setIsEditing(false);
    setCurrentPatientId(null);
    setNewPatient({ name: '', injury: '', exercises: [], type: '' }); // Add type field
    setSelectedFormElement(null); // Reset form element selection
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name === 'injury') {
      const selectedInjury = injuries.find(injury => injury.name === value);
      if (selectedInjury) {
        setFilteredExercises(selectedInjury.exercises);
      } else {
        setFilteredExercises([]);
      }
      setNewPatient({ ...newPatient, [name]: value, exercises: [] }); // Clear exercises when injury is changed
    } else {
      setNewPatient({ ...newPatient, [name]: value });
    }
  };

  const handleExerciseChange = (event) => {
    const { value } = event.target;
    setNewPatient({ ...newPatient, exercises: value });
  };

  const handleFileChange = (event) => {
    setImageFile(event.target.files[0]);
  };

  const handleAddPatient = () => {
    if (!newPatient.name || !newPatient.injury || !newPatient.exercises.length || !imageFile || !newPatient.type) {
      setSnackbarMessage('Please fill in all fields, select at least one exercise, an image, and specify the patient type.');
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
      return;
    }
  
    const selectedInjury = injuries.find(injury => injury.name === newPatient.injury);
    if (!selectedInjury) {
      console.error(`Injury not found: ${newPatient.injury}`);
      return;
    }
  
    const patientData = new FormData();
    patientData.append('name', newPatient.name);
    patientData.append('tuio_id', newPatient.tuio_id);
    patientData.append('injury', newPatient.injury);
    patientData.append('exercises', newPatient.exercises.join(','));
    patientData.append('image', imageFile); // Append image file
    patientData.append('type', newPatient.type); // Append patient type
  
    axios.post('http://localhost:5000/api/patients', patientData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
      .then(response => {
        setPatients([...patients, response.data]);
        setFilteredPatients([...patients, response.data]); // Update filtered patients
        setSnackbarMessage('Patient added successfully');
        setSnackbarSeverity('success');
        setSnackbarOpen(true);
        setOpen(false); // Close the modal after successful operation
        setNewPatient({ name: '', injury: '', exercises: [], type: '' }); // Reset form
        setImageFile(null); // Reset image file
      })
      .catch(error => {
        console.error('Error adding patient:', error);
        if (error.response) {
          console.error('Error response:', error.response);
          setSnackbarMessage('Error adding patient: ' + error.response.data.error);
        } else {
          setSnackbarMessage('Error adding patient');
        }
        setSnackbarSeverity('error');
        setSnackbarOpen(true);
      });
  };

  const handleEditPatient = (patient) => {
    setIsEditing(true);
    setCurrentPatientId(patient._id);
    setNewPatient({
      name: patient.name,
      injury: patient.injury,
      exercises: patient.exercises.map(ex => ex.name), // Ensure exercises are mapped correctly
      type: patient.type // Add type field
    });
    const selectedInjury = injuries.find(injury => injury.name === patient.injury);
    if (selectedInjury) {
      setFilteredExercises(selectedInjury.exercises);
    } else {
      setFilteredExercises([]);
    }
    setOpen(true);
    setSelectedFormElement('injury'); // Set initial form element to 'injury'
  };

  const handleUpdatePatient = () => {
    if (!newPatient.name || !newPatient.injury || !newPatient.exercises.length) {
        setSnackbarMessage('Please fill in all fields and select at least one exercise.');
        setSnackbarSeverity('error');
        setSnackbarOpen(true);
        return;
    }

    const selectedInjury = injuries.find(injury => injury.name === newPatient.injury);
    if (!selectedInjury) {
      console.error(`Injury not found: ${newPatient.injury}`);
      return;
    }

    const patientData = {
      ...newPatient,
      exercises: newPatient.exercises.map(exerciseName => {
        const exercise = selectedInjury.exercises.find(ex => ex.name === exerciseName);
        if (!exercise) {
          console.error(`Exercise not found: ${exerciseName}`);
          return null;
        }
        return {
          name: exercise.name,
          sets: exercise.default_sets,
          reps: exercise.default_reps
        };
      }).filter(exercise => exercise !== null)
    };

    // console.log("Patient data to update:", patientData);  // Add this line to log the patient data to be updated

    axios.put(`http://localhost:5000/api/patients/${currentPatientId}`, patientData)
    .then(response => {
        const updatedPatients = patients.map(patient =>
          patient._id === currentPatientId ? response.data : patient
        );
        setPatients(updatedPatients);
        setFilteredPatients(updatedPatients); // Update filtered patients
        setSnackbarMessage('Patient updated successfully');
        setSnackbarSeverity('success');
        setSnackbarOpen(true);
        setOpen(false); // Close the modal after successful operation
        setIsEditing(false);
        setCurrentPatientId(null);
        setNewPatient({ name: '', injury: '', exercises: [], type: '' }); // Reset form
    })
    .catch(error => {
        console.error('Error updating patient:', error);
        if (error.response) {
          console.error('Error response:', error.response);
          setSnackbarMessage('Error updating patient: ' + error.response.data.error);
        } else {
          setSnackbarMessage('Error updating patient');
        }
        setSnackbarSeverity('error');
        setSnackbarOpen(true);
    });
  };

  const handleDeletePatient = (patientId) => {
    axios.delete(`http://localhost:5000/api/patients/${patientId}`)
      .then(response => {
        setPatients(patients.filter(patient => patient._id !== patientId));
        setFilteredPatients(filteredPatients.filter(patient => patient._id !== patientId)); // Update filtered patients
        setSnackbarMessage('Patient deleted successfully');
        setSnackbarSeverity('success');
        setSnackbarOpen(true);
      })
      .catch(error => {
        console.error('Error deleting patient:', error);
        if (error.response) {
          console.error('Error response:', error.response);
          setSnackbarMessage('Error deleting patient: ' + error.response.data.error);
        } else {
          setSnackbarMessage('Error deleting patient');
        }
        setSnackbarSeverity('error');
        setSnackbarOpen(true);
      });
  };

  const handleOpenDeleteDialog = (patient) => {
    setPatientToDelete(patient);
    setDeleteDialogOpen(true);
  };

  const handleCloseDeleteDialog = () => {
    setDeleteDialogOpen(false);
    setPatientToDelete(null);
  };

  const handleConfirmDelete = () => {
    if (patientToDelete) {
      handleDeletePatient(patientToDelete._id);
      handleCloseDeleteDialog();
    }
  };

  const handleMenuOpen = (patient) => {
    setSelectedPatient(patient);
    setMenuOpen(true);
    setSelectedMenuButton(0); // Reset menu button selection
  };

  const handleMenuClose = () => {
    setMenuOpen(false);
    setSelectedPatient(null);
  };

  return (
    <Container maxWidth="lg" sx={{ paddingTop: '64px', paddingBottom: '20px' }}>
      <AppBar position="fixed" sx={{ background: '#5c67f2', width: '100%', left: 0, top: 0 }}> {/* Ensure AppBar takes full width */}
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Doctor Dashboard
          </Typography>
          <StyledButton
            id="home-button"
            variant="contained"
            color={selectedElement === 'home' ? 'primary' : 'secondary'}
            startIcon={<HomeIcon />}
            onClick={() => navigate('/')}
            sx={{ borderRadius: 20 }}
            className={selectedElement === 'home' ? 'Mui-hovered' : ''} // Add strong hover color
          >
            Home
          </StyledButton>
        </Toolbar>
      </AppBar>
      <Grid container spacing={2} alignItems="center" sx={{ mt: 2 }}>
        <Grid item xs={12} sm={9}>
          <Autocomplete
            freeSolo
            options={patients.map(patient => patient.name)}
            onInputChange={handleSearchChange}
            onChange={handleSearchSelect} // Add this line
            renderInput={(params) => (
              <TextField {...params} label="Search Patient" variant="outlined" fullWidth />
            )}
          />
        </Grid>
        <Grid item xs={12} sm={3}>
          <StyledButton
            id="add-patient-button"
            variant="contained"
            color={selectedElement === 'addPatient' ? 'primary' : 'default'}
            startIcon={<AddIcon />}
            onClick={handleClickOpen}
            fullWidth
            className={selectedElement === 'addPatient' ? 'Mui-hovered' : ''} // Add strong hover color
          >
            Add Patient
          </StyledButton>
        </Grid>
      </Grid>
      <Box sx={{ overflowX: 'auto', mt: 2 }} id="patients-table">
        <TableContainer component={Paper} sx={{ maxHeight: '70vh' }}> {/* Increase table height */}
          <Table stickyHeader> {/* Add stickyHeader for better UX */}
            <TableHead>
              <TableRow>
                <TableCell>Patient Name</TableCell>
                <TableCell>Injury</TableCell>
                <TableCell>Exercises</TableCell>
                <TableCell>TUIO ID</TableCell> {/* Add TUIO ID header */}
                <TableCell>Type</TableCell> {/* Add Type header */}
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredPatients.map((patient, index) => (
                <StyledTableRow
                  key={patient._id}
                  selected={index === selectedRow}
                  className={index === hoveredRow || index === selectedRow ? 'Mui-hovered' : ''} // Add hover and selected class
                  onMouseEnter={() => setHoveredRow(index)}
                  onMouseLeave={() => setHoveredRow(null)}
                >
                  <TableCell>{patient.name}</TableCell>
                  <TableCell>{patient.injury}</TableCell>
                  <TableCell>{patient.exercises.map(ex => ex.name).join(', ')}</TableCell>
                  <TableCell>{patient.tuio_id}</TableCell> {/* Add TUIO ID cell */}
                  <TableCell>{patient.type}</TableCell> {/* Add Type cell */}
                  <TableCell>
                    <IconButton color="primary" onClick={() => handleMenuOpen(patient)}>
                      <MoreVertIcon />
                    </IconButton>
                  </TableCell>
                </StyledTableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
      <CircularMenu
        open={menuOpen}
        handleClose={handleMenuClose}
        handleEditPatient={() => handleEditPatient(selectedPatient)}
        handleDeletePatient={() => handleDeletePatient(selectedPatient._id)} // Directly delete the patient
        selectedMenuButton={selectedMenuButton} // Pass selectedMenuButton prop
        setSelectedMenuButton={setSelectedMenuButton} // Pass setSelectedMenuButton prop
      />
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>{isEditing ? 'Edit Patient' : 'Add New Patient'}</DialogTitle>
        <DialogContent>
          <DialogContentText>
            {isEditing ? 'Edit the details of the patient.' : 'Fill in the details of the new patient.'}
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            label="Name"
            name="name"
            fullWidth
            value={newPatient.name}
            onChange={handleChange}
            disabled // Disable the field to prevent editing
          />
          <TextField
            margin="dense"
            label="TUIO ID"
            name="tuio_id"
            fullWidth
            value={newPatient.tuio_id}
            onChange={handleChange}
          />
          <TextField
            select
            margin="dense"
            label="Injury"
            name="injury"
            fullWidth
            value={newPatient.injury}
            onChange={handleChange}
            sx={{ border: selectedFormElement === 'injury' ? `2px solid ${brighterBorderColor}` : 'inherit' }} // Highlight border if selected
          >
            {injuries.map((injury) => (
              <MenuItem key={injury._id} value={injury.name}>
                {injury.name}
              </MenuItem>
            ))}
          </TextField>
          <FormControl fullWidth margin="dense" sx={{ border: selectedFormElement === 'exercises' ? `2px solid ${brighterBorderColor}` : 'inherit' }}> {/* Highlight border if selected */}
            <InputLabel>Exercises</InputLabel>
            <Select
              multiple
              value={newPatient.exercises}
              onChange={handleExerciseChange}
              renderValue={(selected) => selected.join(', ')}
            >
              {filteredExercises.map((exercise, index) => (
                <MenuItem key={index} value={exercise.name}>
                  {exercise.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            select
            margin="dense"
            label="Patient Type"
            name="type"
            fullWidth
            value={newPatient.type}
            onChange={handleChange}
          >
            <MenuItem value="kid">Kid</MenuItem>
            <MenuItem value="elderly">Elderly</MenuItem>
            <MenuItem value="athlete">Athlete</MenuItem>
          </TextField>
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            style={{ marginTop: '16px' }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="primary" sx={{ border: selectedFormElement === 'cancel' ? `2px solid ${hoverBorderColor}` : 'inherit' }}> {/* Highlight border if selected */}
            Cancel
          </Button>
          <Button onClick={isEditing ? handleUpdatePatient : handleAddPatient} color="primary" sx={{ border: selectedFormElement === 'add' ? `2px solid ${hoverBorderColor}` : 'inherit' }}> {/* Highlight border if selected */}
            {isEditing ? 'Update' : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>
      <Snackbar open={snackbarOpen} autoHideDuration={6000} onClose={handleSnackbarClose}>
        <MuiAlert onClose={handleSnackbarClose} severity={snackbarSeverity} sx={{ width: '100%' }}>
          {snackbarMessage}
        </MuiAlert>
      </Snackbar>
    </Container>
  );
};

export default DoctorDashboard;
