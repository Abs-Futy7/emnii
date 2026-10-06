"use client";
import { useQuery } from "@tanstack/react-query";
import { queryKeys } from "@/hooks/queries/query-keys";
import { listDatasets } from "@/services/datasets";
export function useDatasets(clientId: string) { return useQuery({ queryKey: queryKeys.datasets(clientId), queryFn: () => listDatasets(clientId), enabled: Boolean(clientId) }); }
