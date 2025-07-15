import React from "react";
import { useForm } from "react-hook-form";
import { useAuth } from "../context/AuthContext";
import { TextField, Button, Typography, Box } from "@mui/material";
import { useNavigate } from "react-router-dom";
import AuthLayout from "../layouts/AuthLayout";

const LoginPage = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const { register, handleSubmit } = useForm();

  const onSubmit = async (data) => {
    try {
      const role = await login({ username: data.email, password: data.password });
      if (role === "admin") navigate("/admin/dashboard");
      else if (role === "teacher") navigate("/teacher/dashboard");
      else if (role === "student") navigate("/student/dashboard");
    } catch (error) {
      alert("Login failed. Please check credentials.");
    }
  };

  return (
    <AuthLayout>
      <form
        onSubmit={handleSubmit(onSubmit)}
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "1.2rem",
          width: "100%",
          padding: "2rem",
          backgroundColor: "#fff",
          borderRadius: "10px",
          boxShadow: "0 4px 20px rgba(0,0,0,0.1)",
        }}
      >
        <Typography variant="h5" align="center" fontWeight="bold">
          Login
        </Typography>

        <TextField label="Email" {...register("email", { required: true })} fullWidth />
        <TextField label="Password" type="password" {...register("password", { required: true })} fullWidth />
        <Button variant="contained" color="primary" type="submit">
          Login
        </Button>
      </form>
    </AuthLayout>
  );
};

export default LoginPage;
