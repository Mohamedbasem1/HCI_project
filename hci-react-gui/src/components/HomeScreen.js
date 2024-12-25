import React, { useState, useEffect } from "react";
import {
  Container,
  Typography,
  AppBar,
  Toolbar,
  Button,
  Box,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Paper,
} from "@mui/material";
import { Link, useNavigate } from "react-router-dom";
import { io } from "socket.io-client";

const HomeScreen = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const loggedInUser = JSON.parse(localStorage.getItem("user"));
    if (loggedInUser) {
      setIsLoggedIn(true);
      setUser(loggedInUser);
    }

    const socket = io("http://localhost:5000");

    socket.on("login_event", (data) => {
      if (data.patient) {
        const { patient } = data;
        localStorage.setItem("user", JSON.stringify(patient));
        navigate("/patient-exercise-dashboard", { state: { patient } });
      } else if (data.doctor) {
        const { doctor } = data;
        localStorage.setItem("user", JSON.stringify(doctor));
        navigate("/doctor-dashboard", { state: { doctor } });
      }
    });

    socket.on("redirect_event", (data) => {
      const { url } = data;
      window.location.href = url;
    });

    return () => {
      socket.disconnect();
    };
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("user");
    setIsLoggedIn(false);
    setUser(null);
    navigate("/");
  };

  return (
    <Box>
      {/* AppBar */}
      <AppBar position="static" sx={{ background: "#5c67f2" }}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: "bold" }}>
            Recovery Hub
          </Typography>
          {isLoggedIn ? (
            <>
              <Button
                color="inherit"
                component={Link}
                to="/patient-exercise-dashboard"
                sx={{ borderRadius: 20 }}
              >
                My Exercises
              </Button>
              <Button
                color="inherit"
                onClick={handleLogout}
                sx={{ borderRadius: 20 }}
              >
                Logout
              </Button>
            </>
          ) : (
            <>
              <Button
                color="inherit"
                component={Link}
                to="/doctor"
                sx={{ borderRadius: 20 }}
              >
                Dashboard
              </Button>
              <Button
                color="inherit"
                component={Link}
                to="/login"
                sx={{ borderRadius: 20 }}
              >
                Login
              </Button>
            </>
          )}
        </Toolbar>
      </AppBar>

      {/* Hero Section */}
      <Grid container sx={{ height: "70vh", backgroundColor: "#f5f5f5" }}>
        {/* Left Side */}
        <Grid
          item
          xs={12}
          md={6}
          sx={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            p: 5,
          }}
        >
          <Typography
            variant="h2"
            sx={{ fontWeight: "bold", color: "#1976d2" }}
          >
            Welcome to Recovery Hub
          </Typography>
          <Typography variant="body1" sx={{ mt: 2, color: "#555" }}>
            A complete digital solution for your rehabilitation and recovery
            journey. Track your exercises, monitor your progress, and stay
            connected with your healthcare provider in one seamless platform.
          </Typography>
          <Button
            variant="contained"
            color="primary"
            sx={{ mt: 3, width: "fit-content", borderRadius: 20 }}
            component={Link}
            to="/login"
          >
            Get Started
          </Button>
        </Grid>

        {/* Right Side */}
        <Grid
          item
          xs={12}
          md={6}
          sx={{
            position: "relative",
            overflow: "hidden",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            p: 5,
          }}
        >
          <Box
            sx={{
              display: "flex",
              justifyContent: "flex-start", // Change this to adjust horizontal alignment
              alignItems: "flex-start",
              maxWidth: "80%", // Change this to adjust vertical alignment
            }}
          >
            <img
              src="\logoa.png"
              alt="Recovery Hub Illustration"
              style={{ maxWidth: "100%", height: "auto", borderRadius: "10px" }}
            />
          </Box>
        </Grid>
      </Grid>

      {/* Feature Section */}
      <Container sx={{ py: 6 }}>
        <Typography
          variant="h4"
          align="center"
          sx={{ fontWeight: "bold", mb: 4 }}
        >
          What We Offer
        </Typography>
        <Grid container spacing={4}>
          {/* Card 1 */}
          <Grid item xs={12} sm={4}>
            <Card sx={{ textAlign: "center", p: 3 }}>
              <CardMedia
                component="img"
                src="/image3.png"
                alt="Track Progress"
                sx={{
                  width: "100%",
                  height: "auto",
                  maxWidth: 200,
                  margin: "auto",
                  mb: 2,
                  objectFit: "contain",
                }}
              />
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: "bold" }}>
                  Track Progress
                </Typography>
                <Typography variant="body2" sx={{ mt: 1, color: "#555" }}>
                  Monitor your recovery with easy-to-use tracking tools and
                  detailed insights.
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Card 2 */}
          <Grid item xs={12} sm={4}>
            <Card sx={{ textAlign: "center", p: 3 }}>
              <CardMedia
                component="img"
                src="/image1.png"
                alt="Personalized Plans"
                sx={{
                  width: "100%",
                  height: "auto",
                  maxWidth: 200,
                  margin: "auto",
                  mb: 2,
                  objectFit: "contain",
                }}
              />
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: "bold" }}>
                  Personalized Plans
                </Typography>
                <Typography variant="body2" sx={{ mt: 1, color: "#555" }}>
                  Work with your healthcare provider to create plans tailored to
                  your needs.
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Card 3 */}
          <Grid item xs={12} sm={4}>
            <Card sx={{ textAlign: "center", p: 3 }}>
              <CardMedia
                component="img"
                src="/image 2.png"
                alt="Stay Connected"
                sx={{
                  width: "100%",
                  height: "auto",
                  maxWidth: 200,
                  margin: "auto",
                  mb: 2,
                  objectFit: "contain",
                }}
              />
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: "bold" }}>
                  Stay Connected
                </Typography>
                <Typography variant="body2" sx={{ mt: 1, color: "#555" }}>
                  Get real-time updates and support from your healthcare
                  provider.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>

      {/* Footer */}
      <Paper
        component="footer"
        sx={{
          mt: 6,
          py: 3,
          textAlign: "center",
          backgroundColor: "#1976d2",
          color: "white",
        }}
      >
        <Typography variant="body2">
          © 2024 Recovery Hub. All rights reserved.
        </Typography>
      </Paper>
    </Box>
  );
};

export default HomeScreen;