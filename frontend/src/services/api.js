import axios from "axios";

const api = axios.create({
  baseURL: "/api", // Proxy to Spring Boot via Vite
  timeout: 10000,
});

// Races
export const getRacesByDate = (date) => api.get("/races", { params: { date } });

export const getRaceCard = (raceId, predictions = true) =>
  api.get(`/races/${raceId}/card`, { params: { predictions } });

export const getCompletedRaces = (date) =>
  api.get("/races/completed", { params: { date } });

// Meets
export const getMeetsByDate = (date) => api.get("/meets", { params: { date } });

// Tracks
export const getAllTracks = () => api.get("/tracks");

// Results
export const getResultsForRace = (raceId) => api.get(`/results/race/${raceId}`);

// Predictions
export const getPredictionsForRace = (raceId) =>
  api.get(`/predictions/race/${raceId}`);

export const getMlHealth = () => api.get("/predictions/health");

// Chat
export const sendChatMessage = (
  message,
  conversationHistory = [],
  raceId = null,
) =>
  api.post("/chat", {
    message,
    conversation_history: conversationHistory,
    ...(raceId && { race_id: raceId }),
  });

export const getChatHealth = () => api.get("/chat/health");

export default api;
