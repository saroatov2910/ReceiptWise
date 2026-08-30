import React, { useState, useRef } from "react";
import api from "../api/client";

export default function UploadReceipt({ onUploaded }) {
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  const handleFile = async (file) => {
    if (!file) return;
    const allowed = ["image/jpeg", "image/png", "image/webp", "image/tiff"];
    if (!allowed.includes(file.type)) {
      setError("קובץ לא נתמך. יש להעלות תמונה (JPEG, PNG, WEBP, TIFF).");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      await api.post("/receipts/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      onUploaded && onUploaded();
    } catch (err) {
      setError(err.response?.data?.detail || "שגיאה בהעלאה");
    } finally {
      setLoading(false);
    }
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    handleFile(file);
  };

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={onDrop}
      onClick={() => inputRef.current?.click()}
      style={{
        border: `2px dashed ${dragging ? "#6366f1" : "#d1d5db"}`,
        borderRadius: "12px",
        padding: "32px",
        textAlign: "center",
        cursor: "pointer",
        background: dragging ? "#eef2ff" : "#f9fafb",
        transition: "all 0.2s",
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp,image/tiff"
        style={{ display: "none" }}
        onChange={(e) => handleFile(e.target.files[0])}
      />
      {loading ? (
        <p style={{ color: "#6366f1" }}>מעלה ומעבד...</p>
      ) : (
        <>
          <p style={{ fontWeight: 600, marginBottom: 4 }}>גרור קבלה לכאן</p>
          <p style={{ fontSize: 13, color: "#6b7280" }}>או לחץ לבחירת קובץ</p>
        </>
      )}
      {error && <p style={{ color: "#ef4444", marginTop: 8 }}>{error}</p>}
    </div>
  );
}
