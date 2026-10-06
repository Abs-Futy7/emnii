export type ClientStatus =
  | "onboarding"
  | "active"
  | "needs-attention"
  | "disabled";

export type Client = {
  id: string;
  workspaceId: string;
  company: string;
  industry: string;
  status: ClientStatus;
  records: number;
  documents: number;
  dataQualityScore: number;
  integrations: string[];
  lastActivity: string;
};
