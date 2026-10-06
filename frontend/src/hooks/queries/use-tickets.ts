"use client";
import { useQuery } from "@tanstack/react-query";
import { queryKeys } from "@/hooks/queries/query-keys";
import { getTicket, listTickets } from "@/services/tickets";
export function useTickets() { return useQuery({ queryKey: queryKeys.tickets.all, queryFn: () => listTickets() }); }
export function useTicket(ticketId: string) { return useQuery({ queryKey: queryKeys.tickets.detail(ticketId), queryFn: () => getTicket(ticketId), enabled: Boolean(ticketId) }); }
