"use client";

import {
  ArrowBack as ArrowBackIcon,
  AccessTime as AccessTimeIcon,
  CalendarToday as CalendarIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Update as UpdateIcon,
  Schedule as ScheduleIcon,
} from "@mui/icons-material";
import {
  Alert,
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  CircularProgress,
  Divider,
  Typography,
} from "@mui/material";
import { useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";
import { useRouter } from "next/navigation";
import { useCallback, useState } from "react";
import { useDeleteShiftTemplate, useGetShiftTemplate } from "@/api/client/shift-templates/shift-templates";
import { ConfirmationDialog } from "@/components/common/ConfirmationDialog";

interface ShiftTemplateDetailCardProps {
  shiftTemplateId: string;
  onEdit?: () => void;
  onDelete?: () => void;
}

export function ShiftTemplateDetailCard({
  shiftTemplateId,
  onEdit,
  onDelete,
}: ShiftTemplateDetailCardProps) {
  const router = useRouter();
  const queryClient = useQueryClient();

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  const { data, isLoading, error } = useGetShiftTemplate(shiftTemplateId);
  const deleteMutation = useDeleteShiftTemplate();

  const shiftTemplate = data?.data;
  const isShiftTemplateResponse = shiftTemplate && "name" in shiftTemplate && "id" in shiftTemplate;

  const handleDeleteClick = useCallback(() => {
    setDeleteDialogOpen(true);
  }, []);

  const handleDeleteConfirm = useCallback(async () => {
    try {
      await deleteMutation.mutateAsync({ shiftTemplateId });
      queryClient.invalidateQueries({ queryKey: ["/api/v1/shift-templates/"] });
      setDeleteDialogOpen(false);
      onDelete?.();
    } catch (error) {
      console.error("Failed to delete shift template:", error);
    }
  }, [shiftTemplateId, deleteMutation, queryClient, onDelete]);

  const handleDeleteCancel = useCallback(() => {
    setDeleteDialogOpen(false);
  }, []);

  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), "PPP 'at' pp");
    } catch {
      return dateString;
    }
  };

  const formatTime = (timeString: string) => {
    try {
      return new Date(`2000-01-01T${timeString}`).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return timeString;
    }
  };

  if (isLoading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: 400,
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Error loading shift template: {(error as Error).message}
      </Alert>
    );
  }

  if (!shiftTemplate || !isShiftTemplateResponse) {
    return <Alert severity="warning">Shift template not found</Alert>;
  }

  return (
    <>
      <Card>
        <CardContent>
          <Box sx={{ display: "flex", alignItems: "center", mb: 3, gap: 2 }}>
            <AccessTimeIcon color="primary" sx={{ fontSize: 40 }} />
            <Box>
              <Typography variant="h5" component="div">
                {shiftTemplate.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Shift Template ID: {shiftTemplate.id}
              </Typography>
            </Box>
          </Box>

          <Divider sx={{ my: 2 }} />

          <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <ScheduleIcon color="action" />
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Schedule Template ID
                </Typography>
                <Typography variant="body1">
                  {shiftTemplate.schedule_template_id}
                </Typography>
              </Box>
            </Box>

            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <AccessTimeIcon color="action" />
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Shift Time
                </Typography>
                <Typography variant="body1">
                  {formatTime(shiftTemplate.start_time)} - {formatTime(shiftTemplate.end_time)}
                </Typography>
              </Box>
            </Box>

            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <CalendarIcon color="action" />
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Created
                </Typography>
                <Typography variant="body1">
                  {formatDate(shiftTemplate.created_at)}
                </Typography>
              </Box>
            </Box>

            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <UpdateIcon color="action" />
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Last Updated
                </Typography>
                <Typography variant="body1">
                  {formatDate(shiftTemplate.updated_at)}
                </Typography>
              </Box>
            </Box>
          </Box>

          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>
              Used in Schedules (Coming Soon)
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Schedules using this shift template will be displayed here when the feature is implemented.
            </Typography>
          </Box>
        </CardContent>

        <CardActions sx={{ p: 2, justifyContent: "space-between" }}>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => router.push("/shift-templates")}
          >
            Back to Shift Templates
          </Button>

          <Box sx={{ display: "flex", gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<EditIcon />}
              onClick={onEdit}
            >
              Edit
            </Button>
            <Button
              variant="contained"
              color="error"
              startIcon={<DeleteIcon />}
              onClick={handleDeleteClick}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? (
                <CircularProgress size={20} />
              ) : (
                "Delete"
              )}
            </Button>
          </Box>
        </CardActions>
      </Card>

      <ConfirmationDialog
        open={deleteDialogOpen}
        title="Delete Shift Template"
        message={`Are you sure you want to delete shift template "${shiftTemplate.name}"? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
        severity="error"
      />
    </>
  );
}
