import type { SupportAssistantCase } from "@/types/support-assistant";

export const supportAssistantCase: SupportAssistantCase = {
  caseId: "CASE-58421",
  customerMessage:
    "My order #A9132 has not arrived and I already contacted support last week.",
  issueSummary: "Order #A9132 is delayed beyond its delivery window.",
  contextGathered: [
    "Order API",
    "Customer CRM record",
    "Previous ticket #48329",
    "Shipping Policy v3.2",
  ],
  recommendedAction:
    "Customer is eligible for a full refund or a no-cost replacement with expedited shipping.",
  suggestedResponse:
    "Hi Nadia, I’m sorry your order still hasn’t arrived, especially after you contacted us last week. I confirmed that order #A9132 is past its delivery window. We can issue a full refund to your original payment method or send a replacement at no cost with expedited shipping. Please let me know which option you prefer, and I’ll take care of it right away.",
  sources: [
    { id: "source-order", title: "Order #A9132", type: "Order API", detail: "Shipment delayed; no carrier scan in 6 days.", updatedAt: "2 minutes ago" },
    { id: "source-crm", title: "Nadia Rahman", type: "CRM record", detail: "Gold-tier customer with 14 completed orders.", updatedAt: "4 minutes ago" },
    { id: "source-ticket", title: "Ticket #48329", type: "Previous ticket", detail: "Customer reported the delay last week; carrier trace opened.", updatedAt: "7 days ago" },
    { id: "source-policy", title: "Shipping Policy v3.2", type: "Knowledge document", detail: "Refund or replacement permitted after 5 days without a carrier scan.", updatedAt: "Sep 28, 2026" },
  ],
  tools: [
    { id: "tool-customer", label: "Fetch customer", result: "Customer profile found", duration: "84 ms", status: "complete" },
    { id: "tool-order", label: "Fetch order", result: "Order and shipment found", duration: "112 ms", status: "complete" },
    { id: "tool-tickets", label: "Search previous tickets", result: "1 related ticket found", duration: "168 ms", status: "complete" },
    { id: "tool-policy", label: "Retrieve shipping policy", result: "Policy v3.2 retrieved", duration: "224 ms", status: "complete" },
  ],
  customer: {
    name: "Nadia Rahman",
    email: "nadia.rahman@example.com",
    tier: "Gold",
    lifetimeValue: "$2,840",
    openTickets: 1,
  },
  order: {
    id: "A9132",
    status: "Delayed",
    carrier: "ParcelFlow",
    expectedDelivery: "Sep 29, 2026",
    value: "$184.50",
  },
  previousTicket: {
    id: "48329",
    subject: "Order has not arrived",
    status: "Waiting on carrier",
    openedAt: "Sep 30, 2026",
  },
};
