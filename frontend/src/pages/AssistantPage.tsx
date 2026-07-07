import { useEffect, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Send, Sparkles } from "lucide-react";
import { api } from "../api/client";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

const suggestedPrompts = [
  "Where did I spend the most this month?",
  "How much can I realistically save?",
  "Compare this month with last month.",
  "Which subscriptions should I reconsider?",
];

export default function AssistantPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const { data: insightsData } = useQuery({
    queryKey: ["ai-insights"],
    queryFn: async () => (await api.get<{ insights: string[] }>("/ai/insights")).data,
  });

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  async function sendMessage(text: string) {
    if (!text.trim() || isSending) return;
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setIsSending(true);
    try {
      const { data } = await api.post<{ reply: string }>("/ai/chat", { message: text });
      setMessages((prev) => [...prev, { role: "assistant", content: data.reply }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, something went wrong. Please try again." },
      ]);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="flex gap-6 h-[calc(100vh-4rem)]">
      <div className="flex-1 flex flex-col card overflow-hidden">
        <div className="px-6 py-4 border-b border-ink-border flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-emerald/15 border border-emerald/30 flex items-center justify-center">
            <Sparkles size={16} className="text-emerald" />
          </div>
          <div>
            <p className="font-medium text-paper text-sm">FinSight Assistant</p>
            <p className="text-xs text-paper-faint">Ask anything about your spending</p>
          </div>
        </div>

        <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-5 space-y-4">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <Sparkles size={28} className="text-paper-faint mb-3" />
              <p className="text-paper-muted text-sm mb-4">Ask me anything about your finances.</p>
              <div className="flex flex-wrap gap-2 justify-center max-w-md">
                {suggestedPrompts.map((p) => (
                  <button
                    key={p}
                    onClick={() => sendMessage(p)}
                    className="text-xs px-3 py-2 rounded-full bg-ink-raised border border-ink-border text-paper-muted hover:border-emerald/40 hover:text-emerald transition"
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm whitespace-pre-wrap ${
                  m.role === "user" ? "bg-emerald text-ink font-medium" : "bg-ink-raised text-paper"
                }`}
              >
                {m.content}
              </div>
            </div>
          ))}
          {isSending && (
            <div className="flex justify-start">
              <div className="bg-ink-raised rounded-2xl px-4 py-2.5 text-sm text-paper-faint animate-pulse">
                Thinking…
              </div>
            </div>
          )}
        </div>

        <form
          className="p-4 border-t border-ink-border flex gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            sendMessage(input);
          }}
        >
          <input
            className="input flex-1"
            placeholder="Ask about your spending…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button type="submit" className="btn-primary px-4" disabled={isSending || !input.trim()}>
            <Send size={16} />
          </button>
        </form>
      </div>

      <aside className="w-72 shrink-0 card p-5 h-fit">
        <p className="label mb-3">Auto-generated insights</p>
        {!insightsData ? (
          <p className="text-paper-faint text-sm animate-pulse">Analyzing…</p>
        ) : (
          <ul className="space-y-3">
            {insightsData.insights.map((insight, i) => (
              <li key={i} className="text-sm text-paper-muted leading-relaxed flex gap-2">
                <span className="text-emerald mt-1">·</span>
                <span>{insight}</span>
              </li>
            ))}
          </ul>
        )}
      </aside>
    </div>
  );
}
