"use client";

import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
} from "@mui/material";
import { useDeleteShift } from "@/api/client/shifts/shifts";
import type { ShiftResponse } from "@/api/models";

interface ConfirmDeleteShiftProps {
  shift: ShiftResponse | null;
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function ConfirmDeleteShift({
  shift,
  open,
  onClose,
  onSuccess,
}: ConfirmDeleteShiftProps) {
  const { mutate: deleteShift, isPending: isLoading } = useDeleteShift();

  const handleDelete = () => {
    if (!shift) return;

    deleteShift(
      { shiftId: shift.id },
      {
        onSuccess: () => {
          onClose();
          if (onSuccess) onSuccess();
        },
        onError: (error) => {
          console.error("Failed to delete shift:", error);
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
      <DialogTitle>Delete Shift</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Are you sure you want to delete the shift{" "}
          <strong>{shift?.name}</strong>? This action cannot be undone.
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