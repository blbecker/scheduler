"use client";

import { useState, useMemo } from "react";
import { Box, Button, Typography } from "@mui/material";
import { Add as AddIcon } from "@mui/icons-material";
import { useRouter } from "next/navigation";
import { useListShifts } from "@/api/client/shifts/shifts";
import {
  CreateShiftCardForm,
  ShiftsTable,
  EditShiftForm,
  ConfirmDeleteShift,
} from "@/components/shifts";
import type { ShiftResponse } from "@/api/models";

export default function ShiftsPage() {
  const router = useRouter();
  const { data: shiftsResponse = [], isLoading, refetch } = useListShifts();

  const shifts = useMemo(() => {
    if (!shiftsResponse) return [];
    return Array.isArray(shiftsResponse) ? shiftsResponse : shiftsResponse.data || [];
  }, [shiftsResponse]);

  const [showCreateForm, setShowCreateForm] = useState(false);
  const [shiftToEdit, setShiftToEdit] = useState<ShiftResponse | null>(null);
  const [shiftToDelete, setShiftToDelete] = useState<ShiftResponse | null>(null);

  const handleViewShift = (shiftId: string) => {
    router.push(`/shifts/${shiftId}`);
  };

  const handleEditShift = (shiftId: string) => {
    const shift = shifts.find((s) => s.id === shiftId);
    if (shift) {
      setShiftToEdit(shift);
    }
  };

  const handleDeleteShift = (shift: ShiftResponse) => {
    setShiftToDelete(shift);
  };

  const handleEditSuccess = () => {
    setShiftToEdit(null);
    refetch();
  };

  const handleDeleteSuccess = () => {
    setShiftToDelete(null);
    refetch();
  };

  const handleCreateSuccess = () => {
    setShowCreateForm(false);
    refetch();
  };

  return (
    <Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 3 }}>
        <Typography variant="h4">Shifts</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          {showCreateForm ? "Cancel" : "New Shift"}
        </Button>
      </Box>

      {showCreateForm && (
        <Box sx={{ mb: 4 }}>
          <CreateShiftCardForm
            onSuccess={handleCreateSuccess}
            onCancel={() => setShowCreateForm(false)}
          />
        </Box>
      )}

      <ShiftsTable
        shifts={shifts}
        onView={handleViewShift}
        onDelete={handleDeleteShift}
      />

      {shiftToEdit && (
        <EditShiftForm
          shift={shiftToEdit}
          open={!!shiftToEdit}
          onClose={() => setShiftToEdit(null)}
          onSuccess={handleEditSuccess}
        />
      )}

      <ConfirmDeleteShift
        shift={shiftToDelete}
        open={!!shiftToDelete}
        onClose={() => setShiftToDelete(null)}
        onSuccess={handleDeleteSuccess}
      />
    </Box>
  );
}