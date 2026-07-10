"use client";

import { useMemo, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  Box,
  Button,
  Typography,
  TextField,
  Alert,
  CircularProgress,
} from "@mui/material";
import { Add as AddIcon } from "@mui/icons-material";
import { useListScheduleTemplates, useDeleteScheduleTemplate } from "@/api/client/schedule-templates/schedule-templates";
import { useQueryClient } from "@tanstack/react-query";
import { ConfirmationDialog } from "@/components/common/ConfirmationDialog";
import { ExportButton } from "@/components/common/ExportButton";
import { ScheduleTemplatesTable } from "@/components/schedule-templates/ScheduleTemplatesTable";
import { ScheduleTemplateResponse } from "@/api/models";

export default function ScheduleTemplatesPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState("");
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [scheduleTemplateToDelete, setScheduleTemplateToDelete] = useState<ScheduleTemplateResponse | null>(
    null,
  );

  const { data, isLoading, error } = useListScheduleTemplates();

  const scheduleTemplates = useMemo(() => {
    if (!data) return [];
    return Array.isArray(data) ? data : data.data || [];
  }, [data]);

  const deleteMutation = useDeleteScheduleTemplate();

  const filteredScheduleTemplates = useMemo(() => {
    if (!searchTerm.trim()) return scheduleTemplates;
    const term = searchTerm.toLowerCase();
    return scheduleTemplates.filter(
      (scheduleTemplate) =>
        scheduleTemplate.name.toLowerCase().includes(term) ||
        scheduleTemplate.id.toLowerCase().includes(term),
    );
  }, [scheduleTemplates, searchTerm]);

  const handleDeleteClick = useCallback((scheduleTemplate: ScheduleTemplateResponse) => {
    setScheduleTemplateToDelete(scheduleTemplate);
    setDeleteDialogOpen(true);
  }, []);

  const handleDeleteConfirm = useCallback(async () => {
    if (!scheduleTemplateToDelete) return;
    try {
      await deleteMutation.mutateAsync({ scheduleTemplateId: scheduleTemplateToDelete.id });
      queryClient.invalidateQueries({ queryKey: ["/api/v1/schedule-templates/"] });
      setDeleteDialogOpen(false);
      setScheduleTemplateToDelete(null);
    } catch (error) {
      console.error("Failed to delete schedule template:", error);
    }
  }, [scheduleTemplateToDelete, deleteMutation, queryClient]);

  const handleDeleteCancel = useCallback(() => {
    setDeleteDialogOpen(false);
    setScheduleTemplateToDelete(null);
  }, []);

  const handleView = useCallback(
    (scheduleTemplateId: string) => {
      router.push(`/schedule-templates/${scheduleTemplateId}`);
    },
    [router],
  );

  const handleCreate = () => {
    router.push("/schedule-templates/new");
  };

  const hasError = error || (data && data.status && data.status !== 200);
  if (hasError) {
    return <Alert severity="error">Error loading schedule templates.</Alert>;
  }

  if (isLoading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (scheduleTemplates.length === 0) {
    return (
      <Box>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 3,
          }}
        >
          <Typography variant="h4">Schedule Templates</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreate}
          >
            Add Schedule Template
          </Button>
        </Box>
        <Box sx={{ textAlign: "center", p: 4 }}>
          <Typography variant="h6" gutterBottom>
            No schedule templates found
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Get started by adding your first schedule template.
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreate}
          >
            Add First Schedule Template
          </Button>
        </Box>
      </Box>
    );
  }

  return (
    <Box>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
        }}
      >
        <Typography variant="h4">Schedule Templates</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreate}
        >
          Add Schedule Template
        </Button>
      </Box>

      <Box sx={{ mb: 2, display: "flex", gap: 1, alignItems: "center" }}>
        <TextField
          size="small"
          placeholder="Search schedule templates..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{ width: 300 }}
        />

        <ExportButton<ScheduleTemplateResponse>
          data={filteredScheduleTemplates}
          filename="schedule-templates"
          getHeaders={() => ["ID", "Name", "Created At", "Updated At"]}
          getRowData={(scheduleTemplate) => [
            scheduleTemplate.id,
            scheduleTemplate.name,
            scheduleTemplate.created_at,
            scheduleTemplate.updated_at,
          ]}
          disabled={filteredScheduleTemplates.length === 0}
        />
      </Box>

      <ScheduleTemplatesTable
        scheduleTemplates={filteredScheduleTemplates}
        onView={handleView}
        onDelete={handleDeleteClick}
      />

      <ConfirmationDialog
        open={deleteDialogOpen}
        title="Delete Schedule Template"
        message={`Are you sure you want to delete "${scheduleTemplateToDelete?.name}"?`}
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
      />
    </Box>
  );
}
