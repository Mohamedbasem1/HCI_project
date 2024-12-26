
import React, { useEffect } from 'react';
import { Popover, IconButton, Box } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete'; // Correct import statement
import CancelIcon from '@mui/icons-material/Cancel';
import { styled, keyframes } from '@mui/material/styles';

// Define keyframes for animations
const fadeIn = keyframes`
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
`;

const hoverAndSelectedColor = '#ff9800'; // Change to a different color (e.g., orange)
const brighterBorderColor = '#ffcc80'; // Adjust the brighter border color accordingly
const menuButtonHoverColor = '#ff5722'; // Change to a different hover color (e.g., deep orange)
const menuButtonHoverBackgroundColor = '#ffe0b2'; // Light background color for better icon visibility

// Circular Menu Styling with transparency and lighter dark borders
const CircularMenuContainer = styled(Box)(() => ({
  width: 300, // Increase width
  height: 300, // Increase height
  borderRadius: '50%',
  backgroundColor: 'rgba(255, 255, 255, 0.8)',  // Transparent white background
  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)', // Softer shadow for elegance
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  position: 'relative',
  overflow: 'hidden',
  padding: 0,  // No padding to avoid any unwanted space
  border: '2px solid rgba(0, 0, 0, 0.5)',  // Lighter dark border for better visibility
  animation: `${fadeIn} 0.3s ease-out`, // Add fade-in animation
}));

// Icon Styling with Hover Effects and Larger Size
const IconButtonStyled = styled(IconButton)(({ theme }) => ({
  position: 'absolute',
  zIndex: 2,
  transition: 'all 0.3s ease',
  borderRadius: '50%', // Make icons circular
  '&:hover': {
    backgroundColor: menuButtonHoverBackgroundColor, // Light background color for better icon visibility
    transform: 'scale(1.2)', // Larger icon on hover for emphasis
    boxShadow: '0 0 10px rgba(0, 0, 0, 0.2)', // Optional: Add shadow on hover
    border: `2px solid ${menuButtonHoverColor}`, // Brighter border for hovered button
  },
}));

// Positioning the icons in a cross layout
const TopIcon = styled(IconButtonStyled)(() => ({
  top: '10%',
  left: '50%',
  transform: 'translateX(-50%)',
}));

const LeftIcon = styled(IconButtonStyled)(({ theme }) => ({
  left: '10%',
  top: '50%',
  transform: 'translateY(-50%)',
}));

const RightIcon = styled(IconButtonStyled)(() => ({
  right: '10%',
  top: '50%',
  transform: 'translateY(-50%)',
}));

const BottomIcon = styled(IconButtonStyled)(() => ({
  bottom: '10%',
  left: '50%',
  transform: 'translateX(-50%)',
}));

// Circular Menu with three segments
const CircularMenu = ({
  open,
  handleClose,
  handleEditPatient,
  handleDeletePatient, 
  selectedMenuButton, // Add selectedMenuButton prop
  setSelectedMenuButton, // Add setSelectedMenuButton prop
}) => {
  useEffect(() => {
    const handleRotateEvent = (event) => {
      const { direction } = event.detail;
      if (direction === 'rotate_left') {
        setSelectedMenuButton((prevButton) => (prevButton - 1 ) % 3);
      } else if (direction === 'rotate_right') {
        setSelectedMenuButton((prevButton) => (prevButton + 1) % 3);
      }
    };

    const handleClickEvent = () => {
      if (selectedMenuButton === 0) {
        handleEditPatient();
      } else if (selectedMenuButton === 1) {
        handleClose();
      } else if (selectedMenuButton === 2) {
        handleDeletePatient(); // Directly delete the patient
      }
    };

    window.addEventListener('rotate_event', handleRotateEvent);
    window.addEventListener('click_event', handleClickEvent);

    return () => {
      window.removeEventListener('rotate_event', handleRotateEvent);
      window.removeEventListener('click_event', handleClickEvent);
    };
  }, [selectedMenuButton, handleEditPatient, handleClose, handleDeletePatient, setSelectedMenuButton]);

  return (
    <Popover
      open={open}
      onClose={handleClose}
      anchorReference="none"
      PaperProps={{
        style: {
          position: 'fixed',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          backgroundColor: 'transparent',
          boxShadow: 'none',
        },
      }}
    >
      <CircularMenuContainer>
        {/* Top Icon */}
        <TopIcon
          color="primary"
          onClick={handleEditPatient}
          sx={{ backgroundColor: selectedMenuButton === 0 ? hoverAndSelectedColor : 'inherit' }} // Highlight if selected
        >
          <EditIcon />
        </TopIcon>

        {/* Left Icon */}
        <LeftIcon
          onClick={handleClose}
          sx={{ backgroundColor: selectedMenuButton === 1 ? hoverAndSelectedColor : 'inherit' }} // Highlight if selected
        >
          <CancelIcon />
        </LeftIcon>

        {/* Right Icon */}
        <RightIcon
          color="secondary"
          onClick={handleDeletePatient} // Directly delete the patient
          sx={{ backgroundColor: selectedMenuButton === 2 ? hoverAndSelectedColor : 'inherit' }} // Highlight if selected
        >
          <DeleteIcon />
        </RightIcon>
      </CircularMenuContainer>
    </Popover>
  );
};

export default CircularMenu;