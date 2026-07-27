import type { Role } from "./Role";

export interface User {
  id: number;
  name: string;
  email: string;
  created_at: string;
  updated_at: string;
  roles: Role[];
}

export interface UserBase {
  name: string;
  email: string;
}

export interface UserRegister extends UserBase {
  password: string;
  password_confirmation: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface UserUpdate {
  name?: string | null;
  email?: string | null;
  password?: string | null;
}

export interface UserOut extends UserBase {
  id: number;
  roles: string[];
  created_at?: string | null;
  updated_at?: string | null;
}

export interface UserResponse {
  id: number;
  name: string;
  email: string;
  roles: string[];
  created_at: string;
  updated_at: string;
}