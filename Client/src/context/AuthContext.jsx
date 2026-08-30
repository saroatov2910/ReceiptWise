import { createContext, useContext, useState } from "react";
import api from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem("user");
    return stored ? JSON.parse(stored) : null;
  });

  async function login(email, password) {
    const res = await api.post("/auth/login", { email, password });
    localStorage.setItem("token", res.data.access_token);
    const me = { email };
    localStorage.setItem("user", JSON.stringify(me));
    setUser(me);
  }

  async function register(email, password, fullName) {
    await api.post("/auth/register", { email, password, full_name: fullName });
    await login(email, password);
  }

  function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
