import { PageHeader } from "@/components/layout/page-header";
import { TicketsTable } from "@/components/tickets/tickets-table";
import { supportTickets } from "@/data/mock-tickets";

export default function TicketsPage() {
  return <div className="page-container space-y-6"><PageHeader title="Tickets" description="Review, prioritize, and coordinate customer support work across the organization."/><TicketsTable tickets={supportTickets}/></div>;
}
