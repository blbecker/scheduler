"use client";

import {
  Alert,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
} from "@mui/material";
import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useState, useMemo } from "react";
import { useGetScheduleTemplate, useUpdateScheduleTemplate } from "@/api/client/schedule-templates/schedule-templates";
import type { ScheduleTemplateUpdate } from "@/api/models";

interface EditScheduleTemplateFormProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  scheduleTemplateId: string;
}

export function EditScheduleTemplateForm({
  open,
  onClose,
  onSuccess,
  scheduleTemplateId,
}: EditScheduleTemplateFormProps) {
  const queryClient = useQueryClient();

  const [name, setName] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});

  const updateMutation = useUpdateScheduleTemplate();

  const { data: scheduleTemplateData, isLoading: isLoadingScheduleTemplate } = useGetScheduleTemplate(
    scheduleTemplateId,
    { query: { enabled: Boolean(open && scheduleTemplateId) } },
  );

  useEffect(() => {
    if (scheduleTemplateData?.data && "name" in scheduleTemplateData.data) {
      setName(scheduleTemplateData.data.name);
    }
  }, [scheduleTemplateData]);

  useEffect(() => {
    if (open) {
      setErrors({});
    }
  }, [open]);

  const validate = () => {
    const newErrors: Record<string, string> = {};

    if (!name.trim()) {
      newErrors.name = "Name is required";
    } else if (name.length > 52) {
      newErrors.name = "Name must be 52 characters or less";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    try {
      const updateData: ScheduleTemplateUpdate = { name };
      await updateMutation.mutateAsync({
        scheduleTemplateId,
        data: updateData,
      });

      queryClient.invalidateQueries({ queryKey: ["/api/v1/schedule-templates/"] });
      queryClient.invalidateQueries({
        queryKey: [`/api/v1/schedule-templates/${scheduleTemplateId}`],
      });

      onSuccess?.();
      onClose();
    } catch (error) {
      console.error("Failed to update schedule template:", error);
      setErrors({
        submit: "Failed to update schedule template. Please try again.",
      });
    }
  };

  const isLoading = updateMutation.isPending || isLoadingScheduleTemplate;
  const submitError = errors.submit || "";

  const mutationErrorMessage = useMemo(() => {
    if (!updateMutation.error) return "";

    const err = updateMutation.error;
    if (err instanceof Error) return err.message;
    if (typeof err === "object" && err !== null && "message" in err) {
      return String((err as { message: string }).message);
    }
    return String(err);
  }, [updateMutation.error]);

  const displayError = submitError || mutationErrorMessage;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>Edit Schedule Template</DialogTitle>

        <DialogContent>
          {displayError ? (
            <Alert severity="error" sx={{ mb: 2 }}>
              {displayError}
            </Alert>
          ) : null}

          <TextField
            autoFocus
            margin="dense"
            label="Schedule Template Name"
            fullWidth
            value={name}
            onChange={(e) => setName(e.target.value)}
            error={!!errors.name}
            helperText={errors.name}
            disabled={isLoading}
            sx={{ mt: 2 }}
            placeholder="e.g., Weekly Schedule, Monthly Rotation"
          />
        </DialogContent>

        <DialogActions>
          <Button onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button type="submit" variant="contained" disabled={isLoading}>
            {isLoading ? <CircularProgress size={24} /> : "Update Schedule Template"}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}