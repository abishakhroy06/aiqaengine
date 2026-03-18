export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  oauth_provider: string | null;
  avatar_url: string | null;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}
