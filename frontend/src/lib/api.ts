import axios from "axios";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15_000,
  headers: { Accept: "application/json", "Content-Type": "application/json" },
});

export function assertEndpoint(endpoint: string | null, operation: string): string {
  if (!endpoint) throw new Error(`${operation} is not connected to a backend endpoint yet.`);
  return endpoint;
}
