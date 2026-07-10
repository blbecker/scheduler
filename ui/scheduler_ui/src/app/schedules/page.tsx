"use client";

import { useState, useMemo } from "react";
import { Box, Button, Typography } from "@mui/material";
import { Add as AddIcon } from "@mui/icons-material";
import { useRouter } from "next/navigation";
import { useListSchedules } from "@/api/client/schedules/schedules";
import {
  CreateScheduleCardForm,
  SchedulesTable,
  EditScheduleForm,
  ConfirmDeleteSchedule,
} from "@/components/schedules";
import type { ScheduleResponse } from "@/api/models";

export default function SchedulesPage() {
  const router = useRouter();
  const { data: schedulesResponse = [], isLoading, refetch } = useListSchedules();

  const schedules = useMemo(() => {
    if (!schedulesResponse) return [];
    return Array.isArray(schedulesResponse) ? schedulesResponse : schedulesResponse.data || [];
  }, [schedulesResponse]);

  const [showCreateForm, setShowCreateForm] = useState(false);
  const [scheduleToEdit, setScheduleToEdit] = useState<ScheduleResponse | null>(null);
  const [scheduleToDelete, setScheduleToDelete] = useState<ScheduleResponse | null>(null);

  const handleViewSchedule = (scheduleId: string) => {
    router.push(`/schedules/${scheduleId}`);
  };

  const handleEditSchedule = (scheduleId: string) => {
    const schedule = schedules.find((s) => s.id === scheduleId);
    if (schedule) {
      setScheduleToEdit(schedule);
    }
  };

  const handleDeleteSchedule = (schedule: ScheduleResponse) => {
    setScheduleToDelete(schedule);
  };

  const handleEditSuccess = () => {
    setScheduleToEdit(null);
    refetch();
  };

  const handleDeleteSuccess = () => {
    setScheduleToDelete(null);
    refetch();
  };

  const handleCreateSuccess = () => {
    setShowCreateForm(false);
    refetch();
  };

  return (
    <Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 3 }}>
        <Typography variant="h4">Schedules</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          {showCreateForm ? "Cancel" : "New Schedule"}
        </Button>
      </Box>

      {showCreateForm && (
        <Box sx={{ mb: 4 }}>
          <CreateScheduleCardForm
            onSuccess={handleCreateSuccess}
            onCancel={() => setShowCreateForm(false)}
          />
        </Box>
      )}

      <SchedulesTable
        schedules={schedules}
        onView={handleViewSchedule}
        onDelete={handleDeleteSchedule}
      />

      {scheduleToEdit && (
        <EditScheduleForm
          schedule={scheduleToEdit}
          open={!!scheduleToEdit}
          onClose={() => setScheduleToEdit(null)}
          onSuccess={handleEditSuccess}
        />
      )}

      <ConfirmDeleteSchedule
        schedule={scheduleToDelete}
        open={!!scheduleToDelete}
        onClose={() => setScheduleToDelete(null)}
        onSuccess={handleDeleteSuccess}
      />
    </Box>
  );
}
