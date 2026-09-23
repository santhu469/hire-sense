"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRef, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { ApiError, uploadCandidate } from "@/lib/api";

export function CandidateUpload({ jdId }: { jdId: string }) {
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [fileName, setFileName] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: (file: File) => uploadCandidate(jdId, file),
    onSuccess: () => {
      toast.success("Resume uploaded — evaluation started");
      setFileName(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
      queryClient.invalidateQueries({ queryKey: ["candidates", jdId] });
    },
    onError: (err) => {
      toast.error(err instanceof ApiError ? err.message : "Upload failed");
    },
  });

  return (
    <div className="flex items-center gap-3">
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        className="text-sm"
        onChange={(e) => setFileName(e.target.files?.[0]?.name ?? null)}
      />
      <Button
        disabled={!fileName || mutation.isPending}
        onClick={() => {
          const file = fileInputRef.current?.files?.[0];
          if (file) mutation.mutate(file);
        }}
      >
        {mutation.isPending ? "Uploading…" : "Upload resume"}
      </Button>
    </div>
  );
}
