"use client";

import {
  Alert,
  Button,
  Card,
  CardActions,
  CardContent,
  CircularProgress,
  MenuItem,
  TextField,
  Typography,
} from "@mui/material";
import { useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useCreateShiftTemplate } from "@/api/client/shift-templates/shift-templates";
import { useListScheduleTemplates } from "@/api/client/schedule-templates/schedule-templates";
import type { ShiftTemplateCreate, ScheduleTemplateResponse } from "@/api/models";

interface CreateShiftTemplateCardFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function CreateShiftTemplateCardForm({
  onSuccess,
  onCancel,
}: CreateShiftTemplateCardFormProps) {
  const queryClient = useQueryClient();

  const [scheduleTemplateId, setScheduleTemplateId] = useState("");
  const [name, setName] = useState("");
  const [startTime, setStartTime] = useState("09:00");
  const [endTime, setEndTime] = useState("17:00");
  const [errors, setErrors] = useState<Record<string, string>>({});

  const createMutation = useCreateShiftTemplate();
  const { data: scheduleTemplatesData } = useListScheduleTemplates();

  const scheduleTemplates = scheduleTemplatesData?.data || [];

  const validate = () => {
    const newErrors: Record<string, string> = {};

    if (!scheduleTemplateId.trim()) {
      newErrors.schedule_template_id = "Schedule template is required";
    }

    if (!name.trim()) {
      newErrors.name = "Name is required";
    } else if (name.length > 52) {
      newErrors.name = "Name must be 52 characters or less";
    }

    if (!startTime.trim()) {
      newErrors.start_time = "Start time is required";
    }

    if (!endTime.trim()) {
      newErrors.end_time = "End time is required";
    }

    if (startTime && endTime) {
      const start = new Date(`2000-01-01T${startTime}`);
      const end = new Date(`2000-01-01T${endTime}`);
      if (end <= start) {
        newErrors.end_time = "End time must be after start time";
      }
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
      const createData: ShiftTemplateCreate = {
        schedule_template_id: scheduleTemplateId,
        name,
        start_time: startTime,
        end_time: endTime,
      };
      await createMutation.mutateAsync({ data: createData });

      queryClient.invalidateQueries({ queryKey: ["/api/v1/shift-templates/"] });

      onSuccess?.();
    } catch (error) {
      console.error("Failed to create shift template:", error);
      setErrors({
        submit: "Failed to create shift template. Please try again.",
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
          Add New Shift Template
        </Typography>

        <form onSubmit={handleSubmit}>
          {displayError ? (
            <Alert severity="error" sx={{ mb: 2 }}>
              {displayError}
            </Alert>
          ) : null}

          <TextField
            select
            fullWidth
            label="Schedule Template"
            value={scheduleTemplateId}
            onChange={(e) => setScheduleTemplateId(e.target.value)}
            error={!!errors.schedule_template_id}
            helperText={errors.schedule_template_id}
            disabled={isLoading}
            sx={{ mt: 2, mb: 2 }}
          >
            <MenuItem value="">
              <em>Select a schedule template</em>
            </MenuItem>
            {scheduleTemplates.map((template: ScheduleTemplateResponse) => (
              <MenuItem key={template.id} value={template.id}>
                {template.name}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            autoFocus
            fullWidth
            label="Shift Template Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            error={!!errors.name}
            helperText={errors.name}
            disabled={isLoading}
            sx={{ mb: 2 }}
            placeholder="e.g., Morning Shift, Night Shift, Weekend Shift"
          />

          <TextField
            fullWidth
            label="Start Time"
            type="time"
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
            error={!!errors.start_time}
            helperText={errors.start_time}
            disabled={isLoading}
            sx={{ mb: 2 }}
          />

          <TextField
            fullWidth
            label="End Time"
            type="time"
            value={endTime}
            onChange={(e) => setEndTime(e.target.value)}
            error={!!errors.end_time}
            helperText={errors.end_time}
            disabled={isLoading}
            sx={{ mb: 2 }}
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
          {isLoading ? <CircularProgress size={24} /> : "Create Shift Template"}
        </Button>
      </CardActions>
    </Card>
  );
}