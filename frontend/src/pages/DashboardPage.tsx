import { useQuery } from "@tanstack/react-query";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ArrowDownRight, ArrowUpRight, TrendingUp, Wallet } from "lucide-react";
import { api } from "../api/client";
import type { DashboardSummary } from "../types";

function formatCurrency(value: number) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(value);
}

function LedgerNumber({ value, tone }: { value: number; tone: "positive" | "negative" | "neutral" }) {
  const color = tone === "positive" ? "text-emerald" : tone === "negative" ? "text-coral" : "text-paper";
  const [whole, decimal] = Math.abs(value).toFixed(2).split(".");
  return (
    <span className={`font-display font-medium ${color}`}>
      {value < 0 && "−"}
      <span className="text-4xl tracking-tight">{formatCurrency(Number(whole)).replace(/\.\d+$/, "")}</span>
      <span className="font-mono text-lg text-paper-faint">.{decimal}</span>
    </span>
  );
}

export default function DashboardPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: async () => (await api.get<DashboardSummary>("/dashboard/summary")).data,
  });

  if (isLoading) {
    return <div className="text-paper-muted animate-pulse">Loading your ledger…</div>;
  }
  if (error || !data) {
    return <div className="text-coral">Couldn't load your dashboard. Please try again.</div>;
  }

  const maxCategoryTotal = Math.max(...data.category_breakdown.map((c) => c.total), 1);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-display text-2xl font-semibold">Overview</h1>
        <p className="text-paper-muted text-sm mt-1">
          Your balance, at a glance — {new Date().toLocaleDateString("en-US", { month: "long", year: "numeric" })}
        </p>
      </div>

      {/* Hero balance */}
      <div className="card p-8">
        <p className="label mb-3">Total balance</p>
        <LedgerNumber
          value={data.total_balance}
          tone={data.total_balance >= 0 ? "positive" : "negative"}
        />
        <div className="mt-6 flex items-center gap-2 text-sm">
          <div className="flex items-center gap-1.5 text-emerald">
            <TrendingUp size={15} />
            <span>{data.savings_rate_pct}% savings rate this month</span>
          </div>
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-3 gap-4">
        <div className="card p-5">
          <div className="flex items-center gap-2 text-paper-muted mb-2">
            <ArrowUpRight size={16} className="text-emerald" />
            <span className="label">Income this month</span>
          </div>
          <p className="font-mono text-xl font-medium text-paper">{formatCurrency(data.monthly_income)}</p>
        </div>
        <div className="card p-5">
          <div className="flex items-center gap-2 text-paper-muted mb-2">
            <ArrowDownRight size={16} className="text-coral" />
            <span className="label">Expenses this month</span>
          </div>
          <p className="font-mono text-xl font-medium text-paper">{formatCurrency(data.monthly_expense)}</p>
        </div>
        <div className="card p-5">
          <div className="flex items-center gap-2 text-paper-muted mb-2">
            <Wallet size={16} className="text-gold" />
            <span className="label">Net savings</span>
          </div>
          <p className="font-mono text-xl font-medium text-paper">{formatCurrency(data.net_savings)}</p>
        </div>
      </div>

      <div className="grid grid-cols-5 gap-4">
        {/* Trend chart */}
        <div className="card p-6 col-span-3">
          <p className="label mb-4">Income vs. expense trend</p>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={data.monthly_trends}>
              <defs>
                <linearGradient id="incomeGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#3DD68C" stopOpacity={0.35} />
                  <stop offset="100%" stopColor="#3DD68C" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="expenseGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#FF6B5D" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="#FF6B5D" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#232F47" vertical={false} />
              <XAxis
                dataKey="month"
                stroke="#5C6883"
                fontSize={11}
                tickLine={false}
                axisLine={false}
                tickFormatter={(m) => m.slice(5)}
              />
              <YAxis stroke="#5C6883" fontSize={11} tickLine={false} axisLine={false} width={40} />
              <Tooltip
                contentStyle={{
                  background: "#182238",
                  border: "1px solid #232F47",
                  borderRadius: 12,
                  fontSize: 12,
                }}
                labelStyle={{ color: "#8B96AB" }}
              />
              <Area type="monotone" dataKey="income" stroke="#3DD68C" fill="url(#incomeGrad)" strokeWidth={2} />
              <Area type="monotone" dataKey="expense" stroke="#FF6B5D" fill="url(#expenseGrad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Category breakdown - ledger lines */}
        <div className="card p-6 col-span-2">
          <p className="label mb-4">Spending by category</p>
          {data.category_breakdown.length === 0 ? (
            <p className="text-paper-faint text-sm py-8 text-center">No expenses recorded this month yet.</p>
          ) : (
            <div className="space-y-3.5">
              {data.category_breakdown.slice(0, 6).map((cat) => (
                <div key={cat.category_name}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-paper">{cat.category_name}</span>
                    <span className="font-mono text-paper-muted">{formatCurrency(cat.total)}</span>
                  </div>
                  <div className="h-1.5 bg-ink-raised rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${(cat.total / maxCategoryTotal) * 100}%`,
                        backgroundColor: cat.category_color,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
