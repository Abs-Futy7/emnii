"use client";

import { useState } from "react";
import {
  AlertTriangle,
  Bot,
  Check,
  CheckCircle2,
  ChevronRight,
  ClipboardCheck,
  DatabaseZap,
  ExternalLink,
  PackageSearch,
  Pencil,
  ShieldAlert,
  UserRound,
} from "lucide-react";

import { WorkspacePageHeader } from "@/components/clients/workspace-page-header";
import { StatusBadge } from "@/components/dashboard/status-badge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import type {
  AssistantSource,
  SupportAssistantCase,
} from "@/types/support-assistant";

type ReviewState = "pending" | "approved" | "escalated";

export function AssistantWorkspace({ supportCase }: { supportCase: SupportAssistantCase }) {
  const [reviewState, setReviewState] = useState<ReviewState>("pending");
  const [isEditing, setIsEditing] = useState(false);
  const [response, setResponse] = useState(supportCase.suggestedResponse);
  const [activeSource, setActiveSource] = useState<AssistantSource>(supportCase.sources[0]);

  return (
    <div className="space-y-6">
      <WorkspacePageHeader
        title="Support Copilot"
        description="Review evidence-backed AI recommendations before anything is sent to the customer."
        actions={
          reviewState === "approved" ? (
            <StatusBadge status="active" label="Response Approved" />
          ) : reviewState === "escalated" ? (
            <StatusBadge status="warning" label="Escalated to Human" />
          ) : (
            <StatusBadge status="pending" label="Awaiting Review" />
          )
        }
      />

      <div className="grid items-start gap-4 xl:grid-cols-[minmax(0,1fr)_340px]">
        <div className="space-y-4">
          <Card>
            <CardHeader className="border-b">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-xs font-medium tracking-wide text-muted-foreground uppercase">Active case</p>
                  <CardTitle className="mt-1">{supportCase.caseId}</CardTitle>
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Badge variant="outline">Email</Badge>
                  <Badge variant="outline">Delivery issue</Badge>
                  <Badge variant="secondary">High priority</Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-5">
              <section aria-labelledby="customer-request-heading" className="rounded-xl border bg-muted/25 p-4">
                <div className="flex items-center gap-2 text-sm font-medium">
                  <UserRound className="size-4 text-muted-foreground" aria-hidden="true" />
                  <h3 id="customer-request-heading">Customer request</h3>
                </div>
                <blockquote className="mt-3 border-l-2 border-primary pl-4 text-base leading-7">
                  “{supportCase.customerMessage}”
                </blockquote>
              </section>

              <section aria-labelledby="tool-activity-heading">
                <div className="mb-3 flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2"><DatabaseZap className="size-4 text-primary" aria-hidden="true" /><h3 id="tool-activity-heading" className="text-sm font-semibold">Tool Activity</h3></div>
                  <span className="text-xs text-muted-foreground">4 tools completed</span>
                </div>
                <div className="grid gap-2 sm:grid-cols-2">
                  {supportCase.tools.map((tool) => (
                    <div key={tool.id} className="flex items-center gap-3 rounded-lg border p-3">
                      <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"><Check className="size-3.5" aria-hidden="true" /></span>
                      <div className="min-w-0 flex-1"><p className="text-sm font-medium">{tool.label}</p><p className="truncate text-xs text-muted-foreground">{tool.result}</p></div>
                      <span className="text-[11px] text-muted-foreground tabular-nums">{tool.duration}</span>
                    </div>
                  ))}
                </div>
              </section>
            </CardContent>
          </Card>

          <Card className="ring-primary/20">
            <CardHeader className="border-b bg-primary/[0.03]">
              <div className="flex items-center gap-3">
                <span className="flex size-9 items-center justify-center rounded-lg bg-primary text-primary-foreground"><Bot className="size-4" aria-hidden="true" /></span>
                <div><CardTitle>AI Recommendation Draft</CardTitle><p className="mt-0.5 text-xs text-muted-foreground">Generated from approved client data and policy sources</p></div>
              </div>
            </CardHeader>
            <CardContent className="space-y-5">
              <div className="grid gap-4 lg:grid-cols-2">
                <section className="rounded-lg border p-4">
                  <p className="text-xs font-semibold tracking-wide text-muted-foreground uppercase">Issue Summary</p>
                  <p className="mt-2 text-sm leading-6">{supportCase.issueSummary}</p>
                </section>
                <section className="rounded-lg border p-4">
                  <p className="text-xs font-semibold tracking-wide text-muted-foreground uppercase">Recommended Action</p>
                  <p className="mt-2 text-sm leading-6">{supportCase.recommendedAction}</p>
                </section>
              </div>

              <section>
                <p className="text-xs font-semibold tracking-wide text-muted-foreground uppercase">Context Gathered</p>
                <ul className="mt-2 grid gap-2 sm:grid-cols-2">
                  {supportCase.contextGathered.map((item) => (
                    <li key={item} className="flex items-center gap-2 text-sm"><CheckCircle2 className="size-4 text-emerald-600 dark:text-emerald-400" aria-hidden="true" />{item}</li>
                  ))}
                </ul>
              </section>

              <section>
                <div className="mb-2 flex items-center justify-between gap-3">
                  <p className="text-xs font-semibold tracking-wide text-muted-foreground uppercase">Suggested Response</p>
                  {isEditing ? <Badge variant="secondary">Editing draft</Badge> : null}
                </div>
                {isEditing ? (
                  <Textarea value={response} onChange={(event) => setResponse(event.target.value)} rows={7} aria-label="Edit suggested response" />
                ) : (
                  <div className="rounded-lg border bg-background p-4 text-sm leading-7">{response}</div>
                )}
              </section>

              <section>
                <p className="text-xs font-semibold tracking-wide text-muted-foreground uppercase">Sources</p>
                <div className="mt-2 grid gap-2 sm:grid-cols-2">
                  {supportCase.sources.map((source) => (
                    <button
                      key={source.id}
                      type="button"
                      onClick={() => setActiveSource(source)}
                      className={cn(
                        "group rounded-lg border p-3 text-left outline-none transition-colors hover:bg-muted/50 focus-visible:ring-2 focus-visible:ring-ring",
                        activeSource.id === source.id && "border-primary/40 bg-primary/5",
                      )}
                    >
                      <div className="flex items-start justify-between gap-3"><div><p className="text-sm font-medium">{source.title}</p><p className="mt-0.5 text-xs text-muted-foreground">{source.type}</p></div><ChevronRight className="size-4 text-muted-foreground transition-transform group-hover:translate-x-0.5" aria-hidden="true" /></div>
                    </button>
                  ))}
                </div>
              </section>
            </CardContent>
            <div className="flex flex-col gap-2 border-t bg-muted/30 p-4 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-xs text-muted-foreground">A human reviewer must approve this response before delivery.</p>
              <div className="flex flex-wrap gap-2">
                <Button type="button" variant="outline" onClick={() => setIsEditing((value) => !value)}><Pencil data-icon="inline-start" aria-hidden="true" />{isEditing ? "Finish Editing" : "Edit Response"}</Button>
                <Button type="button" variant="outline" onClick={() => setReviewState("escalated")}><ShieldAlert data-icon="inline-start" aria-hidden="true" />Escalate</Button>
                <Button type="button" onClick={() => setReviewState("approved")}><ClipboardCheck data-icon="inline-start" aria-hidden="true" />Approve Response</Button>
              </div>
            </div>
          </Card>
        </div>

        <aside className="space-y-4 xl:sticky xl:top-20" aria-label="Customer and case context">
          <Card>
            <CardHeader className="border-b"><CardTitle>Customer Context</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3"><span className="flex size-10 items-center justify-center rounded-full bg-primary/10 font-semibold text-primary">NR</span><div className="min-w-0"><p className="font-medium">{supportCase.customer.name}</p><p className="truncate text-xs text-muted-foreground">{supportCase.customer.email}</p></div></div>
              <dl className="grid grid-cols-2 gap-3 rounded-lg bg-muted/30 p-3">
                <div><dt className="text-xs text-muted-foreground">Customer tier</dt><dd className="mt-0.5 text-sm font-medium">{supportCase.customer.tier}</dd></div>
                <div><dt className="text-xs text-muted-foreground">Lifetime value</dt><dd className="mt-0.5 text-sm font-medium">{supportCase.customer.lifetimeValue}</dd></div>
                <div><dt className="text-xs text-muted-foreground">Open tickets</dt><dd className="mt-0.5 text-sm font-medium">{supportCase.customer.openTickets}</dd></div>
                <div><dt className="text-xs text-muted-foreground">Sentiment</dt><dd className="mt-0.5 text-sm font-medium text-amber-600 dark:text-amber-400">Frustrated</dd></div>
              </dl>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="border-b"><div className="flex items-center gap-2"><PackageSearch className="size-4 text-primary" aria-hidden="true" /><CardTitle>Order #{supportCase.order.id}</CardTitle></div></CardHeader>
            <CardContent><dl className="space-y-3"><div className="flex justify-between gap-3"><dt className="text-muted-foreground">Status</dt><dd><StatusBadge status="warning" label={supportCase.order.status} /></dd></div><div className="flex justify-between gap-3"><dt className="text-muted-foreground">Carrier</dt><dd className="font-medium">{supportCase.order.carrier}</dd></div><div className="flex justify-between gap-3"><dt className="text-muted-foreground">Expected</dt><dd className="font-medium">{supportCase.order.expectedDelivery}</dd></div><div className="flex justify-between gap-3"><dt className="text-muted-foreground">Order value</dt><dd className="font-medium">{supportCase.order.value}</dd></div></dl></CardContent>
          </Card>

          <Card className="ring-primary/20">
            <CardHeader className="border-b"><div className="flex items-center justify-between gap-2"><CardTitle>Selected Source</CardTitle><ExternalLink className="size-3.5 text-muted-foreground" aria-hidden="true" /></div></CardHeader>
            <CardContent><Badge variant="outline">{activeSource.type}</Badge><p className="mt-3 font-medium">{activeSource.title}</p><p className="mt-2 text-sm leading-6 text-muted-foreground">{activeSource.detail}</p><p className="mt-3 text-xs text-muted-foreground">Updated {activeSource.updatedAt}</p></CardContent>
          </Card>

          <div className="flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs leading-5 text-amber-800 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-200"><AlertTriangle className="mt-0.5 size-3.5 shrink-0" aria-hidden="true" />AI output may contain errors. Verify policy and customer context before approval.</div>
        </aside>
      </div>
    </div>
  );
}
