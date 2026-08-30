import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate, Link } from "react-router-dom";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch {
      setError("אימייל או סיסמה שגויים");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h1 style={styles.title}>ReceiptWise</h1>
        <p style={styles.sub}>ניהול הוצאות חכם</p>
        <form onSubmit={handleSubmit} style={styles.form}>
          <input
            style={styles.input}
            type="email"
            placeholder="אימייל"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            style={styles.input}
            type="password"
            placeholder="סיסמה"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          {error && <p style={styles.error}>{error}</p>}
          <button style={styles.btn} type="submit" disabled={loading}>
            {loading ? "...מתחבר" : "התחברות"}
          </button>
        </form>
        <p style={styles.link}>
          אין חשבון?{" "}
          <Link to="/register" style={{ color: "#6366f1" }}>
            הירשם כאן
          </Link>
        </p>
      </div>
    </div>
  );
}

const styles = {
  page: { minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#f1f5f9" },
  card: { background: "#fff", padding: "2.5rem", borderRadius: "1rem", boxShadow: "0 4px 24px rgba(0,0,0,0.08)", width: "100%", maxWidth: 400, textAlign: "center" },
  title: { fontSize: "2rem", fontWeight: 700, color: "#1e293b", marginBottom: 4 },
  sub: { color: "#64748b", marginBottom: "1.5rem" },
  form: { display: "flex", flexDirection: "column", gap: "0.8rem" },
  input: { padding: "0.75rem 1rem", borderRadius: "0.5rem", border: "1px solid #e2e8f0", fontSize: "1rem", outline: "none", direction: "rtl" },
  btn: { padding: "0.8rem", background: "#6366f1", color: "#fff", border: "none", borderRadius: "0.5rem", fontSize: "1rem", fontWeight: 600, cursor: "pointer", marginTop: "0.5rem" },
  error: { color: "#ef4444", fontSize: "0.875rem" },
  link: { marginTop: "1rem", color: "#64748b", fontSize: "0.9rem" },
};
