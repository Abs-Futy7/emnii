export type IntegrationStatus = "Connected" | "Disconnected" | "Degraded";
export type IntegrationHealth = "Healthy" | "Warning" | "Offline";

export type Integration = {
  id: string;
  name: string;
  category: string;
  description: string;
  icon: "github" | "slack" | "crm" | "ticketing" | "api" | "mockcorp";
  status: IntegrationStatus;
  lastSync: string;
  recordsSynced: number;
  health: IntegrationHealth;
  details: {
    endpoint: string;
    authenticationType: string;
    apiLatency: string;
    failedRequests: number;
    schemaDriftDetected: boolean;
  };
};
