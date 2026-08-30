import { useState, useRef } from "react";
import api from "../api/client";

export default function UploadReceipt({ onUploaded }) {
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const inputRef = useRef();

  async function uploadFile(file) {
    if (!file) return;
    setLoading(true);
    setMessage("");
    const form = new FormData();
    form.append("file", file);
    try {
      await api.post("/receipts/upload", form, { headers: { "Content-Type": "multipart/form-data" } });
      setMessage("✅ הקבלה הועלתה ועובדה בהצלחה!");
      onUploaded();
    } catch (e) {
      setMessage("❌ שגיאה בהעלאה — " + (e.response?.data?.detail || "נסה שוב"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{ ...styles.zone, ...(dragging ? styles.dragging : {}) }}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => { e.preventDefault(); setDragging(false); uploadFile(e.dataTransfer.files[0]); }}
      onClick={() => inputRef.current.click()}
    >
      <input ref={inputRef} type="file" accept="image/*" style={{ display: "none" }} onChange={(e) => uploadFile(e.target.files[0])} />
      {loading ? (
        <p style={styles.text}>⏳ מעבד קבלה עם OCR + AI...</p>
      ) : (
        <>
          <p style={styles.icon}>📤</p>
          <p style={styles.text}>גרור קבלה לכאן או לחץ להעלאה</p>
          <p style={styles.sub}>JPG / PNG / WEBP</p>
        </>
      )}
      {message && <p style={styles.msg}>{message}</p>}
    </div>
  );
}

const styles = {
  zone: { flex: 1, minWidth: 220, border: "2px dashed #c7d2fe", borderRadius: "1rem", padding: "1.5rem", textAlign: "center", cursor: "pointer", background: "#f8f9ff", transition: "all 0.2s" },
  dragging: { borderColor: "#6366f1", background: "#eef2ff" },
  icon: { fontSize: "2rem", margin: 0 },
  text: { fontWeight: 600, color: "#4f46e5", margin: "0.25rem 0" },
  sub: { color: "#94a3b8", fontSize: "0.8rem" },
  msg: { marginTop: "0.5rem", fontSize: "0.875rem" },
};
