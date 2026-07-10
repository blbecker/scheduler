"use client";

import {
  ArrowBack as ArrowBackIcon,
  CalendarMonth as CalendarMonthIcon,
  CalendarToday as CalendarIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Update as UpdateIcon,
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
import { useDeleteScheduleTemplate, useGetScheduleTemplate } from "@/api/client/schedule-templates/schedule-templates";
import { ConfirmationDialog } from "@/components/common/ConfirmationDialog";

interface ScheduleTemplateDetailCardProps {
  scheduleTemplateId: string;
  onEdit?: () => void;
  onDelete?: () => void;
}

export function ScheduleTemplateDetailCard({
  scheduleTemplateId,
  onEdit,
  onDelete,
}: ScheduleTemplateDetailCardProps) {
  const router = useRouter();
  const queryClient = useQueryClient();

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  const { data, isLoading, error } = useGetScheduleTemplate(scheduleTemplateId);
  const deleteMutation = useDeleteScheduleTemplate();

  const scheduleTemplate = data?.data;
  const isScheduleTemplateResponse = scheduleTemplate && "name" in scheduleTemplate && "id" in scheduleTemplate;

  const handleDeleteClick = useCallback(() => {
    setDeleteDialogOpen(true);
  }, []);

  const handleDeleteConfirm = useCallback(async () => {
    try {
      await deleteMutation.mutateAsync({ scheduleTemplateId });
      queryClient.invalidateQueries({ queryKey: ["/api/v1/schedule-templates/"] });
      setDeleteDialogOpen(false);
      onDelete?.();
    } catch (error) {
      console.error("Failed to delete schedule template:", error);
    }
  }, [scheduleTemplateId, deleteMutation, queryClient, onDelete]);

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
        Error loading schedule template: {(error as Error).message}
      </Alert>
    );
  }

  if (!scheduleTemplate || !isScheduleTemplateResponse) {
    return <Alert severity="warning">Schedule template not found</Alert>;
  }

  return (
    <>
      <Card>
        <CardContent>
          <Box sx={{ display: "flex", alignItems: "center", mb: 3, gap: 2 }}>
            <CalendarMonthIcon color="primary" sx={{ fontSize: 40 }} />
            <Box>
              <Typography variant="h5" component="div">
                {scheduleTemplate.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Schedule Template ID: {scheduleTemplate.id}
              </Typography>
            </Box>
          </Box>

          <Divider sx={{ my: 2 }} />

          <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <CalendarIcon color="action" />
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Created
                </Typography>
                <Typography variant="body1">
                  {formatDate(scheduleTemplate.created_at)}
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
                  {formatDate(scheduleTemplate.updated_at)}
                </Typography>
              </Box>
            </Box>
          </Box>

          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>
              Associated Shift Templates (Coming Soon)
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Shift templates using this schedule template will be displayed here when the feature is implemented.
            </Typography>
          </Box>

          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>
              Generated Schedules (Coming Soon)
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Schedules generated from this template will be displayed here when the feature is implemented.
            </Typography>
          </Box>
        </CardContent>

        <CardActions sx={{ p: 2, justifyContent: "space-between" }}>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => router.push("/schedule-templates")}
          >
            Back to Schedule Templates
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
        title="Delete Schedule Template"
        message={`Are you sure you want to delete schedule template "${scheduleTemplate.name}"? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
        severity="error"
      />
    </>
  );
}
