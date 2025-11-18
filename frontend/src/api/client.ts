// Use relative URLs in production (nginx will proxy), or absolute URL in development
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000');

export interface ChatRequest {
  message: string;
  history: Array<{ role: string; content: string }>;
  employee_id: string | null;
  employee_name: string | null;
}

export interface ChatResponse {
  message: string;
  employee_id: string | null;
  employee_name: string | null;
}

class ApiClient {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async sendMessage(
    message: string,
    history: Array<{ role: string; content: string }>,
    employeeId: string | null,
    employeeName: string | null
  ): Promise<ChatResponse> {
    return this.request<ChatResponse>('/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        history,
        employee_id: employeeId,
        employee_name: employeeName,
      }),
    });
  }
}

export const apiClient = new ApiClient();

