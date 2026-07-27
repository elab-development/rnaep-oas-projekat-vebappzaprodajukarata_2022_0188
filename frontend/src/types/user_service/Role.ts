export interface Role {
  id: number;
  name: "guest" | "user" | "admin";
  description?: string | null;
  created_at: string;
}