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
import { useCreateScheduleTemplate } from "@/api/client/schedule-templates/schedule-templates";
import type { ScheduleTemplateCreate } from "@/api/models";

interface CreateScheduleTemplateCardFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function CreateScheduleTemplateCardForm({
  onSuccess,
  onCancel,
}: CreateScheduleTemplateCardFormProps) {
  const queryClient = useQueryClient();

  const [name, setName] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});

  const createMutation = useCreateScheduleTemplate();

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
      const createData: ScheduleTemplateCreate = { name };
      await createMutation.mutateAsync({ data: createData });

      queryClient.invalidateQueries({ queryKey: ["/api/v1/schedule-templates/"] });

      onSuccess?.();
    } catch (error) {
      console.error("Failed to create schedule template:", error);
      setErrors({
        submit: "Failed to create schedule template. Please try again.",
      });
    }
  };

  const isLoading = createMutation.isPending;

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
          Add New Schedule Template
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
            label="Schedule Template Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            error={!!errors.name}
            helperText={errors.name}
            disabled={isLoading}
            sx={{ mt: 2, mb: 2 }}
            placeholder="e.g., Weekly Schedule, Monthly Rotation"
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
          {isLoading ? <CircularProgress size={24} /> : "Create Schedule Template"}
        </Button>
      </CardActions>
    </Card>
  );
}