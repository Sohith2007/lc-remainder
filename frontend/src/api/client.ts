// API Client Module
// Handles all communication with the LeetCode Daily Reminder backend

import type {
  HomeResponse,
  ProblemResponse,
  RecipientResponse,
  RefreshResponse,
  ErrorResponse,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const defaultHeaders = {
      'Content-Type': 'application/json',
    };

    const response = await fetch(url, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = (await response.json()) as ErrorResponse;
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return response.json();
  }

  async getHome(): Promise<HomeResponse> {
    return this.request<HomeResponse>('/api/home');
  }

  async getProblem(): Promise<ProblemResponse> {
    return this.request<ProblemResponse>('/api/problem');
  }

  async addRecipient(email: string): Promise<RecipientResponse> {
    return this.request<RecipientResponse>('/api/recipients', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  }

  async refresh(): Promise<RefreshResponse> {
    return this.request<RefreshResponse>('/api/refresh', {
      method: 'POST',
    });
  }
}

export const apiClient = new ApiClient();
