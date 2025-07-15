// src/context/AuthContext.jsx
import React, { createContext, useState, useContext } from "react";
import axiosInstance from "../interceptor";

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  const login = async (credentials) => {
    console.log("Login called with:", credentials);

    try {
      const response = await axiosInstance.post("/token/", credentials);
      console.log("Token response:", response.data);

      const { access, refresh, role } = response.data;

      localStorage.setItem("access_token", access);
      localStorage.setItem("refresh_token", refresh);
      localStorage.setItem("role", role);

      setUser({ access, refresh, role });
      return role; // ✅ Let caller decide what to do
    } catch (error) {
      console.error("Login failed:", error.response?.data || error.message);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("role");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
