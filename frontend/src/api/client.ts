import axios, { AxiosError } from "axios";

export const api = axios.create({
  baseURL: "/api/v1",
  headers: { "Content-Type": "application/json" },
});

function getAccessToken() {
  return localStorage.getItem("finsight_access_token");
}
function getRefreshToken() {
  return localStorage.getItem("finsight_refresh_token");
}
export function setTokens(access: string, refresh: string) {
  localStorage.setItem("finsight_access_token", access);
  localStorage.setItem("finsight_refresh_token", refresh);
}
export function clearTokens() {
  localStorage.removeItem("finsight_access_token");
  localStorage.removeItem("finsight_refresh_token");
}

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

let isRefreshing = false;
let refreshQueue: Array<() => void> = [];

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as (typeof error.config & { _retry?: boolean }) | undefined;

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      const refreshToken = getRefreshToken();
      if (!refreshToken || originalRequest.url?.includes("/auth/")) {
        clearTokens();
        window.location.href = "/login";
        return Promise.reject(error);
      }

      originalRequest._retry = true;

      if (isRefreshing) {
        return new Promise((resolve) => {
          refreshQueue.push(() => resolve(api(originalRequest)));
        });
      }

      isRefreshing = true;
      try {
        const { data } = await axios.post("/api/v1/auth/refresh", { refresh_token: refreshToken });
        setTokens(data.access_token, refreshToken);
        refreshQueue.forEach((cb) => cb());
        refreshQueue = [];
        return api(originalRequest);
      } catch (refreshError) {
        clearTokens();
        window.location.href = "/login";
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);
