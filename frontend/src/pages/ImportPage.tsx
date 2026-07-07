import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { FileUp, Upload } from "lucide-react";
import { api } from "../api/client";

interface PreviewResponse {
  columns: string[];
  preview_rows: Record<string, string>[];
  total_rows: number;
}

interface ImportResult {
  imported: number;
  skipped_duplicates: number;
  skipped_invalid: number;
  total_rows: number;
}

export default function ImportPage() {
  const queryClient = useQueryClient();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<PreviewResponse | null>(null);
  const [mapping, setMapping] = useState<Record<string, string>>({});
  const [result, setResult] = useState<ImportResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFileSelect(selected: File) {
    setFile(selected);
    setResult(null);
    setError(null);
    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", selected);
      const { data } = await api.post<PreviewResponse>("/import/preview", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setPreview(data);
      setMapping({});
    } catch {
      setError("Could not read this CSV file. Please check the format and try again.");
      setPreview(null);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleConfirmImport() {
    if (!file || !mapping.date || !mapping.description || !mapping.amount) return;
    setIsLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("column_map", JSON.stringify(mapping));
      formData.append("default_type", "expense");
      const { data } = await api.post<ImportResult>("/import/confirm", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(data);
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
    } catch {
      setError("Import failed. Please check your column mapping and try again.");
    } finally {
      setIsLoading(false);
    }
  }

  const requiredFields: { key: string; label: string }[] = [
    { key: "date", label: "Date" },
    { key: "description", label: "Description" },
    { key: "amount", label: "Amount" },
  ];
  const optionalFields: { key: string; label: string }[] = [
    { key: "merchant", label: "Merchant (optional)" },
    { key: "type", label: "Type — credit/debit (optional)" },
  ];

  const canImport = mapping.date && mapping.description && mapping.amount;

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="font-display text-2xl font-semibold">Import bank statement</h1>
        <p className="text-paper-muted text-sm mt-1">
          Upload a CSV export from your bank. We'll detect duplicates automatically.
        </p>
      </div>

      {!preview && (
        <label className="card flex flex-col items-center justify-center gap-3 p-12 border-dashed cursor-pointer hover:border-emerald/40 transition">
          <FileUp size={32} className="text-paper-faint" />
          <span className="text-paper-muted text-sm">
            {isLoading ? "Reading file…" : "Click to choose a CSV file, or drag it here"}
          </span>
          <input
            type="file"
            accept=".csv"
            className="hidden"
            onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
          />
        </label>
      )}

      {error && (
        <div className="bg-coral/10 border border-coral/30 text-coral text-sm rounded-xl px-4 py-3">{error}</div>
      )}

      {preview && !result && (
        <div className="card p-6 space-y-5">
          <div>
            <p className="text-sm text-paper-muted">
              Detected <span className="text-paper font-medium">{preview.total_rows}</span> rows with columns:{" "}
              <span className="font-mono text-xs text-paper-faint">{preview.columns.join(", ")}</span>
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            {[...requiredFields, ...optionalFields].map((field) => (
              <div key={field.key}>
                <label className="label mb-1.5 block">{field.label}</label>
                <select
                  className="input w-full"
                  value={mapping[field.key] ?? ""}
                  onChange={(e) => setMapping((m) => ({ ...m, [field.key]: e.target.value }))}
                >
                  <option value="">— Not mapped —</option>
                  {preview.columns.map((col) => (
                    <option key={col} value={col}>
                      {col}
                    </option>
                  ))}
                </select>
              </div>
            ))}
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-paper-faint uppercase tracking-wide">
                  {preview.columns.map((c) => (
                    <th key={c} className="text-left py-2 pr-4 font-medium">
                      {c}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {preview.preview_rows.slice(0, 5).map((row, i) => (
                  <tr key={i} className="border-t border-ink-border">
                    {preview.columns.map((c) => (
                      <td key={c} className="py-2 pr-4 text-paper-muted">
                        {String(row[c])}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex gap-3">
            <button
              className="btn-primary flex items-center gap-2"
              disabled={!canImport || isLoading}
              onClick={handleConfirmImport}
            >
              <Upload size={16} /> {isLoading ? "Importing…" : "Confirm import"}
            </button>
            <button
              className="btn-secondary"
              onClick={() => {
                setPreview(null);
                setFile(null);
              }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {result && (
        <div className="card p-6">
          <p className="font-display text-lg font-semibold text-emerald mb-3">Import complete</p>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <p className="text-2xl font-mono text-emerald">{result.imported}</p>
              <p className="text-paper-faint">Imported</p>
            </div>
            <div>
              <p className="text-2xl font-mono text-gold">{result.skipped_duplicates}</p>
              <p className="text-paper-faint">Duplicates skipped</p>
            </div>
            <div>
              <p className="text-2xl font-mono text-coral">{result.skipped_invalid}</p>
              <p className="text-paper-faint">Invalid rows skipped</p>
            </div>
          </div>
          <button
            className="btn-secondary mt-6"
            onClick={() => {
              setResult(null);
              setPreview(null);
              setFile(null);
            }}
          >
            Import another file
          </button>
        </div>
      )}
    </div>
  );
}
