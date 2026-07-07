"use client";

import {
  Alert,
  Button,
  Card,
  CardActions,
  CardContent,
  CircularProgress,
  TextField,
  Typography,
} from "@mui/material";
import { useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useCreateWorker } from "@/api/client/workers/workers";
import type { WorkerCreate } from "@/api/models";

interface CreateWorkerCardFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function CreateWorkerCardForm({
  onSuccess,
  onCancel,
}: CreateWorkerCardFormProps) {
  const queryClient = useQueryClient();

  // State
  const [name, setName] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});

  // API hooks
  const createMutation = useCreateWorker();

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
      const createData: WorkerCreate = { name };
      await createMutation.mutateAsync({ data: createData });

      // Invalidate queries to refresh data
      queryClient.invalidateQueries({ queryKey: ["/api/v1/workers/"] });

      // Success - navigate back to workers listing
      onSuccess?.();
    } catch (error) {
      console.error("Failed to create worker:", error);
      setErrors({
        submit: "Failed to create worker. Please try again.",
      });
    }
  };

  const isLoading = createMutation.isPending;

  // Safely get error message from mutation
  const getMutationErrorMessage = () => {
    if (!createMutation.error) return "";

    const err = createMutation.error;
    if (err instanceof Error) return err.message;
    if (typeof err === "object" && err !== null && "message" in err) {
      return String((err as { message: string }).message);
    }
    return String(err);
  };

  const submitError = errors.submit || getMutationErrorMessage();
  const displayError = submitError;

  return (
    <Card sx={{ maxWidth: 600, mx: "auto" }}>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          Add New Worker
        </Typography>

        <form onSubmit={handleSubmit}>
          {displayError ? (
            <Alert severity="error" sx={{ mb: 2 }}>
              {displayError}
            </Alert>
          ) : null}

          <TextField
            autoFocus
            fullWidth
            label="Worker Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            error={!!errors.name}
            helperText={errors.name}
            disabled={isLoading}
            sx={{ mt: 2, mb: 2 }}
          />
        </form>
      </CardContent>

      <CardActions sx={{ p: 2, justifyContent: "flex-end" }}>
        <Button onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button
          type="submit"
          variant="contained"
          disabled={isLoading}
          onClick={handleSubmit}
        >
          {isLoading ? <CircularProgress size={24} /> : "Create Worker"}
        </Button>
      </CardActions>
    </Card>
  );
}
