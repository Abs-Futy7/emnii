import Link from "next/link";
import { ArrowLeft, Bot, ExternalLink, Package, UserRound } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { TicketPriorityBadge, TicketStatusBadge } from "@/components/tickets/ticket-badges";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { SupportTicket } from "@/types/support-ticket";

export function TicketDetail({ ticket }: { ticket: SupportTicket }) {
  return <div className="page-container space-y-6">
    <PageHeader eyebrow={ticket.id} title={ticket.subject} description={`Created ${ticket.createdAt} · Assigned to ${ticket.assignedAgent}`} actions={<><TicketPriorityBadge priority={ticket.priority}/><TicketStatusBadge status={ticket.status}/></>}/>
    <Button variant="ghost" render={<Link href="/tickets"/>}><ArrowLeft data-icon="inline-start"/>Back to tickets</Button>
    <div className="grid items-start gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
      <div className="space-y-4">
        <Card><CardHeader><CardTitle>Conversation</CardTitle></CardHeader><CardContent className="space-y-4">{ticket.conversation.map((message) => <article key={message.id} className="rounded-xl border bg-muted/30 p-4"><div className="mb-2 flex items-center justify-between gap-4"><p className="text-sm font-semibold">{message.author}</p><time className="text-xs text-muted-foreground">{message.createdAt}</time></div><p className="text-sm leading-6 text-muted-foreground">{message.content}</p></article>)}</CardContent></Card>
        <Card className="border-primary/20 bg-primary/[0.025]"><CardHeader><div className="flex items-center gap-2"><Bot className="size-5 text-primary"/><CardTitle>AI recommendation</CardTitle></div></CardHeader><CardContent className="space-y-5"><div><p className="text-sm font-semibold">Recommended action</p><p className="mt-1 text-sm leading-6 text-muted-foreground">{ticket.aiRecommendation}</p></div><div><p className="text-sm font-semibold">Suggested response</p><div className="mt-2 rounded-xl border bg-background p-4 text-sm leading-6">{ticket.suggestedResponse}</div></div><div className="flex flex-wrap gap-2"><Button>Approve response</Button><Button variant="outline">Edit response</Button><Button variant="outline">Escalate</Button></div></CardContent></Card>
        <Card><CardHeader><CardTitle>Source citations</CardTitle></CardHeader><CardContent className="grid gap-3 sm:grid-cols-2">{ticket.sources.map((source) => <button key={source.id} type="button" className="rounded-xl border p-4 text-left transition-colors hover:bg-muted/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"><div className="flex items-start justify-between gap-3"><p className="font-medium">{source.title}</p><ExternalLink className="size-4 text-muted-foreground"/></div><p className="mt-1 text-xs text-muted-foreground">{source.type} · {source.detail}</p></button>)}</CardContent></Card>
      </div>
      <aside className="space-y-4">
        <Card><CardHeader><div className="flex items-center gap-2"><UserRound className="size-4 text-primary"/><CardTitle>Customer</CardTitle></div></CardHeader><CardContent className="space-y-3 text-sm"><div><p className="font-medium">{ticket.customer.name}</p><p className="text-muted-foreground">{ticket.customer.email}</p></div><div className="flex gap-2"><Badge variant="secondary">{ticket.customer.tier}</Badge><Badge variant="outline">{ticket.customer.location}</Badge></div></CardContent></Card>
        <Card><CardHeader><div className="flex items-center gap-2"><Package className="size-4 text-primary"/><CardTitle>Related order</CardTitle></div></CardHeader><CardContent className="grid grid-cols-2 gap-3 text-sm"><span className="text-muted-foreground">Order</span><span className="text-right font-medium">#{ticket.relatedOrder.id}</span><span className="text-muted-foreground">Status</span><span className="text-right">{ticket.relatedOrder.status}</span><span className="text-muted-foreground">Total</span><span className="text-right">{ticket.relatedOrder.total}</span><span className="text-muted-foreground">Method</span><span className="text-right">{ticket.relatedOrder.fulfillment}</span></CardContent></Card>
        <Card><CardHeader><CardTitle>Previous tickets</CardTitle></CardHeader><CardContent className="space-y-3">{ticket.previousTickets.map((previous) => <div key={previous.id} className="rounded-lg border p-3"><div className="flex items-center justify-between"><p className="font-mono text-xs font-semibold">{previous.id}</p><TicketStatusBadge status={previous.status}/></div><p className="mt-2 text-sm">{previous.subject}</p></div>)}</CardContent></Card>
      </aside>
    </div>
  </div>;
}
