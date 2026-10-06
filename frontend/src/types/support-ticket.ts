import type { AIMessage, AssistantSource } from "@/types/support-assistant";

export type TicketPriority = "Low" | "Medium" | "High" | "Urgent";
export type TicketStatus = "Open" | "In Progress" | "Waiting" | "Resolved";

export type SupportTicket = {
  id: string;
  customer: { name: string; email: string; tier: string; location: string };
  subject: string;
  priority: TicketPriority;
  status: TicketStatus;
  assignedAgent: string;
  aiRecommendation: string;
  createdAt: string;
  conversation: AIMessage[];
  relatedOrder: { id: string; status: string; total: string; fulfillment: string };
  previousTickets: Array<{ id: string; subject: string; status: TicketStatus }>;
  suggestedResponse: string;
  sources: AssistantSource[];
};
