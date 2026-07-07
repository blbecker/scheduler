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
import { useGetWorker, useUpdateWorker } from "@/api/client/workers/workers";
import type { WorkerUpdate } from "@/api/models";

interface EditWorkerFormProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  workerId: string;
}

export function EditWorkerForm({
  open,
  onClose,
  onSuccess,
  workerId,
}: EditWorkerFormProps) {
  const queryClient = useQueryClient();

  // State
  const [name, setName] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});

  // API hooks
  const updateMutation = useUpdateWorker();

  // Fetch worker data for edit mode
  const { data: workerData, isLoading: isLoadingWorker } = useGetWorker(
    workerId,
    { query: { enabled: Boolean(open && workerId) } },
  );

  // Populate form with worker data
  useEffect(() => {
    if (workerData?.data && "name" in workerData.data) {
      setName(workerData.data.name);
    }
  }, [workerData]);

  // Reset form when opening
  useEffect(() => {
    if (open) {
      setErrors({});
    }
  }, [open]);

  // Validate form
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

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    try {
      const updateData: WorkerUpdate = { name };
      await updateMutation.mutateAsync({
        workerId,
        data: updateData,
      });

      // Invalidate queries to refresh data
      queryClient.invalidateQueries({ queryKey: ["/api/v1/workers/"] });
      queryClient.invalidateQueries({
        queryKey: [`/api/v1/workers/${workerId}`],
      });

      onSuccess?.();
      onClose();
    } catch (error) {
      console.error("Failed to update worker:", error);
      setErrors({
        submit: "Failed to update worker. Please try again.",
      });
    }
  };

  const isLoading = updateMutation.isPending || isLoadingWorker;
  const submitError = errors.submit || "";

  // Safely get error message from mutation
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
        <DialogTitle>Edit Worker</DialogTitle>

        <DialogContent>
          {displayError ? (
            <Alert severity="error" sx={{ mb: 2 }}>
              {displayError}
            </Alert>
          ) : null}

          <TextField
            autoFocus
            margin="dense"
            label="Worker Name"
            fullWidth
            value={name}
            onChange={(e) => setName(e.target.value)}
            error={!!errors.name}
            helperText={errors.name}
            disabled={isLoading}
            sx={{ mt: 2 }}
          />
        </DialogContent>

        <DialogActions>
          <Button onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button type="submit" variant="contained" disabled={isLoading}>
            {isLoading ? <CircularProgress size={24} /> : "Update Worker"}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}
