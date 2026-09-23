"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { ApiError, changeCandidateStatus } from "@/lib/api";
import type { DecisionStatus } from "@/lib/types";

const OPTIONS: { value: DecisionStatus; label: string }[] = [
  { value: "shortlisted", label: "Shortlist" },
  { value: "hold", label: "Hold" },
  { value: "rejected", label: "Reject" },
];

export function StatusChangeDialog({ candidateId, jdId }: { candidateId: string; jdId: string }) {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState<DecisionStatus>("shortlisted");
  const [reasonNote, setReasonNote] = useState("");

  const mutation = useMutation({
    mutationFn: () => changeCandidateStatus(candidateId, status, reasonNote || null),
    onSuccess: () => {
      toast.success("Status updated");
      setOpen(false);
      setReasonNote("");
      queryClient.invalidateQueries({ queryKey: ["candidate", candidateId] });
      queryClient.invalidateQueries({ queryKey: ["candidates", jdId] });
    },
    onError: (err) => {
      toast.error(err instanceof ApiError ? err.message : "Failed to update status");
    },
  });

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button />}>Change status</DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Change candidate status</DialogTitle>
        </DialogHeader>

        <div className="flex flex-col gap-4">
          <div className="flex gap-2">
            {OPTIONS.map((opt) => (
              <Button
                key={opt.value}
                type="button"
                variant={status === opt.value ? "default" : "outline"}
                size="sm"
                onClick={() => setStatus(opt.value)}
              >
                {opt.label}
              </Button>
            ))}
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="reason_note">Reason (optional)</Label>
            <Textarea
              id="reason_note"
              rows={3}
              value={reasonNote}
              onChange={(e) => setReasonNote(e.target.value)}
            />
          </div>
        </div>

        <DialogFooter>
          <Button disabled={mutation.isPending} onClick={() => mutation.mutate()}>
            {mutation.isPending ? "Saving…" : "Confirm"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
