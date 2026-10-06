import type { SupportTicket } from "@/types/support-ticket";

const baseDetails = {
  conversation: [
    { id: "m1", role: "customer" as const, author: "Customer", content: "My order still has not arrived, and I contacted support last week. Can you help?", createdAt: "Oct 6, 9:14 AM" },
    { id: "m2", role: "agent" as const, author: "Maya Chen", content: "I’m reviewing the carrier events and your earlier case now.", createdAt: "Oct 6, 9:18 AM" },
  ],
  relatedOrder: { id: "A9132", status: "Delayed", total: "$184.00", fulfillment: "Express shipping" },
  previousTickets: [{ id: "48329", subject: "Delivery status request", status: "Resolved" as const }],
  suggestedResponse: "I’m sorry for the delay. I confirmed that your shipment missed its latest carrier scan. You are eligible for either an immediate replacement or a full refund. Please let me know which option you prefer, and I’ll arrange it today.",
  sources: [
    { id: "s1", title: "Shipping Policy v3.2", type: "Knowledge base", detail: "Delayed shipment remediation", updatedAt: "Sep 28, 2026" },
    { id: "s2", title: "Order A9132", type: "Order API", detail: "Latest fulfillment events", updatedAt: "Oct 6, 2026" },
  ],
};

export const supportTickets: SupportTicket[] = [
  { id: "TCK-10482", customer: { name: "Elena Marquez", email: "elena@example.com", tier: "Enterprise", location: "Austin, US" }, subject: "Order A9132 has not arrived", priority: "Urgent", status: "Open", assignedAgent: "Maya Chen", aiRecommendation: "Offer refund or replacement", createdAt: "Oct 6, 9:14 AM", ...baseDetails },
  { id: "TCK-10481", customer: { name: "Jon Bell", email: "jon@example.com", tier: "Business", location: "London, UK" }, subject: "Unable to update billing address", priority: "High", status: "In Progress", assignedAgent: "Owen Wright", aiRecommendation: "Verify identity, then update CRM", createdAt: "Oct 6, 8:42 AM", ...baseDetails },
  { id: "TCK-10478", customer: { name: "Priya Shah", email: "priya@example.com", tier: "Enterprise", location: "Toronto, CA" }, subject: "Duplicate charge on latest invoice", priority: "High", status: "Waiting", assignedAgent: "Sara Kim", aiRecommendation: "Request transaction reference", createdAt: "Oct 6, 7:58 AM", ...baseDetails },
  { id: "TCK-10473", customer: { name: "Marcus Green", email: "marcus@example.com", tier: "Standard", location: "Denver, US" }, subject: "Product return eligibility", priority: "Medium", status: "Open", assignedAgent: "Unassigned", aiRecommendation: "Approve return under 30-day policy", createdAt: "Oct 5, 6:31 PM", ...baseDetails },
  { id: "TCK-10469", customer: { name: "Aisha Rahman", email: "aisha@example.com", tier: "Business", location: "Dhaka, BD" }, subject: "Workspace export completed incorrectly", priority: "Medium", status: "Resolved", assignedAgent: "Maya Chen", aiRecommendation: "Regenerate export", createdAt: "Oct 5, 4:17 PM", ...baseDetails },
  { id: "TCK-10461", customer: { name: "Theo Martin", email: "theo@example.com", tier: "Standard", location: "Paris, FR" }, subject: "Question about plan limits", priority: "Low", status: "Resolved", assignedAgent: "Owen Wright", aiRecommendation: "Share plan comparison", createdAt: "Oct 5, 1:22 PM", ...baseDetails },
];

export function getTicketById(ticketId: string) {
  return supportTickets.find((ticket) => ticket.id === ticketId);
}
