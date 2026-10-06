export type ApiResponse<T> = { data: T; message?: string };
export type ApiListResponse<T> = { data: T[]; total: number };
export type ApiErrorResponse = { message: string; code?: string; details?: Record<string, string[]> };
export type ServiceOptions = { source?: "mock" | "api" };
