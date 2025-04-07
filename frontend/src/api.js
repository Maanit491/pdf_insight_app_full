// src/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000',
});

export const uploadPDF = async (selectedFile) => {
  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const response = await api.post('/uploadfile/', formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error uploading PDF:", error);
    throw error;
  }
};

export default api;
