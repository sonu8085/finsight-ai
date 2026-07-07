import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2, X } from "lucide-react";
import { api } from "../api/client";
import type { Budget, Category } from "../types";

function formatCurrency(value: number) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(value);
}

const now = new Date();

function NewBudgetModal({ onClose, categories }: { onClose: () => void; categories: Category[] }) {
  const queryClient = useQueryClient();
  const [categoryId, setCategoryId] = useState("");
  const [amountLimit, setAmountLimit] = useState("");

  const createMutation = useMutation({
    mutationFn: async () =>
      api.post("/budgets", {
        category_id: categoryId || null,
        period: "monthly",
        amount_limit: Number(amountLimit),
        month: now.getMonth() + 1,
        year: now.getFullYear(),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["budgets"] });
      onClose();
    },
  });

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4">
      <div className="card w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-display text-lg font-semibold">New budget</h2>
          <button onClick={onClose} className="text-paper-faint hover:text-paper">
            <X size={20} />
          </button>
        </div>
        <div className="space-y-3">
          <div>
            <label className="label mb-1.5 block">Category</label>
            <select className="input w-full" value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
              <option value="">Overall (all spending)</option>
              {categories
                .filter((c) => c.type === "expense")
                .map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
            </select>
          </div>
          <div>
            <label className="label mb-1.5 block">Monthly limit</label>
            <input
              type="number"
              min="1"
              step="0.01"
              className="input w-full"
              value={amountLimit}
              onChange={(e) => setAmountLimit(e.target.value)}
              placeholder="500.00"
            />
          </div>
        </div>
        <button
          className="btn-primary w-full mt-6"
          disabled={!amountLimit || createMutation.isPending}
          onClick={() => createMutation.mutate()}
        >
          {createMutation.isPending ? "Saving…" : "Create budget"}
        </button>
      </div>
    </div>
  );
}

export default function BudgetsPage() {
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);

  const { data: categories } = useQuery({
    queryKey: ["categories"],
    queryFn: async () => (await api.get<Category[]>("/categories")).data,
  });

  const { data: budgets, isLoading } = useQuery({
    queryKey: ["budgets", now.getMonth(), now.getFullYear()],
    queryFn: async () =>
      (
        await api.get<Budget[]>("/budgets", {
          params: { month: now.getMonth() + 1, year: now.getFullYear() },
        })
      ).data,
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => api.delete(`/budgets/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["budgets"] }),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold">Budgets</h1>
          <p className="text-paper-muted text-sm mt-1">
            {now.toLocaleDateString("en-US", { month: "long", year: "numeric" })} spending limits
          </p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-primary flex items-center gap-2">
          <Plus size={17} /> New budget
        </button>
      </div>

      {isLoading ? (
        <div className="text-paper-muted animate-pulse">Loading budgets…</div>
      ) : budgets?.length === 0 ? (
        <div className="card p-12 text-center">
          <p className="text-paper-muted">No budgets set for this month yet.</p>
          <p className="text-paper-faint text-sm mt-1">Create one to start tracking your spending limits.</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {budgets?.map((b) => {
            const isOver = b.utilization_pct >= 100;
            const isWarning = b.utilization_pct >= 80 && !isOver;
            const barColor = isOver ? "#FF6B5D" : isWarning ? "#E8B85C" : "#3DD68C";
            return (
              <div key={b.id} className="card p-5">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <p className="font-medium text-paper">{b.category?.name ?? "Overall budget"}</p>
                    <p className="text-xs text-paper-faint mt-0.5">
                      {formatCurrency(b.spent)} of {formatCurrency(b.amount_limit)}
                    </p>
                  </div>
                  <button
                    onClick={() => deleteMutation.mutate(b.id)}
                    className="text-paper-faint hover:text-coral transition p-1"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
                <div className="h-2 bg-ink-raised rounded-full overflow-hidden mb-2">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{ width: `${Math.min(b.utilization_pct, 100)}%`, backgroundColor: barColor }}
                  />
                </div>
                <div className="flex justify-between text-xs">
                  <span style={{ color: barColor }}>{b.utilization_pct}% used</span>
                  <span className="text-paper-faint">{formatCurrency(b.remaining)} remaining</span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {showModal && <NewBudgetModal onClose={() => setShowModal(false)} categories={categories ?? []} />}
    </div>
  );
}
