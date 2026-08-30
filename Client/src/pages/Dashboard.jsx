import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import api from "../api/client";
import UploadReceipt from "../components/UploadReceipt";

const CATEGORY_LABELS = {
  food: "🍔 מזון", transport: "🚗 תחבורה", office: "💼 משרד",
  utilities: "💡 חשמל/מים", entertainment: "🎬 בידור", health: "💊 בריאות", other: "📦 אחר",
};

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [receipts, setReceipts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [month, setMonth] = useState(new Date().toISOString().slice(0, 7));

  useEffect(() => {
    if (!user) { navigate("/login"); return; }
    fetchReceipts();
  }, [user]);

  async function fetchReceipts() {
    try {
      const res = await api.get("/receipts/");
      setReceipts(res.data);
    } finally {
      setLoading(false);
    }
  }

  async function downloadReport() {
    const res = await api.get(`/reports/monthly?month=${month}`, { responseType: "blob" });
    const url = URL.createObjectURL(res.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = `report_${month}.pdf`;
    a.click();
  }

  async function deleteReceipt(id) {
    await api.delete(`/receipts/${id}`);
    setReceipts((prev) => prev.filter((r) => r.id !== id));
  }

  const total = receipts.reduce((s, r) => s + (r.amount || 0), 0);

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <h1 style={styles.logo}>ReceiptWise</h1>
        <div style={styles.headerRight}>
          <span style={styles.userEmail}>{user?.email}</span>
          <button style={styles.logoutBtn} onClick={() => { logout(); navigate("/login"); }}>יציאה</button>
        </div>
      </header>

      <main style={styles.main}>
        {/* סטטיסטיקות */}
        <div style={styles.statsRow}>
          <div style={styles.statCard}><p style={styles.statNum}>{receipts.length}</p><p style={styles.statLabel}>קבלות</p></div>
          <div style={styles.statCard}><p style={styles.statNum}>₪{total.toFixed(2)}</p><p style={styles.statLabel}>סה"כ הוצאות</p></div>
        </div>

        {/* העלאה + דוח */}
        <div style={styles.actionsRow}>
          <UploadReceipt onUploaded={fetchReceipts} />
          <div style={styles.reportBox}>
            <input type="month" value={month} onChange={(e) => setMonth(e.target.value)} style={styles.monthInput} />
            <button style={styles.reportBtn} onClick={downloadReport}>📄 הורד דוח PDF</button>
          </div>
        </div>

        {/* טבלת קבלות */}
        <div style={styles.tableWrap}>
          <h2 style={styles.tableTitle}>הקבלות שלי</h2>
          {loading ? <p>טוען...</p> : receipts.length === 0 ? (
            <p style={styles.empty}>אין קבלות עדיין — העלה את הראשונה!</p>
          ) : (
            <table style={styles.table}>
              <thead>
                <tr style={styles.thead}>
                  <th>תאריך</th><th>ספק</th><th>קטגוריה</th><th>סכום</th><th></th>
                </tr>
              </thead>
              <tbody>
                {receipts.map((r) => (
                  <tr key={r.id} style={styles.row}>
                    <td>{r.date || "—"}</td>
                    <td>{r.vendor || "לא ידוע"}</td>
                    <td>{CATEGORY_LABELS[r.category] || r.category}</td>
                    <td>{r.amount ? `₪${r.amount.toFixed(2)}` : "—"}</td>
                    <td><button style={styles.deleteBtn} onClick={() => deleteReceipt(r.id)}>🗑</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </main>
    </div>
  );
}

const styles = {
  page: { minHeight: "100vh", background: "#f8fafc", fontFamily: "system-ui, sans-serif", direction: "rtl" },
  header: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "1rem 2rem", background: "#fff", boxShadow: "0 1px 4px rgba(0,0,0,0.06)" },
  logo: { fontSize: "1.5rem", fontWeight: 700, color: "#6366f1", margin: 0 },
  headerRight: { display: "flex", alignItems: "center", gap: "1rem" },
  userEmail: { color: "#64748b", fontSize: "0.9rem" },
  logoutBtn: { padding: "0.4rem 1rem", background: "#fee2e2", color: "#ef4444", border: "none", borderRadius: "0.5rem", cursor: "pointer", fontWeight: 600 },
  main: { maxWidth: 900, margin: "2rem auto", padding: "0 1rem" },
  statsRow: { display: "flex", gap: "1rem", marginBottom: "1.5rem" },
  statCard: { flex: 1, background: "#fff", padding: "1.5rem", borderRadius: "1rem", boxShadow: "0 2px 8px rgba(0,0,0,0.05)", textAlign: "center" },
  statNum: { fontSize: "2rem", fontWeight: 700, color: "#6366f1", margin: 0 },
  statLabel: { color: "#64748b", marginTop: 4 },
  actionsRow: { display: "flex", gap: "1rem", marginBottom: "1.5rem", flexWrap: "wrap" },
  reportBox: { display: "flex", gap: "0.5rem", alignItems: "center" },
  monthInput: { padding: "0.6rem", borderRadius: "0.5rem", border: "1px solid #e2e8f0" },
  reportBtn: { padding: "0.6rem 1.2rem", background: "#6366f1", color: "#fff", border: "none", borderRadius: "0.5rem", cursor: "pointer", fontWeight: 600 },
  tableWrap: { background: "#fff", borderRadius: "1rem", boxShadow: "0 2px 8px rgba(0,0,0,0.05)", padding: "1.5rem" },
  tableTitle: { fontSize: "1.1rem", fontWeight: 700, color: "#1e293b", marginBottom: "1rem" },
  table: { width: "100%", borderCollapse: "collapse" },
  thead: { background: "#f1f5f9" },
  row: { borderBottom: "1px solid #f1f5f9" },
  deleteBtn: { background: "none", border: "none", cursor: "pointer", fontSize: "1rem" },
  empty: { color: "#94a3b8", textAlign: "center", padding: "2rem" },
};
