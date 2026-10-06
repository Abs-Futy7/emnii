"use client";

import { Activity, Bot, CircleAlert, Gauge, Server, TriangleAlert } from "lucide-react";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { PageHeader } from "@/components/layout/page-header";
import { StatCard } from "@/components/dashboard/stat-card";
import { StatusBadge } from "@/components/dashboard/status-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { monitoringSnapshot } from "@/data/mock-monitoring";
import type { Status } from "@/components/dashboard/status-badge";

const metricIcons = [Server, Gauge, CircleAlert, Bot, TriangleAlert, Activity];
const healthStatus: Record<"Healthy" | "Degraded" | "Down", Status> = { Healthy: "active", Degraded: "warning", Down: "critical" };
const chartTooltipStyle = { borderRadius: "10px", border: "1px solid var(--border)", background: "var(--popover)", color: "var(--popover-foreground)", fontSize: "12px" };

function ChartCard({ title, description, children }: { title: string; description: string; children: React.ReactNode }) {
  return <Card className="min-w-0"><CardHeader><CardTitle>{title}</CardTitle><p className="text-sm text-muted-foreground">{description}</p></CardHeader><CardContent className="h-72 pl-1 sm:pl-3">{children}</CardContent></Card>;
}

export function MonitoringDashboard() {
  return (
    <div className="page-container space-y-6">
      <PageHeader title="Monitoring" description="Observe platform traffic, AI usage, service health, and operational failures." />
      <section aria-label="Monitoring key performance indicators" className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {monitoringSnapshot.metrics.map((metric, index) => {
          const Icon = metricIcons[index];
          return <StatCard key={metric.label} title={metric.label} value={metric.value} description={`${metric.change} · ${metric.description}`} icon={Icon} />;
        })}
      </section>
      <section aria-label="Monitoring charts" className="grid gap-4 xl:grid-cols-2">
        <ChartCard title="API requests over time" description="Aggregate requests across the last 24 hours.">
          <ResponsiveContainer width="100%" height="100%"><AreaChart data={monitoringSnapshot.apiRequests} margin={{ top: 8, right: 16, left: 0 }}>
            <defs><linearGradient id="apiFill" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="var(--primary)" stopOpacity={0.3}/><stop offset="95%" stopColor="var(--primary)" stopOpacity={0}/></linearGradient></defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)"/><XAxis dataKey="time" tickLine={false} axisLine={false} fontSize={12}/><YAxis tickLine={false} axisLine={false} fontSize={12} width={44} tickFormatter={(value: number) => `${Math.round(value / 1000)}k`}/><Tooltip contentStyle={chartTooltipStyle}/><Area type="monotone" dataKey="requests" stroke="var(--primary)" fill="url(#apiFill)" strokeWidth={2}/>
          </AreaChart></ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Latency over time" description="P50 and P95 response latency in milliseconds.">
          <ResponsiveContainer width="100%" height="100%"><LineChart data={monitoringSnapshot.latency} margin={{ top: 8, right: 16, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)"/><XAxis dataKey="time" tickLine={false} axisLine={false} fontSize={12}/><YAxis tickLine={false} axisLine={false} fontSize={12} width={42} unit="ms"/><Tooltip contentStyle={chartTooltipStyle}/><Legend/><Line type="monotone" dataKey="p50" stroke="var(--primary)" strokeWidth={2} dot={false}/><Line type="monotone" dataKey="p95" stroke="var(--chart-3)" strokeWidth={2} dot={false}/>
          </LineChart></ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Tool call outcomes" description="Successful and failed integration tool calls.">
          <ResponsiveContainer width="100%" height="100%"><BarChart data={monitoringSnapshot.toolCalls} margin={{ top: 8, right: 16, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)"/><XAxis dataKey="time" tickLine={false} axisLine={false} fontSize={12}/><YAxis tickLine={false} axisLine={false} fontSize={12} width={42} tickFormatter={(value: number) => `${Math.round(value / 1000)}k`}/><Tooltip contentStyle={chartTooltipStyle}/><Legend/><Bar dataKey="successful" stackId="calls" fill="var(--chart-2)"/><Bar dataKey="failed" stackId="calls" fill="var(--destructive)"/>
          </BarChart></ResponsiveContainer>
        </ChartCard>
        <ChartCard title="AI request usage" description="Daily copilot requests and token consumption.">
          <ResponsiveContainer width="100%" height="100%"><AreaChart data={monitoringSnapshot.aiUsage} margin={{ top: 8, right: 16, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)"/><XAxis dataKey="time" tickLine={false} axisLine={false} fontSize={12}/><YAxis yAxisId="left" tickLine={false} axisLine={false} fontSize={12} width={42} tickFormatter={(value: number) => `${Math.round(value / 1000)}k`}/><YAxis yAxisId="right" orientation="right" tickLine={false} axisLine={false} fontSize={12} width={42} unit="M"/><Tooltip contentStyle={chartTooltipStyle}/><Legend/><Area yAxisId="left" type="monotone" dataKey="requests" stroke="var(--primary)" fill="var(--primary)" fillOpacity={0.12} strokeWidth={2}/><Line yAxisId="right" type="monotone" dataKey="tokens" stroke="var(--chart-3)" strokeWidth={2} dot={false}/>
          </AreaChart></ResponsiveContainer>
        </ChartCard>
      </section>
      <Card><CardHeader><CardTitle>Service health</CardTitle><p className="text-sm text-muted-foreground">Current availability and performance across critical dependencies.</p></CardHeader><CardContent className="p-0"><div className="overflow-x-auto"><Table>
        <TableHeader><TableRow><TableHead>Service</TableHead><TableHead>Status</TableHead><TableHead>Uptime</TableHead><TableHead>Latency</TableHead><TableHead>Error Rate</TableHead><TableHead>Last Check</TableHead></TableRow></TableHeader>
        <TableBody>{monitoringSnapshot.services.map((service) => <TableRow key={service.id}><TableCell className="font-medium">{service.name}</TableCell><TableCell><StatusBadge status={healthStatus[service.status]} label={service.status}/></TableCell><TableCell>{service.uptime}</TableCell><TableCell>{service.latency}</TableCell><TableCell>{service.errorRate}</TableCell><TableCell className="text-muted-foreground">{service.lastCheck}</TableCell></TableRow>)}</TableBody>
      </Table></div></CardContent></Card>
    </div>
  );
}
