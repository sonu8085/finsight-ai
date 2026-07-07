import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, Search, Trash2, X } from "lucide-react";
import { api } from "../api/client";
import type { Category, Transaction, TransactionListResponse, TransactionType } from "../types";

function formatCurrency(value: number) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(value);
}

function NewTransactionModal({ onClose, categories }: { onClose: () => void; categories: Category[] }) {
  const queryClient = useQueryClient();
  const [type, setType] = useState<TransactionType>("expense");
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10));

  const filteredCategories = categories.filter((c) => c.type === type);

  const createMutation = useMutation({
    mutationFn: async () =>
      api.post("/transactions", {
        type,
        amount: Number(amount),
        description,
        category_id: categoryId || null,
        transaction_date: date,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      onClose();
    },
  });

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4">
      <div className="card w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-display text-lg font-semibold">New transaction</h2>
          <button onClick={onClose} className="text-paper-faint hover:text-paper">
            <X size={20} />
          </button>
        </div>

        <div className="flex gap-2 mb-4">
          {(["expense", "income"] as const).map((t) => (
            <button
              key={t}
              onClick={() => {
                setType(t);
                setCategoryId("");
              }}
              className={`flex-1 py-2 rounded-xl text-sm font-medium capitalize transition ${
                type === t ? "bg-emerald/15 text-emerald border border-emerald/30" : "bg-ink-raised text-paper-muted"
              }`}
            >
              {t}
            </button>
          ))}
        </div>

        <div className="space-y-3">
          <div>
            <label className="label mb-1.5 block">Amount</label>
            <input
              type="number"
              min="0.01"
              step="0.01"
              className="input w-full"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="0.00"
            />
          </div>
          <div>
            <label className="label mb-1.5 block">Description</label>
            <input
              type="text"
              className="input w-full"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="e.g. Grocery run"
            />
          </div>
          <div>
            <label className="label mb-1.5 block">Category</label>
            <select className="input w-full" value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
              <option value="">Uncategorized</option>
              {filteredCategories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label mb-1.5 block">Date</label>
            <input type="date" className="input w-full" value={date} onChange={(e) => setDate(e.target.value)} />
          </div>
        </div>

        <button
          className="btn-primary w-full mt-6"
          disabled={!amount || !description || createMutation.isPending}
          onClick={() => createMutation.mutate()}
        >
          {createMutation.isPending ? "Saving…" : "Save transaction"}
        </button>
      </div>
    </div>
  );
}

export default function TransactionsPage() {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState<TransactionType | "">("");
  const [showModal, setShowModal] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  const { data: categories } = useQuery({
    queryKey: ["categories"],
    queryFn: async () => (await api.get<Category[]>("/categories")).data,
  });

  const { data, isLoading } = useQuery({
    queryKey: ["transactions", page, search, typeFilter],
    queryFn: async () =>
      (
        await api.get<TransactionListResponse>("/transactions", {
          params: { page, page_size: 15, search: search || undefined, type: typeFilter || undefined },
        })
      ).data,
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => api.delete(`/transactions/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
    },
  });

  const bulkDeleteMutation = useMutation({
    mutationFn: async () => api.post("/transactions/bulk-delete", { ids: Array.from(selectedIds) }),
    onSuccess: () => {
      setSelectedIds(new Set());
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
    },
  });

  function toggleSelect(id: string) {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }

  const totalPages = data ? Math.max(1, Math.ceil(data.total / data.page_size)) : 1;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold">Transactions</h1>
          <p className="text-paper-muted text-sm mt-1">{data?.total ?? 0} entries in your ledger</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-primary flex items-center gap-2">
          <Plus size={17} /> New transaction
        </button>
      </div>

      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-xs">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-paper-faint" />
          <input
            className="input w-full pl-9"
            placeholder="Search description or merchant…"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
          />
        </div>
        <select
          className="input"
          value={typeFilter}
          onChange={(e) => {
            setTypeFilter(e.target.value as TransactionType | "");
            setPage(1);
          }}
        >
          <option value="">All types</option>
          <option value="income">Income</option>
          <option value="expense">Expense</option>
        </select>
        {selectedIds.size > 0 && (
          <button
            onClick={() => bulkDeleteMutation.mutate()}
            className="flex items-center gap-2 text-sm text-coral bg-coral/10 border border-coral/30 rounded-xl px-3.5 py-2.5 hover:bg-coral/20 transition"
          >
            <Trash2 size={15} /> Delete {selectedIds.size} selected
          </button>
        )}
      </div>

      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-paper-muted animate-pulse">Loading transactions…</div>
        ) : data?.items.length === 0 ? (
          <div className="p-12 text-center">
            <p className="text-paper-muted">No transactions match your filters yet.</p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-ink-border text-paper-faint text-xs uppercase tracking-wide">
                <th className="w-10 py-3 pl-4"></th>
                <th className="text-left py-3 font-medium">Description</th>
                <th className="text-left py-3 font-medium">Category</th>
                <th className="text-left py-3 font-medium">Date</th>
                <th className="text-right py-3 font-medium pr-4">Amount</th>
                <th className="w-10"></th>
              </tr>
            </thead>
            <tbody>
              {data?.items.map((t: Transaction) => (
                <tr key={t.id} className="border-b border-ink-border last:border-0 hover:bg-ink-raised/50 transition">
                  <td className="pl-4 py-3">
                    <input
                      type="checkbox"
                      checked={selectedIds.has(t.id)}
                      onChange={() => toggleSelect(t.id)}
                      className="accent-emerald"
                    />
                  </td>
                  <td className="py-3">
                    <p className="text-paper font-medium">{t.description}</p>
                    {t.merchant && <p className="text-paper-faint text-xs">{t.merchant}</p>}
                  </td>
                  <td className="py-3">
                    {t.category ? (
                      <span
                        className="inline-flex items-center gap-1.5 text-xs px-2 py-1 rounded-full"
                        style={{ backgroundColor: `${t.category.color}22`, color: t.category.color }}
                      >
                        {t.category.name}
                      </span>
                    ) : (
                      <span className="text-paper-faint text-xs">Uncategorized</span>
                    )}
                  </td>
                  <td className="py-3 text-paper-muted font-mono text-xs">
                    {new Date(t.transaction_date).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                  </td>
                  <td
                    className={`py-3 pr-4 text-right font-mono font-medium ${
                      t.type === "income" ? "text-emerald" : "text-coral"
                    }`}
                  >
                    {t.type === "income" ? "+" : "−"}
                    {formatCurrency(t.amount)}
                  </td>
                  <td className="pr-3">
                    <button
                      onClick={() => deleteMutation.mutate(t.id)}
                      className="text-paper-faint hover:text-coral transition p-1"
                    >
                      <Trash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {data && data.total > 0 && (
        <div className="flex items-center justify-between text-sm text-paper-muted">
          <span>
            Page {page} of {totalPages}
          </span>
          <div className="flex gap-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
              className="btn-secondary px-3 py-1.5 text-xs disabled:opacity-30"
            >
              Previous
            </button>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
              className="btn-secondary px-3 py-1.5 text-xs disabled:opacity-30"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {showModal && <NewTransactionModal onClose={() => setShowModal(false)} categories={categories ?? []} />}
    </div>
  );
}
