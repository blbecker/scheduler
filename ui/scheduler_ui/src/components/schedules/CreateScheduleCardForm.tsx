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
import { useCreateSchedule } from "@/api/client/schedules/schedules";
import type { ScheduleCreate } from "@/api/models";

interface CreateScheduleCardFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function CreateScheduleCardForm({
  onSuccess,
  onCancel,
}: CreateScheduleCardFormProps) {
  const { mutate: createSchedule, isPending: isLoading } = useCreateSchedule();
  const [name, setName] = useState("");
  const [scheduleTemplateId, setScheduleTemplateId] = useState("");
  const [errors, setErrors] = useState<Partial<Record<keyof ScheduleCreate, string>>>({});

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof ScheduleCreate, string>> = {};

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

    const scheduleData: ScheduleCreate = {
      schedule_template_id: scheduleTemplateId,
      name,
    };

    createSchedule(
      { data: scheduleData },
      {
        onSuccess: () => {
          setName("");
          setScheduleTemplateId("");
          setErrors({});
          if (onSuccess) onSuccess();
        },
        onError: (error) => {
          console.error("Failed to create schedule:", error);
        },
      },
    );
  };

  const handleCancel = () => {
    setName("");
    setScheduleTemplateId("");
    setErrors({});
    if (onCancel) onCancel();
  };

  // Clear errors when user starts typing
  useEffect(() => {
    if (errors.name && name) {
      setErrors((prev) => ({ ...prev, name: undefined }));
    }
  }, [name, errors.name]);

  useEffect(() => {
    if (errors.schedule_template_id && scheduleTemplateId) {
      setErrors((prev) => ({ ...prev, schedule_template_id: undefined }));
    }
  }, [scheduleTemplateId, errors.schedule_template_id]);

  return (
    <Card>
      <CardHeader title="Create Schedule" />
      <CardContent>
        <TextField
          fullWidth
          label="Schedule Template ID"
          value={scheduleTemplateId}
          onChange={(e) => setScheduleTemplateId(e.target.value)}
          error={!!errors.schedule_template_id}
          helperText={errors.schedule_template_id}
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
        <Box sx={{ display: "flex", gap: 2, justifyContent: "flex-end" }}>
          <Button onClick={handleCancel} disabled={isLoading}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={isLoading}
          >
            {isLoading ? "Creating..." : "Create Schedule"}
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
}