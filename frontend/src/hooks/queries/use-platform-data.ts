"use client";
import { useQuery } from "@tanstack/react-query";
import { queryKeys } from "@/hooks/queries/query-keys";
import { getAssistantCase } from "@/services/assistant";
import { listIntegrations } from "@/services/integrations";
import { getMonitoringSnapshot } from "@/services/monitoring";
export function useAssistantCase(clientId: string) { return useQuery({ queryKey: queryKeys.assistant(clientId), queryFn: () => getAssistantCase(clientId), enabled: Boolean(clientId) }); }
export function useIntegrations() { return useQuery({ queryKey: queryKeys.integrations, queryFn: () => listIntegrations() }); }
export function useMonitoring() { return useQuery({ queryKey: queryKeys.monitoring, queryFn: () => getMonitoringSnapshot() }); }
