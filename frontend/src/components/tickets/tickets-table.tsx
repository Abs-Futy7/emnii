"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { Search, Tickets } from "lucide-react";
import { EmptyState } from "@/components/layout/empty-state";
import { TicketPriorityBadge, TicketStatusBadge } from "@/components/tickets/ticket-badges";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { SupportTicket, TicketPriority, TicketStatus } from "@/types/support-ticket";

export function TicketsTable({ tickets }: { tickets: SupportTicket[] }) {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<TicketStatus | "all">("all");
  const [priority, setPriority] = useState<TicketPriority | "all">("all");
  const filtered = useMemo(() => {
    const search = query.trim().toLowerCase();
    return tickets.filter((ticket) => (!search || `${ticket.id} ${ticket.customer.name} ${ticket.subject}`.toLowerCase().includes(search)) && (status === "all" || ticket.status === status) && (priority === "all" || ticket.priority === priority));
  }, [priority, query, status, tickets]);
  const reset = () => { setQuery(""); setStatus("all"); setPriority("all"); };

  return <Card><CardHeader className="border-b"><div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
    <div className="relative w-full lg:max-w-sm"><Search className="pointer-events-none absolute left-2.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" aria-hidden="true"/><Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search tickets, customers, or subjects…" aria-label="Search tickets" className="pl-8"/></div>
    <div className="flex flex-col gap-2 sm:flex-row">
      <Select value={status} onValueChange={(value) => setStatus((value ?? "all") as TicketStatus | "all")}><SelectTrigger className="w-full sm:w-40" aria-label="Filter by status"><SelectValue/></SelectTrigger><SelectContent align="start"><SelectItem value="all">All statuses</SelectItem>{(["Open", "In Progress", "Waiting", "Resolved"] as TicketStatus[]).map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent></Select>
      <Select value={priority} onValueChange={(value) => setPriority((value ?? "all") as TicketPriority | "all")}><SelectTrigger className="w-full sm:w-40" aria-label="Filter by priority"><SelectValue/></SelectTrigger><SelectContent align="start"><SelectItem value="all">All priorities</SelectItem>{(["Low", "Medium", "High", "Urgent"] as TicketPriority[]).map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent></Select>
    </div>
  </div><p className="text-xs text-muted-foreground" aria-live="polite">Showing {filtered.length} of {tickets.length} tickets</p></CardHeader>
  <CardContent className="px-0">{filtered.length ? <div className="overflow-x-auto"><Table className="min-w-[1100px]"><TableHeader><TableRow><TableHead className="pl-4">Ticket ID</TableHead><TableHead>Customer</TableHead><TableHead>Subject</TableHead><TableHead>Priority</TableHead><TableHead>Status</TableHead><TableHead>Assigned Agent</TableHead><TableHead>AI Recommendation</TableHead><TableHead>Created At</TableHead></TableRow></TableHeader><TableBody>
    {filtered.map((ticket) => <TableRow key={ticket.id}><TableCell className="pl-4"><Link href={`/tickets/${ticket.id}`} className="font-mono text-xs font-semibold text-primary hover:underline">{ticket.id}</Link></TableCell><TableCell><p className="font-medium">{ticket.customer.name}</p><p className="text-xs text-muted-foreground">{ticket.customer.email}</p></TableCell><TableCell><Link href={`/tickets/${ticket.id}`} className="font-medium hover:text-primary hover:underline">{ticket.subject}</Link></TableCell><TableCell><TicketPriorityBadge priority={ticket.priority}/></TableCell><TableCell><TicketStatusBadge status={ticket.status}/></TableCell><TableCell>{ticket.assignedAgent}</TableCell><TableCell className="max-w-60 truncate text-muted-foreground">{ticket.aiRecommendation}</TableCell><TableCell className="whitespace-nowrap text-muted-foreground">{ticket.createdAt}</TableCell></TableRow>)}
  </TableBody></Table></div> : <div className="p-6"><EmptyState title="No tickets found" description="Adjust the search or filters to see more support requests." icon={Tickets} action={<Button variant="outline" onClick={reset}>Clear filters</Button>}/></div>}</CardContent></Card>;
}
