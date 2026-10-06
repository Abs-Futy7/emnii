import type { Client } from "@/types/client";

export const clients: Client[] = [
  {
    id: "shopnest",
    workspaceId: "ws_shopnest_01",
    company: "ShopNest",
    industry: "E-commerce",
    status: "active",
    records: 1_284_500,
    documents: 482,
    dataQualityScore: 96,
    integrations: ["Zendesk", "Shopify", "Slack", "Segment"],
    lastActivity: "12 minutes ago",
  },
  {
    id: "techmart",
    workspaceId: "ws_techmart_01",
    company: "TechMart",
    industry: "Consumer Electronics",
    status: "onboarding",
    records: 842_300,
    documents: 216,
    dataQualityScore: 88,
    integrations: ["Intercom", "Salesforce"],
    lastActivity: "38 minutes ago",
  },
  {
    id: "acme-commerce",
    workspaceId: "ws_acme_01",
    company: "Acme Commerce",
    industry: "Retail",
    status: "needs-attention",
    records: 2_104_820,
    documents: 731,
    dataQualityScore: 74,
    integrations: ["Freshdesk", "HubSpot", "Stripe"],
    lastActivity: "2 hours ago",
  },
  {
    id: "novaretail",
    workspaceId: "ws_novaretail_01",
    company: "NovaRetail",
    industry: "Retail",
    status: "active",
    records: 675_400,
    documents: 354,
    dataQualityScore: 93,
    integrations: ["Zendesk", "Microsoft Teams", "Snowflake"],
    lastActivity: "3 hours ago",
  },
  {
    id: "brightdesk",
    workspaceId: "ws_brightdesk_01",
    company: "BrightDesk",
    industry: "B2B SaaS",
    status: "active",
    records: 438_900,
    documents: 198,
    dataQualityScore: 91,
    integrations: ["Intercom", "Slack"],
    lastActivity: "Yesterday",
  },
  {
    id: "finora",
    workspaceId: "ws_finora_01",
    company: "Finora",
    industry: "Financial Services",
    status: "disabled",
    records: 319_750,
    documents: 127,
    dataQualityScore: 82,
    integrations: ["Salesforce"],
    lastActivity: "6 days ago",
  },
];

export const clientIndustries = Array.from(
  new Set(clients.map((client) => client.industry)),
).sort();

export const recentClients = clients.slice(0, 4);

export function getClientById(clientId: string) {
  return clients.find((client) => client.id === clientId);
}
