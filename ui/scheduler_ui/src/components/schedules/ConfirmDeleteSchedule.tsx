"use client";

import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
} from "@mui/material";
import { useDeleteSchedule } from "@/api/client/schedules/schedules";
import type { ScheduleResponse } from "@/api/models";

interface ConfirmDeleteScheduleProps {
  schedule: ScheduleResponse | null;
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function ConfirmDeleteSchedule({
  schedule,
  open,
  onClose,
  onSuccess,
}: ConfirmDeleteScheduleProps) {
  const { mutate: deleteSchedule, isPending: isLoading } = useDeleteSchedule();

  const handleDelete = () => {
    if (!schedule) return;

    deleteSchedule(
      { scheduleId: schedule.id },
      {
        onSuccess: () => {
          onClose();
          if (onSuccess) onSuccess();
        },
        onError: (error) => {
          console.error("Failed to delete schedule:", error);
        },
      },
    );
  };

  const handleClose = () => {
    if (!isLoading) {
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={handleClose}>
      <DialogTitle>Delete Schedule</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Are you sure you want to delete the schedule{" "}
          <strong>{schedule?.name}</strong>? This action cannot be undone.
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={isLoading}>
          Cancel
        </Button>
        <Button
          onClick={handleDelete}
          variant="contained"
          color="error"
          disabled={isLoading}
        >
          {isLoading ? "Deleting..." : "Delete"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}