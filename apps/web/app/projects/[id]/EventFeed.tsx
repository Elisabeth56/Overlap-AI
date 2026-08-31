"use client";

import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";

type EventRow = {
  id: number;
  kind: string;
  actor: string;
  payload: Record<string, unknown> | null;
  at: string;
};

export default function EventFeed({ projectId }: { projectId: string }) {
  const [events, setEvents] = useState<EventRow[]>([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    let cancelled = false;

    // Initial fetch — 50 most recent events.
    supabase
      .from("events")
      .select("id, kind, actor, payload, at")
      .eq("project_id", projectId)
      .order("at", { ascending: false })
      .limit(50)
      .then(({ data, error }) => {
        if (cancelled) return;
        if (error) {
          console.error(error);
          return;
        }
        setEvents((data ?? []) as EventRow[]);
      });

    // Subscribe to new inserts for this project.
    const channel = supabase
      .channel(`events:${projectId}`)
      .on(
        "postgres_changes",
        {
          event: "INSERT",
          schema: "public",
          table: "events",
          filter: `project_id=eq.${projectId}`,
        },
        (msg) => {
          setEvents((prev) => [msg.new as EventRow, ...prev].slice(0, 200));
        },
      )
      .subscribe((status) => setConnected(status === "SUBSCRIBED"));

    return () => {
      cancelled = true;
      supabase.removeChannel(channel);
    };
  }, [projectId]);

  return (
    <div>
      <p className="mb-2 text-xs opacity-60">
        Realtime: {connected ? "connected" : "connecting…"}
      </p>

      {events.length === 0 ? (
        <div className="rounded-md border border-dashed border-neutral-300 p-6 text-sm opacity-70 dark:border-neutral-800">
          No events yet. Trigger a handoff to see items stream in.
        </div>
      ) : (
        <ol className="divide-y divide-neutral-200 rounded-md border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
          {events.map((e) => (
            <li key={e.id} className="flex items-baseline gap-3 p-3 text-sm">
              <time className="w-40 shrink-0 font-mono text-xs opacity-60">
                {new Date(e.at).toLocaleTimeString()}
              </time>
              <span className="rounded bg-neutral-200 px-1.5 py-0.5 font-mono text-xs dark:bg-neutral-800">
                {e.actor}
              </span>
              <span className="font-medium">{e.kind}</span>
              {e.payload && Object.keys(e.payload).length > 0 && (
                <code className="ml-auto truncate text-xs opacity-60">
                  {JSON.stringify(e.payload)}
                </code>
              )}
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
