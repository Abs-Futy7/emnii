export type AssistantSource = {
  id: string;
  title: string;
  type: string;
  detail: string;
  updatedAt: string;
};

export type ToolCall = {
  id: string;
  label: string;
  result: string;
  duration: string;
  status: "complete" | "warning";
};

export type ToolActivity = ToolCall;

export type AIMessage = {
  id: string;
  role: "customer" | "agent" | "assistant" | "system";
  author: string;
  content: string;
  createdAt: string;
};

export type SupportAssistantCase = {
  caseId: string;
  customerMessage: string;
  issueSummary: string;
  contextGathered: string[];
  recommendedAction: string;
  suggestedResponse: string;
  sources: AssistantSource[];
  tools: ToolActivity[];
  customer: {
    name: string;
    email: string;
    tier: string;
    lifetimeValue: string;
    openTickets: number;
  };
  order: {
    id: string;
    status: string;
    carrier: string;
    expectedDelivery: string;
    value: string;
  };
  previousTicket: {
    id: string;
    subject: string;
    status: string;
    openedAt: string;
  };
};
