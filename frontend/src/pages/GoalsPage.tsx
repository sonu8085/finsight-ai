import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, Target, Trash2, X } from "lucide-react";
import { api } from "../api/client";
import type { Goal } from "../types";

function formatCurrency(value: number) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(value);
}

function NewGoalModal({ onClose }: { onClose: () => void }) {
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [targetAmount, setTargetAmount] = useState("");
  const [currentAmount, setCurrentAmount] = useState("");

  const createMutation = useMutation({
    mutationFn: async () =>
      api.post("/goals", {
        name,
        target_amount: Number(targetAmount),
        current_amount: Number(currentAmount || 0),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["goals"] });
      onClose();
    },
  });

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4">
      <div className="card w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-display text-lg font-semibold">New goal</h2>
          <button onClick={onClose} className="text-paper-faint hover:text-paper">
            <X size={20} />
          </button>
        </div>
        <div className="space-y-3">
          <div>
            <label className="label mb-1.5 block">Goal name</label>
            <input
              className="input w-full"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Emergency Fund"
            />
          </div>
          <div>
            <label className="label mb-1.5 block">Target amount</label>
            <input
              type="number"
              min="1"
              className="input w-full"
              value={targetAmount}
              onChange={(e) => setTargetAmount(e.target.value)}
              placeholder="10000"
            />
          </div>
          <div>
            <label className="label mb-1.5 block">Already saved (optional)</label>
            <input
              type="number"
              min="0"
              className="input w-full"
              value={currentAmount}
              onChange={(e) => setCurrentAmount(e.target.value)}
              placeholder="0"
            />
          </div>
        </div>
        <button
          className="btn-primary w-full mt-6"
          disabled={!name || !targetAmount || createMutation.isPending}
          onClick={() => createMutation.mutate()}
        >
          {createMutation.isPending ? "Saving…" : "Create goal"}
        </button>
      </div>
    </div>
  );
}

export default function GoalsPage() {
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);

  const { data: goals, isLoading } = useQuery({
    queryKey: ["goals"],
    queryFn: async () => (await api.get<Goal[]>("/goals")).data,
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => api.delete(`/goals/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["goals"] }),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold">Financial goals</h1>
          <p className="text-paper-muted text-sm mt-1">Track progress toward what matters</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-primary flex items-center gap-2">
          <Plus size={17} /> New goal
        </button>
      </div>

      {isLoading ? (
        <div className="text-paper-muted animate-pulse">Loading goals…</div>
      ) : goals?.length === 0 ? (
        <div className="card p-12 text-center">
          <Target className="mx-auto text-paper-faint mb-3" size={28} />
          <p className="text-paper-muted">No goals yet.</p>
          <p className="text-paper-faint text-sm mt-1">Create one for your emergency fund, a trip, or anything else.</p>
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-4">
          {goals?.map((g) => (
            <div key={g.id} className="card p-5">
              <div className="flex items-start justify-between mb-4">
                <div className="w-10 h-10 rounded-xl bg-gold/15 border border-gold/30 flex items-center justify-center">
                  <Target size={18} className="text-gold" />
                </div>
                <button
                  onClick={() => deleteMutation.mutate(g.id)}
                  className="text-paper-faint hover:text-coral transition p-1"
                >
                  <Trash2 size={14} />
                </button>
              </div>
              <p className="font-medium text-paper mb-1">{g.name}</p>
              <p className="text-xs text-paper-faint mb-3">
                {formatCurrency(g.current_amount)} of {formatCurrency(g.target_amount)}
              </p>
              <div className="h-2 bg-ink-raised rounded-full overflow-hidden mb-2">
                <div className="h-full bg-gold rounded-full transition-all" style={{ width: `${g.progress_pct}%` }} />
              </div>
              <p className="text-xs text-gold">{g.progress_pct}% complete</p>
            </div>
          ))}
        </div>
      )}

      {showModal && <NewGoalModal onClose={() => setShowModal(false)} />}
    </div>
  );
}
