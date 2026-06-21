import type { UserOut } from "../types/user_service/User";

export function getCurrentUser(): UserOut | null {
  const user = localStorage.getItem("user");

  if (!user) return null;

  return JSON.parse(user);
}

export function getToken(): string | null {
  return localStorage.getItem("token");
}

export function isGuest(): boolean {
  return localStorage.getItem("guest") === "true" && !getToken();
}

export function isAuthenticated(): boolean {
  return !!getToken() && !!getCurrentUser();
}

export function isAdmin(): boolean {
  const user = getCurrentUser();
  return user?.roles?.includes("admin") ?? false;
}

export function isUser(): boolean {
  const user = getCurrentUser();
  return user?.roles?.includes("user") ?? false;
}