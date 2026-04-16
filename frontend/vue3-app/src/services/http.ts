const trimSlash = (value: string) => value.replace(/\/$/, '');

const DEFAULT_TIMEOUT_MS = Number(import.meta.env.VITE_API_TIMEOUT_MS || 30000);

const defaultApiBaseUrl = () => {
  if (typeof window === 'undefined') {
    return '/api';
  }
  return `${window.location.protocol}//${window.location.hostname}:8000/api`;
};

const API_BASE_URL = trimSlash(import.meta.env.VITE_API_BASE_URL || defaultApiBaseUrl());

export interface RequestOptions extends RequestInit {
  timeoutMs?: number;
}

const parseErrorMessage = async (response: Response): Promise<string> => {
  try {
    const payload = await response.json();
    if (typeof payload?.detail === 'string' && payload.detail.trim()) {
      return payload.detail;
    }
    if (typeof payload?.message === 'string' && payload.message.trim()) {
      return payload.message;
    }
  } catch {
    // Ignore JSON parse errors and fall through to the status message.
  }
  return `HTTP ${response.status}`;
};

const isAbortError = (error: unknown): boolean => {
  if (error instanceof DOMException && error.name === 'AbortError') {
    return true;
  }
  if (error instanceof Error && error.name === 'AbortError') {
    return true;
  }
  return false;
};

export async function requestJson<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { timeoutMs = DEFAULT_TIMEOUT_MS, headers, ...rest } = options;
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...rest,
      headers: {
        'Content-Type': 'application/json',
        ...(headers || {}),
      },
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error(await parseErrorMessage(response));
    }

    const text = await response.text();
    if (!text) {
      return {} as T;
    }

    return JSON.parse(text) as T;
  } catch (error) {
    if (isAbortError(error)) {
      throw new Error(`请求超时（${Math.ceil(timeoutMs / 1000)}秒），请稍后重试`);
    }
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('网络请求失败，请稍后重试');
  } finally {
    window.clearTimeout(timer);
  }
}
