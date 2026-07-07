export type TransactionType = "income" | "expense";
export type PaymentMethod = "cash" | "card" | "upi" | "net_banking" | "wallet" | "other";
export type BudgetPeriod = "weekly" | "monthly";

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
}

export interface Category {
  id: string;
  name: string;
  type: TransactionType;
  icon: string;
  color: string;
  is_default: boolean;
}

export interface Transaction {
  id: string;
  type: TransactionType;
  amount: number;
  description: string;
  notes: string | null;
  payment_method: PaymentMethod;
  merchant: string | null;
  tags: string | null;
  transaction_date: string;
  is_recurring: boolean;
  category: Category | null;
}

export interface TransactionListResponse {
  total: number;
  page: number;
  page_size: number;
  items: Transaction[];
}

export interface Budget {
  id: string;
  period: BudgetPeriod;
  amount_limit: number;
  month: number;
  year: number;
  category: Category | null;
  spent: number;
  remaining: number;
  utilization_pct: number;
}

export interface Goal {
  id: string;
  name: string;
  target_amount: number;
  current_amount: number;
  target_date: string | null;
  icon: string;
  progress_pct: number;
}

export interface CategoryBreakdownItem {
  category_name: string;
  category_color: string;
  total: number;
  percentage: number;
}

export interface MonthlyTrendItem {
  month: string;
  income: number;
  expense: number;
  net: number;
}

export interface DashboardSummary {
  total_balance: number;
  monthly_income: number;
  monthly_expense: number;
  net_savings: number;
  savings_rate_pct: number;
  category_breakdown: CategoryBreakdownItem[];
  monthly_trends: MonthlyTrendItem[];
  recent_transactions_count: number;
}
