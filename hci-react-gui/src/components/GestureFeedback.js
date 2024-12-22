import React, { useState, useEffect } from 'react';
import { Box, Typography, Fade } from '@mui/material';

function GestureFeedback({ gesture }) {
    const [show, setShow] = useState(false);

    useEffect(() => {
        if (gesture) {
            setShow(true);
            const timer = setTimeout(() => setShow(false), 1000); // Hide after 1 second
            return () => clearTimeout(timer); // Cleanup timer
        }
    }, [gesture]);

    const getGestureText = (gesture) => {
        switch(gesture) {
            case 'thumbs_up':
                return 'Next Exercise';
            case 'thumbs_down':
                return 'Previous Exercise';
            case 'swipe_right':
                return 'Perform Exercise';
            case 'swipe_left':
                return 'Return Home';
            default:
                return '';
        }
    };

    const getGestureIcon = (gesture) => {
        switch(gesture) {
            case 'thumbs_up':
                return 'THUMBS UP';
            case 'thumbs_down':
                return 'THUMBS DOWN';
            case 'swipe_right':
                return 'RIGHT';
            case 'swipe_left':
                return 'LEFT';
            default:
                return '';
        }
    };

    if (!gesture) return null;

    return (
        <Fade in={show}>
            <Box
                position="fixed"
                top="50%"
                left="50%"
                sx={{
                    transform: 'translate(-50%, -50%)',
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    color: 'white',
                    padding: 3,
                    borderRadius: 2,
                    zIndex: 9999,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: 1,
                    minWidth: '200px',
                    textAlign: 'center',
                    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    backdropFilter: 'blur(10px)'
                }}
            >
                <Typography 
                    variant="h3" 
                    component="div" 
                    sx={{ 
                        fontWeight: 'bold',
                        letterSpacing: '1px'
                    }}
                >
                    {getGestureIcon(gesture)}
                </Typography>
                <Typography 
                    variant="h6" 
                    component="div"
                    sx={{
                        opacity: 0.9,
                        fontWeight: 500
                    }}
                >
                    {getGestureText(gesture)}
                </Typography>
            </Box>
        </Fade>
    );
}

export default GestureFeedback;
