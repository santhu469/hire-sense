"use client";

import { createColumnHelper, tableFeatures, useTable } from "@tanstack/react-table";
import { useRouter } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { Candidate, DecisionStatus, ProcessingStatus } from "@/lib/types";

const features = tableFeatures({});
const helper = createColumnHelper<typeof features, Candidate>();

const PROCESSING_VARIANT: Record<ProcessingStatus, "outline" | "secondary" | "default" | "destructive"> = {
  pending: "outline",
  parsing: "secondary",
  evaluating: "secondary",
  completed: "default",
  failed: "destructive",
};

const DECISION_VARIANT: Record<DecisionStatus, "default" | "secondary" | "destructive"> = {
  shortlisted: "default",
  hold: "secondary",
  rejected: "destructive",
};

const columns = helper.columns([
  helper.accessor((row) => row.parsed_profile?.name ?? null, {
    id: "name",
    header: "Candidate",
    cell: (info) => info.getValue() ?? "—",
  }),
  helper.accessor("processing_status", {
    header: "Processing",
    cell: (info) => <Badge variant={PROCESSING_VARIANT[info.getValue()]}>{info.getValue()}</Badge>,
  }),
  helper.accessor((row) => row.latest_evaluation?.overall_score ?? null, {
    id: "overall_score",
    header: "Score",
    cell: (info) => {
      const value = info.getValue();
      return value === null ? "—" : value.toFixed(1);
    },
  }),
  helper.accessor("current_status", {
    header: "Decision",
    cell: (info) => {
      const value = info.getValue();
      return value ? <Badge variant={DECISION_VARIANT[value]}>{value}</Badge> : <span className="text-muted-foreground">—</span>;
    },
  }),
]);

export function CandidateRankingTable({ candidates }: { candidates: Candidate[] }) {
  const router = useRouter();
  const table = useTable({ features, columns, data: candidates });

  return (
    <Table>
      <TableHeader>
        {table.getHeaderGroups().map((group) => (
          <TableRow key={group.id}>
            {group.headers.map((header) => (
              <TableHead key={header.id}>
                {header.isPlaceholder ? null : <table.FlexRender header={header} />}
              </TableHead>
            ))}
          </TableRow>
        ))}
      </TableHeader>
      <TableBody>
        {table.getRowModel().rows.map((row) => (
          <TableRow
            key={row.id}
            className="cursor-pointer"
            onClick={() => router.push(`/candidates/${row.original.id}`)}
          >
            {row.getAllCells().map((cell) => (
              <TableCell key={cell.id}>
                <table.FlexRender cell={cell} />
              </TableCell>
            ))}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
