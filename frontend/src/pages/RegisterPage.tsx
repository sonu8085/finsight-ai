import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { AxiosError } from "axios";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await register(email, fullName, password);
      navigate("/");
    } catch (err) {
      const message =
        err instanceof AxiosError ? err.response?.data?.detail ?? "Registration failed" : "Registration failed";
      setError(typeof message === "string" ? message : "Registration failed");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="font-display text-3xl font-semibold">
            FinSight <span className="text-emerald">AI</span>
          </div>
          <p className="text-paper-muted text-sm mt-2">Open your ledger in under a minute.</p>
        </div>

        <form onSubmit={handleSubmit} className="card p-6 space-y-4">
          {error && (
            <div className="bg-coral/10 border border-coral/30 text-coral text-sm rounded-xl px-3.5 py-2.5">
              {error}
            </div>
          )}
          <div>
            <label className="label mb-1.5 block" htmlFor="fullName">
              Full name
            </label>
            <input
              id="fullName"
              type="text"
              required
              minLength={2}
              className="input w-full"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Jane Doe"
            />
          </div>
          <div>
            <label className="label mb-1.5 block" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              className="input w-full"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
            />
          </div>
          <div>
            <label className="label mb-1.5 block" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              minLength={8}
              className="input w-full"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 8 characters"
            />
          </div>
          <button type="submit" disabled={isSubmitting} className="btn-primary w-full">
            {isSubmitting ? "Creating account…" : "Create account"}
          </button>
        </form>

        <p className="text-center text-sm text-paper-muted mt-6">
          Already have an account?{" "}
          <Link to="/login" className="text-emerald hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
