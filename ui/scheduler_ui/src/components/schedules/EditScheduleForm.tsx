"use client";

import { useState, useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
} from "@mui/material";
import { useUpdateSchedule } from "@/api/client/schedules/schedules";
import type { ScheduleResponse } from "@/api/models";

interface EditScheduleFormProps {
  schedule: ScheduleResponse;
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function EditScheduleForm({
  schedule,
  open,
  onClose,
  onSuccess,
}: EditScheduleFormProps) {
  const { mutate: updateSchedule, isPending: isLoading } = useUpdateSchedule();
  const [name, setName] = useState(schedule.name);
  const [scheduleTemplateId, setScheduleTemplateId] = useState(
    schedule.schedule_template_id,
  );
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (open) {
      setName(schedule.name);
      setScheduleTemplateId(schedule.schedule_template_id);
      setErrors({});
    }
  }, [open, schedule.name, schedule.schedule_template_id]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!scheduleTemplateId.trim()) {
      newErrors.schedule_template_id = "Schedule Template ID is required";
    }

    if (!name.trim()) {
      newErrors.name = "Name is required";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (!validate()) return;

    updateSchedule(
      { scheduleId: schedule.id, data: { schedule_template_id: scheduleTemplateId, name } },
      {
        onSuccess: () => {
          onClose();
          if (onSuccess) onSuccess();
        },
        onError: (error) => {
          console.error("Failed to update schedule:", error);
        },
      },
    );
  };

  const handleClose = () => {
    setErrors({});
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Edit Schedule</DialogTitle>
      <DialogContent>
        <TextField
          margin="dense"
          label="Schedule Template ID"
          fullWidth
          value={scheduleTemplateId}
          onChange={(e) => setScheduleTemplateId(e.target.value)}
          error={!!errors.schedule_template_id}
          helperText={errors.schedule_template_id}
          disabled={isLoading}
          sx={{ mt: 2 }}
        />
        <TextField
          margin="dense"
          label="Name"
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
        <Button onClick={handleClose} disabled={isLoading}>
          Cancel
        </Button>
        <Button onClick={handleSubmit} variant="contained" disabled={isLoading}>
          {isLoading ? "Updating..." : "Update Schedule"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}