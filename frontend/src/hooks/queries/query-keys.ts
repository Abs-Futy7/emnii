export const queryKeys = {
  clients: { all: ["clients"] as const, detail: (clientId: string) => ["clients", clientId] as const },
  datasets: (clientId: string) => ["clients", clientId, "datasets"] as const,
  documents: (clientId: string) => ["clients", clientId, "documents"] as const,
  tickets: { all: ["tickets"] as const, detail: (ticketId: string) => ["tickets", ticketId] as const },
  assistant: (clientId: string) => ["clients", clientId, "assistant"] as const,
  integrations: ["integrations"] as const,
  monitoring: ["monitoring"] as const,
};
