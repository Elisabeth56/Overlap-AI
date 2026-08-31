import { redirect } from "next/navigation";

export default function Home() {
  const fixture = process.env.NEXT_PUBLIC_FIXTURE_PROJECT_ID;
  if (fixture) redirect(`/projects/${fixture}`);
  return (
    <main className="mx-auto max-w-2xl p-8">
      <h1 className="text-2xl font-semibold">Overlap</h1>
      <p className="mt-2 text-sm opacity-70">
        Set NEXT_PUBLIC_FIXTURE_PROJECT_ID in <code>.env.local</code> to jump straight to a project.
      </p>
    </main>
  );
}
