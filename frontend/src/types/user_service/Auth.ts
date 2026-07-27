import type { User } from "./User";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type?: string;
  user: User;
}

import type { UserOut } from "./User";

export interface Token {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginResponse {
  user: UserOut;
  token: string;
  token_type: string;
  expires_in: number;
}