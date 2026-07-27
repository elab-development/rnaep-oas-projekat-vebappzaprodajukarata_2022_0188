const API = "http://localhost:8000/api";

export interface Payment {
  id: number;
  reservation_id: number;
  user_id: number;
  payment_method_id: number;
  amount: number;
  status: string;
  created_at: string;
  paid_at: string | null;
}

export interface Refund {
  id: number;
  payment_id: number;
  amount: number;
  status: string;
  refunded_at: string | null;
}

export interface Transaction {
  id: number;
  payment_id: number;
  amount: number;
  status: string;
  processed_at: string | null;
}

function authHeaders() {
  return { Authorization: `Bearer ${localStorage.getItem("token")}` };
}

export async function getAllPayments(): Promise<Payment[]> {
  const res = await fetch(`${API}/payments`, { headers: authHeaders() });
  if (!res.ok) throw new Error("Ne mogu da učitam plaćanja.");
  return res.json();
}

export async function getAllRefunds(): Promise<Refund[]> {
  const res = await fetch(`${API}/refunds`, { headers: authHeaders() });
  if (!res.ok) throw new Error("Ne mogu da učitam refundacije.");
  return res.json();
}

export async function getAllTransactions(): Promise<Transaction[]> {
  const res = await fetch(`${API}/transactions`, { headers: authHeaders() });
  if (!res.ok) throw new Error("Ne mogu da učitam transakcije.");
  return res.json();
}