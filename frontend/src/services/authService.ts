import type { LoginResponse } from "../types/user_service/Auth";
import type { UserLogin, UserRegister } from "../types/user_service/User";

const API_BASE_URL = "http://localhost:8000";

export async function login(data: UserLogin): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error("Invalid credentials");
  }

  return response.json();
}

export async function register(data: UserRegister): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error("Registration failed");
  }

  return response.json();
}