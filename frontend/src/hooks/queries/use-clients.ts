"use client";
import { useQuery } from "@tanstack/react-query";
import { queryKeys } from "@/hooks/queries/query-keys";
import { getClient, listClients } from "@/services/clients";
export function useClients() { return useQuery({ queryKey: queryKeys.clients.all, queryFn: () => listClients() }); }
export function useClient(clientId: string) { return useQuery({ queryKey: queryKeys.clients.detail(clientId), queryFn: () => getClient(clientId), enabled: Boolean(clientId) }); }
