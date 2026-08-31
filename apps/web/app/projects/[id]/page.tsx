import EventFeed from "./EventFeed";

export default function ProjectPage({ params }: { params: { id: string } }) {
  return (
    <main className="mx-auto max-w-4xl p-8">
      <header className="mb-6">
        <p className="text-xs uppercase tracking-wide opacity-60">Project</p>
        <h1 className="mt-1 font-mono text-sm break-all">{params.id}</h1>
      </header>

      <section>
        <h2 className="mb-2 text-sm font-medium opacity-70">Event feed</h2>
        <EventFeed projectId={params.id} />
      </section>
    </main>
  );
}
