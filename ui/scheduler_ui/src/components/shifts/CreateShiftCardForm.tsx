"use client";

import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  TextField,
  Button,
  Box,
} from "@mui/material";
import { useCreateShift } from "@/api/client/shifts/shifts";
import type { ShiftCreate } from "@/api/models";

interface CreateShiftCardFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function CreateShiftCardForm({
  onSuccess,
  onCancel,
}: CreateShiftCardFormProps) {
  const { mutate: createShift, isPending: isLoading } = useCreateShift();
  const [scheduleId, setScheduleId] = useState("");
  const [shiftTemplateId, setShiftTemplateId] = useState("");
  const [name, setName] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [errors, setErrors] = useState<Partial<Record<keyof ShiftCreate, string>>>({});

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof ShiftCreate, string>> = {};

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

    const shiftData: ShiftCreate = {
      schedule_id: scheduleId,
      shift_template_id: shiftTemplateId,
      name,
      start_time: startTime,
      end_time: endTime,
    };

    createShift(
      { data: shiftData },
      {
        onSuccess: () => {
          setScheduleId("");
          setShiftTemplateId("");
          setName("");
          setStartTime("");
          setEndTime("");
          setErrors({});
          if (onSuccess) onSuccess();
        },
        onError: (error) => {
          console.error("Failed to create shift:", error);
        },
      },
    );
  };

  const handleCancel = () => {
    setScheduleId("");
    setShiftTemplateId("");
    setName("");
    setStartTime("");
    setEndTime("");
    setErrors({});
    if (onCancel) onCancel();
  };

  // Clear errors when user starts typing
  useEffect(() => {
    if (errors.schedule_id && scheduleId) {
      setErrors((prev) => ({ ...prev, schedule_id: undefined }));
    }
  }, [scheduleId, errors.schedule_id]);

  useEffect(() => {
    if (errors.shift_template_id && shiftTemplateId) {
      setErrors((prev) => ({ ...prev, shift_template_id: undefined }));
    }
  }, [shiftTemplateId, errors.shift_template_id]);

  useEffect(() => {
    if (errors.name && name) {
      setErrors((prev) => ({ ...prev, name: undefined }));
    }
  }, [name, errors.name]);

  useEffect(() => {
    if (errors.start_time && startTime) {
      setErrors((prev) => ({ ...prev, start_time: undefined }));
    }
  }, [startTime, errors.start_time]);

  useEffect(() => {
    if (errors.end_time && endTime) {
      setErrors((prev) => ({ ...prev, end_time: undefined }));
    }
  }, [endTime, errors.end_time]);

  return (
    <Card>
      <CardHeader title="Create Shift" />
      <CardContent>
        <TextField
          fullWidth
          label="Schedule ID"
          value={scheduleId}
          onChange={(e) => setScheduleId(e.target.value)}
          error={!!errors.schedule_id}
          helperText={errors.schedule_id}
          disabled={isLoading}
          sx={{ mb: 2 }}
        />
        <TextField
          fullWidth
          label="Shift Template ID"
          value={shiftTemplateId}
          onChange={(e) => setShiftTemplateId(e.target.value)}
          error={!!errors.shift_template_id}
          helperText={errors.shift_template_id}
          disabled={isLoading}
          sx={{ mb: 2 }}
        />
        <TextField
          fullWidth
          label="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          error={!!errors.name}
          helperText={errors.name}
          disabled={isLoading}
          sx={{ mb: 2 }}
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
        <Box sx={{ display: "flex", gap: 2, justifyContent: "flex-end" }}>
          <Button onClick={handleCancel} disabled={isLoading}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={isLoading}
          >
            {isLoading ? "Creating..." : "Create Shift"}
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
}