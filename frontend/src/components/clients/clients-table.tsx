"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { Building2, Eye, MoreHorizontal, Search, Settings2 } from "lucide-react";

import { ClientStatusBadge } from "@/components/clients/client-status-badge";
import { DataQualityScore } from "@/components/clients/data-quality-score";
import { EmptyState } from "@/components/layout/empty-state";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { Client, ClientStatus } from "@/types/client";
import { formatCompactNumber } from "@/lib/formatters";

const statusOptions: Array<{ value: ClientStatus | "all"; label: string }> = [
  { value: "all", label: "All statuses" },
  { value: "onboarding", label: "Onboarding" },
  { value: "active", label: "Active" },
  { value: "needs-attention", label: "Needs Attention" },
  { value: "disabled", label: "Disabled" },
];

type ClientsTableProps = {
  clients: Client[];
  industries: string[];
};

export function ClientsTable({ clients, industries }: ClientsTableProps) {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<ClientStatus | "all">("all");
  const [industry, setIndustry] = useState("all");

  const filteredClients = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();

    return clients.filter((client) => {
      const matchesQuery =
        !normalizedQuery ||
        client.company.toLowerCase().includes(normalizedQuery) ||
        client.industry.toLowerCase().includes(normalizedQuery);
      const matchesStatus = status === "all" || client.status === status;
      const matchesIndustry = industry === "all" || client.industry === industry;

      return matchesQuery && matchesStatus && matchesIndustry;
    });
  }, [clients, industry, query, status]);

  const resetFilters = () => {
    setQuery("");
    setStatus("all");
    setIndustry("all");
  };

  return (
    <Card>
      <CardHeader className="border-b">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div className="relative w-full lg:max-w-sm">
            <Search
              className="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground"
              aria-hidden="true"
            />
            <Input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search clients or industries…"
              aria-label="Search clients"
              className="pl-8"
            />
          </div>
          <div className="flex flex-col gap-2 sm:flex-row">
            <Select
              value={status}
              onValueChange={(value) => setStatus(value as ClientStatus | "all")}
            >
              <SelectTrigger className="w-full sm:w-44" aria-label="Filter by status">
                <SelectValue />
              </SelectTrigger>
              <SelectContent align="start">
                {statusOptions.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={industry} onValueChange={(value) => setIndustry(value ?? "all")}>
              <SelectTrigger className="w-full sm:w-52" aria-label="Filter by industry">
                <SelectValue />
              </SelectTrigger>
              <SelectContent align="start">
                <SelectItem value="all">All industries</SelectItem>
                {industries.map((item) => (
                  <SelectItem key={item} value={item}>
                    {item}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
        <p className="text-xs text-muted-foreground" aria-live="polite">
          Showing {filteredClients.length} of {clients.length} clients
        </p>
      </CardHeader>

      <CardContent className="px-0">
        {filteredClients.length ? (
          <Table className="min-w-[1120px]">
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <TableHead className="pl-4">Company</TableHead>
                <TableHead>Industry</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Records</TableHead>
                <TableHead className="text-right">Documents</TableHead>
                <TableHead>Data Quality</TableHead>
                <TableHead>Integrations</TableHead>
                <TableHead>Last Activity</TableHead>
                <TableHead className="pr-4 text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredClients.map((client) => (
                <TableRow key={client.id}>
                  <TableCell className="pl-4">
                    <Link
                      href={`/clients/${client.id}`}
                      className="flex items-center gap-2.5 font-medium hover:text-primary focus-visible:rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                      <span className="flex size-8 items-center justify-center rounded-lg border bg-muted text-xs font-semibold text-muted-foreground">
                        {client.company.slice(0, 2).toUpperCase()}
                      </span>
                      {client.company}
                    </Link>
                  </TableCell>
                  <TableCell className="text-muted-foreground">{client.industry}</TableCell>
                  <TableCell><ClientStatusBadge status={client.status} /></TableCell>
                  <TableCell className="text-right tabular-nums">{formatCompactNumber(client.records)}</TableCell>
                  <TableCell className="text-right tabular-nums">{client.documents}</TableCell>
                  <TableCell><DataQualityScore score={client.dataQualityScore} /></TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1.5">
                      {client.integrations.slice(0, 2).map((integration) => (
                        <Badge key={integration} variant="secondary" className="font-normal">
                          {integration}
                        </Badge>
                      ))}
                      {client.integrations.length > 2 ? (
                        <span className="text-xs text-muted-foreground">+{client.integrations.length - 2}</span>
                      ) : null}
                    </div>
                  </TableCell>
                  <TableCell className="text-muted-foreground">{client.lastActivity}</TableCell>
                  <TableCell className="pr-4 text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger
                        render={
                          <Button
                            variant="ghost"
                            size="icon-sm"
                            aria-label={`Actions for ${client.company}`}
                          >
                            <MoreHorizontal aria-hidden="true" />
                          </Button>
                        }
                      />
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem render={<Link href={`/clients/${client.id}`} />}>
                          <Eye aria-hidden="true" />
                          View client
                        </DropdownMenuItem>
                        <DropdownMenuItem disabled>
                          <Settings2 aria-hidden="true" />
                          Configure
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem disabled>Disable client</DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        ) : (
          <EmptyState
            icon={Building2}
            title="No clients found"
            description="Try changing your search or filters to find the organization you need."
            action={
              <Button variant="outline" onClick={resetFilters}>
                Clear filters
              </Button>
            }
            className="m-4 min-h-64"
          />
        )}
      </CardContent>
    </Card>
  );
}
