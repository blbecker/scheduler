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
import { useListShiftTemplates, useDeleteShiftTemplate } from "@/api/client/shift-templates/shift-templates";
import { useQueryClient } from "@tanstack/react-query";
import { ConfirmationDialog } from "@/components/common/ConfirmationDialog";
import { ExportButton } from "@/components/common/ExportButton";
import { ShiftTemplatesTable } from "@/components/shift-templates/ShiftTemplatesTable";
import { ShiftTemplateResponse } from "@/api/models";

export default function ShiftTemplatesPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState("");
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [shiftTemplateToDelete, setShiftTemplateToDelete] = useState<ShiftTemplateResponse | null>(
    null,
  );

  const { data, isLoading, error } = useListShiftTemplates();

  const shiftTemplates = useMemo(() => {
    if (!data) return [];
    return Array.isArray(data) ? data : data.data || [];
  }, [data]);

  const deleteMutation = useDeleteShiftTemplate();

  const filteredShiftTemplates = useMemo(() => {
    if (!searchTerm.trim()) return shiftTemplates;
    const term = searchTerm.toLowerCase();
    return shiftTemplates.filter(
      (shiftTemplate) =>
        shiftTemplate.name.toLowerCase().includes(term) ||
        shiftTemplate.id.toLowerCase().includes(term) ||
        shiftTemplate.schedule_template_id.toLowerCase().includes(term) ||
        shiftTemplate.start_time.toLowerCase().includes(term) ||
        shiftTemplate.end_time.toLowerCase().includes(term),
    );
  }, [shiftTemplates, searchTerm]);

  const handleDeleteClick = useCallback((shiftTemplate: ShiftTemplateResponse) => {
    setShiftTemplateToDelete(shiftTemplate);
    setDeleteDialogOpen(true);
  }, []);

  const handleDeleteConfirm = useCallback(async () => {
    if (!shiftTemplateToDelete) return;
    try {
      await deleteMutation.mutateAsync({ shiftTemplateId: shiftTemplateToDelete.id });
      queryClient.invalidateQueries({ queryKey: ["/api/v1/shift-templates/"] });
      setDeleteDialogOpen(false);
      setShiftTemplateToDelete(null);
    } catch (error) {
      console.error("Failed to delete shift template:", error);
    }
  }, [shiftTemplateToDelete, deleteMutation, queryClient]);

  const handleDeleteCancel = useCallback(() => {
    setDeleteDialogOpen(false);
    setShiftTemplateToDelete(null);
  }, []);

  const handleView = useCallback(
    (shiftTemplateId: string) => {
      router.push(`/shift-templates/${shiftTemplateId}`);
    },
    [router],
  );

  const handleCreate = () => {
    router.push("/shift-templates/new");
  };

  const hasError = error || (data && data.status && data.status !== 200);
  if (hasError) {
    return <Alert severity="error">Error loading shift templates.</Alert>;
  }

  if (isLoading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (shiftTemplates.length === 0) {
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
          <Typography variant="h4">Shift Templates</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreate}
          >
            Add Shift Template
          </Button>
        </Box>
        <Box sx={{ textAlign: "center", p: 4 }}>
          <Typography variant="h6" gutterBottom>
            No shift templates found
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Get started by adding your first shift template.
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreate}
          >
            Add First Shift Template
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
        <Typography variant="h4">Shift Templates</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreate}
        >
          Add Shift Template
        </Button>
      </Box>

      <Box sx={{ mb: 2, display: "flex", gap: 1, alignItems: "center" }}>
        <TextField
          size="small"
          placeholder="Search shift templates..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{ width: 300 }}
        />

        <ExportButton<ShiftTemplateResponse>
          data={filteredShiftTemplates}
          filename="shift-templates"
          getHeaders={() => ["ID", "Schedule Template ID", "Name", "Start Time", "End Time", "Created At", "Updated At"]}
          getRowData={(shiftTemplate) => [
            shiftTemplate.id,
            shiftTemplate.schedule_template_id,
            shiftTemplate.name,
            shiftTemplate.start_time,
            shiftTemplate.end_time,
            shiftTemplate.created_at,
            shiftTemplate.updated_at,
          ]}
          disabled={filteredShiftTemplates.length === 0}
        />
      </Box>

      <ShiftTemplatesTable
        shiftTemplates={filteredShiftTemplates}
        onView={handleView}
        onDelete={handleDeleteClick}
      />

      <ConfirmationDialog
        open={deleteDialogOpen}
        title="Delete Shift Template"
        message={`Are you sure you want to delete "${shiftTemplateToDelete?.name}"?`}
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
      />
    </Box>
  );
}