// TODO: Replace null values only after the FastAPI route contract is documented.
// Keeping these unset prevents the frontend from silently assuming backend paths.
export const endpoints = {
  clients: { list: null as string | null, detail: null as ((clientId: string) => string) | null },
  datasets: { list: null as ((clientId: string) => string) | null, upload: null as ((clientId: string) => string) | null },
  documents: { list: null as ((clientId: string) => string) | null, upload: null as ((clientId: string) => string) | null },
  tickets: { list: null as string | null, detail: null as ((ticketId: string) => string) | null },
  assistant: { case: null as ((clientId: string) => string) | null },
  integrations: { list: null as string | null },
  monitoring: { snapshot: null as string | null },
} as const;
