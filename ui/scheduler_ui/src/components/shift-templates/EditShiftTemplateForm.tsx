"use client";

import {
  Alert,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  MenuItem,
  TextField,
} from "@mui/material";
import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useState, useMemo } from "react";
import { useGetShiftTemplate, useUpdateShiftTemplate } from "@/api/client/shift-templates/shift-templates";
import { useListScheduleTemplates } from "@/api/client/schedule-templates/schedule-templates";
import type { ShiftTemplateUpdate, ScheduleTemplateResponse } from "@/api/models";

interface EditShiftTemplateFormProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  shiftTemplateId: string;
}

export function EditShiftTemplateForm({
  open,
  onClose,
  onSuccess,
  shiftTemplateId,
}: EditShiftTemplateFormProps) {
  const queryClient = useQueryClient();

  const [scheduleTemplateId, setScheduleTemplateId] = useState("");
  const [name, setName] = useState("");
  const [startTime, setStartTime] = useState("09:00");
  const [endTime, setEndTime] = useState("17:00");
  const [errors, setErrors] = useState<Record<string, string>>({});

  const updateMutation = useUpdateShiftTemplate();
  const { data: scheduleTemplatesData } = useListScheduleTemplates();

  const { data: shiftTemplateData, isLoading: isLoadingShiftTemplate } = useGetShiftTemplate(
    shiftTemplateId,
    { query: { enabled: Boolean(open && shiftTemplateId) } },
  );

  const scheduleTemplates = scheduleTemplatesData?.data || [];

  useEffect(() => {
    if (shiftTemplateData?.data && "name" in shiftTemplateData.data) {
      const shiftTemplate = shiftTemplateData.data;
      setScheduleTemplateId(shiftTemplate.schedule_template_id);
      setName(shiftTemplate.name);
      setStartTime(shiftTemplate.start_time);
      setEndTime(shiftTemplate.end_time);
    }
  }, [shiftTemplateData]);

  useEffect(() => {
    if (open) {
      setErrors({});
    }
  }, [open]);

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
      const updateData: ShiftTemplateUpdate = {
        schedule_template_id: scheduleTemplateId,
        name,
        start_time: startTime,
        end_time: endTime,
      };
      await updateMutation.mutateAsync({
        shiftTemplateId,
        data: updateData,
      });

      queryClient.invalidateQueries({ queryKey: ["/api/v1/shift-templates/"] });
      queryClient.invalidateQueries({
        queryKey: [`/api/v1/shift-templates/${shiftTemplateId}`],
      });

      onSuccess?.();
      onClose();
    } catch (error) {
      console.error("Failed to update shift template:", error);
      setErrors({
        submit: "Failed to update shift template. Please try again.",
      });
    }
  };

  const isLoading = updateMutation.isPending || isLoadingShiftTemplate;
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
        <DialogTitle>Edit Shift Template</DialogTitle>

        <DialogContent>
          {displayError ? (
            <Alert severity="error" sx={{ mb: 2 }}>
              {displayError}
            </Alert>
          ) : null}

          <TextField
            select
            fullWidth
            margin="dense"
            label="Schedule Template"
            value={scheduleTemplateId}
            onChange={(e) => setScheduleTemplateId(e.target.value)}
            error={!!errors.schedule_template_id}
            helperText={errors.schedule_template_id}
            disabled={isLoading}
            sx={{ mt: 2 }}
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
            margin="dense"
            label="Shift Template Name"
            fullWidth
            value={name}
            onChange={(e) => setName(e.target.value)}
            error={!!errors.name}
            helperText={errors.name}
            disabled={isLoading}
            sx={{ mt: 2 }}
            placeholder="e.g., Morning Shift, Night Shift, Weekend Shift"
          />

          <TextField
            margin="dense"
            label="Start Time"
            type="time"
            fullWidth
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
            error={!!errors.start_time}
            helperText={errors.start_time}
            disabled={isLoading}
            sx={{ mt: 2 }}
          />

          <TextField
            margin="dense"
            label="End Time"
            type="time"
            fullWidth
            value={endTime}
            onChange={(e) => setEndTime(e.target.value)}
            error={!!errors.end_time}
            helperText={errors.end_time}
            disabled={isLoading}
            sx={{ mt: 2 }}
          />
        </DialogContent>

        <DialogActions>
          <Button onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button type="submit" variant="contained" disabled={isLoading}>
            {isLoading ? <CircularProgress size={24} /> : "Update Shift Template"}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}
