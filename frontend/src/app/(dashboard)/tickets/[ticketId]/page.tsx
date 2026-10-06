import { notFound } from "next/navigation";
import { TicketDetail } from "@/components/tickets/ticket-detail";
import { getTicketById, supportTickets } from "@/data/mock-tickets";

export function generateStaticParams() { return supportTickets.map((ticket) => ({ ticketId: ticket.id })); }

export default async function TicketDetailPage({ params }: { params: Promise<{ ticketId: string }> }) {
  const { ticketId } = await params;
  const ticket = getTicketById(ticketId);
  if (!ticket) notFound();
  return <TicketDetail ticket={ticket}/>;
}
