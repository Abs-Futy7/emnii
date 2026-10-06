export type OnboardingStepStatus = "completed" | "pending" | "warning";

export type OnboardingStep = {
  id: string;
  title: string;
  status: OnboardingStepStatus;
  detail: string;
};

export type IngestionJob = {
  id: string;
  source: string;
  fileName: string;
  status: "completed" | "processing" | "failed";
  records: number;
  startedAt: string;
};

export type WorkspaceDocument = {
  id: string;
  name: string;
  type: string;
  status: "indexed" | "processing" | "failed";
  chunks: number;
  updatedAt: string;
};

export type WorkspaceIntegration = {
  id: string;
  name: string;
  status: "connected" | "syncing" | "error";
  lastSync: string;
};

export type AiActivity = {
  id: string;
  summary: string;
  channel: string;
  confidence: number;
  occurredAt: string;
};

export type ClientWorkspaceData = {
  clientId: string;
  onboarding: OnboardingStep[];
  ingestionJobs: IngestionJob[];
  documents: WorkspaceDocument[];
  integrations: WorkspaceIntegration[];
  aiActivity: AiActivity[];
};
