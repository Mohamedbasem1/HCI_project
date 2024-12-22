import React, { useEffect } from 'react';
import io from 'socket.io-client';

const socket = io('http://localhost:5000');

function GestureControl({ onNextExercise, onPreviousExercise, onPerformExercise, onNavigateHome }) {
    useEffect(() => {
        // Start gesture recognition automatically when component mounts
        startGestureRecognition();

        // Set up socket listener
        socket.on('gesture_event', handleGesture);

        // Cleanup on unmount
        return () => {
            stopGestureRecognition();
            socket.off('gesture_event', handleGesture);
        };
    }, []);

    const startGestureRecognition = async () => {
        try {
            const response = await fetch('/api/gesture/start', { method: 'POST' });
            const data = await response.json();
            if (data.status !== 'success') {
                console.error('Failed to start gesture recognition');
            }
        } catch (error) {
            console.error('Error starting gesture recognition:', error);
        }
    };

    const stopGestureRecognition = async () => {
        try {
            await fetch('/api/gesture/stop', { method: 'POST' });
        } catch (error) {
            console.error('Error stopping gesture recognition:', error);
        }
    };

    const handleGesture = (data) => {
        const timestamp = new Date().toISOString();
        console.log(`[${timestamp}] Gesture detected:`, data.gesture); // Log gesture with timestamp

        switch(data.gesture) {
            case 'thumbs_up':
                console.log('Gesture: thumbs_up detected, moving to next exercise');
                onNextExercise?.();
                break;
            case 'thumbs_down':
                console.log('Gesture: thumbs_down detected, moving to previous exercise');
                onPreviousExercise?.();
                break;
            case 'swipe_right':
                console.log('Gesture: swipe_right detected, performing exercise');
                onPerformExercise?.();
                break;
            case 'swipe_left':
                console.log('Gesture: swipe_left detected, navigating to home');
                onNavigateHome?.();
                break;
            default:
                console.log('Unknown gesture detected:', data.gesture);
                break;
        }
    };

    // No need to render any UI
    return null;
}

export default GestureControl;
