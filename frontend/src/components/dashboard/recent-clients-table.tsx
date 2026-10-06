import Link from "next/link";

import { ClientStatusBadge } from "@/components/clients/client-status-badge";
import { DataQualityScore } from "@/components/clients/data-quality-score";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { Client } from "@/types/client";
import { formatCompactNumber } from "@/lib/formatters";

export function RecentClientsTable({ clients }: { clients: Client[] }) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between border-b">
        <CardTitle>Recent Clients</CardTitle>
        <Link
          href="/clients"
          className="text-sm font-medium text-primary hover:underline focus-visible:rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          View all
        </Link>
      </CardHeader>
      <CardContent className="px-0">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead className="pl-4">Company</TableHead>
              <TableHead>Industry</TableHead>
              <TableHead>Onboarding status</TableHead>
              <TableHead className="text-right">Records</TableHead>
              <TableHead className="text-right">Documents</TableHead>
              <TableHead className="pr-4">Data quality</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {clients.map((client) => (
              <TableRow key={client.id}>
                <TableCell className="pl-4 font-medium">
                  <Link
                    href={`/clients/${client.id}`}
                    className="hover:text-primary hover:underline focus-visible:rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  >
                    {client.company}
                  </Link>
                </TableCell>
                <TableCell className="text-muted-foreground">{client.industry}</TableCell>
                <TableCell><ClientStatusBadge status={client.status} /></TableCell>
                <TableCell className="text-right tabular-nums">{formatCompactNumber(client.records)}</TableCell>
                <TableCell className="text-right tabular-nums">{client.documents}</TableCell>
                <TableCell className="pr-4"><DataQualityScore score={client.dataQualityScore} compact /></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
