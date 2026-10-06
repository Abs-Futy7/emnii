"use client";
import { useQuery } from "@tanstack/react-query";
import { queryKeys } from "@/hooks/queries/query-keys";
import { listDocuments } from "@/services/documents";
export function useDocuments(clientId: string) { return useQuery({ queryKey: queryKeys.documents(clientId), queryFn: () => listDocuments(clientId), enabled: Boolean(clientId) }); }
