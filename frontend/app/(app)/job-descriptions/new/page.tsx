"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import * as api from "@/lib/api";
import { ApiError } from "@/lib/api";

const schema = z.object({
  title: z.string().min(1, "Title is required").max(255),
  raw_text: z.string().min(1, "Job description text is required"),
});

type FormValues = z.infer<typeof schema>;

export default function NewJobDescriptionPage() {
  const router = useRouter();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const mutation = useMutation({
    mutationFn: (values: FormValues) => api.createJobDescription(values.title, values.raw_text),
    onSuccess: (jd) => {
      toast.success("Job description created");
      router.push(`/job-descriptions/${jd.id}`);
    },
    onError: (err) => {
      toast.error(err instanceof ApiError ? err.message : "Failed to create job description");
    },
  });

  return (
    <div className="mx-auto flex w-full max-w-2xl flex-col gap-6">
      <h1 className="text-2xl font-semibold">New job description</h1>
      <form
        onSubmit={handleSubmit((values) => mutation.mutate(values))}
        className="flex flex-col gap-4"
      >
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="title">Title</Label>
          <Input id="title" {...register("title")} />
          {errors.title && <p className="text-sm text-destructive">{errors.title.message}</p>}
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="raw_text">Job description</Label>
          <Textarea id="raw_text" rows={12} {...register("raw_text")} />
          {errors.raw_text && <p className="text-sm text-destructive">{errors.raw_text.message}</p>}
          <p className="text-xs text-muted-foreground">
            A default weighted rubric (Skills Match, Domain Experience, Education &amp; Certifications, Overall
            Fit) is seeded automatically and can be tuned in a later phase.
          </p>
        </div>
        <Button type="submit" disabled={mutation.isPending} className="self-start">
          {mutation.isPending ? "Creating…" : "Create job description"}
        </Button>
      </form>
    </div>
  );
}
