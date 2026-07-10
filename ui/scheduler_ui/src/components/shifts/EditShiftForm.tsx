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
import { useUpdateShift } from "@/api/client/shifts/shifts";
import type { ShiftResponse } from "@/api/models";

interface EditShiftFormProps {
  shift: ShiftResponse;
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function EditShiftForm({
  shift,
  open,
  onClose,
  onSuccess,
}: EditShiftFormProps) {
  const { mutate: updateShift, isPending: isLoading } = useUpdateShift();
  const [scheduleId, setScheduleId] = useState(shift.schedule_id);
  const [shiftTemplateId, setShiftTemplateId] = useState(shift.shift_template_id);
  const [name, setName] = useState(shift.name);
  const [startTime, setStartTime] = useState(shift.start_time);
  const [endTime, setEndTime] = useState(shift.end_time);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (open) {
      setScheduleId(shift.schedule_id);
      setShiftTemplateId(shift.shift_template_id);
      setName(shift.name);
      setStartTime(shift.start_time);
      setEndTime(shift.end_time);
      setErrors({});
    }
  }, [open, shift.schedule_id, shift.shift_template_id, shift.name, shift.start_time, shift.end_time]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!scheduleId.trim()) {
      newErrors.schedule_id = "Schedule ID is required";
    }

    if (!shiftTemplateId.trim()) {
      newErrors.shift_template_id = "Shift Template ID is required";
    }

    if (!name.trim()) {
      newErrors.name = "Name is required";
    }

    if (!startTime.trim()) {
      newErrors.start_time = "Start Time is required";
    }

    if (!endTime.trim()) {
      newErrors.end_time = "End Time is required";
    } else if (startTime && endTime && endTime <= startTime) {
      newErrors.end_time = "End Time must be after Start Time";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (!validate()) return;

    updateShift(
      { shiftId: shift.id, data: { schedule_id: scheduleId, shift_template_id: shiftTemplateId, name, start_time: startTime, end_time: endTime } },
      {
        onSuccess: () => {
          onClose();
          if (onSuccess) onSuccess();
        },
        onError: (error) => {
          console.error("Failed to update shift:", error);
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
      <DialogTitle>Edit Shift</DialogTitle>
      <DialogContent>
        <TextField
          margin="dense"
          label="Schedule ID"
          fullWidth
          value={scheduleId}
          onChange={(e) => setScheduleId(e.target.value)}
          error={!!errors.schedule_id}
          helperText={errors.schedule_id}
          disabled={isLoading}
          sx={{ mt: 2 }}
        />
        <TextField
          margin="dense"
          label="Shift Template ID"
          fullWidth
          value={shiftTemplateId}
          onChange={(e) => setShiftTemplateId(e.target.value)}
          error={!!errors.shift_template_id}
          helperText={errors.shift_template_id}
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
        <Button onClick={handleClose} disabled={isLoading}>
          Cancel
        </Button>
        <Button onClick={handleSubmit} variant="contained" disabled={isLoading}>
          {isLoading ? "Updating..." : "Update Shift"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
