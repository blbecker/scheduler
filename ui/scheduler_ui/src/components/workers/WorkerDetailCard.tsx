"use client";

import {
  ArrowBack as ArrowBackIcon,
  CalendarToday as CalendarIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Person as PersonIcon,
  Update as UpdateIcon,
} from "@mui/icons-material";
import {
  Alert,
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  Typography,
} from "@mui/material";
import { useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";
import { useRouter } from "next/navigation";
import { useCallback, useState } from "react";
import { useDeleteWorker, useGetWorker } from "@/api/client/workers/workers";
import { ConfirmationDialog } from "@/components/common/ConfirmationDialog";

interface WorkerDetailCardProps {
  workerId: string;
  onEdit?: () => void;
  onDelete?: () => void;
}

export function WorkerDetailCard({
  workerId,
  onEdit,
  onDelete,
}: WorkerDetailCardProps) {
  const router = useRouter();
  const queryClient = useQueryClient();

  // State
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  // API hooks
  const { data, isLoading, error } = useGetWorker(workerId);
  const deleteMutation = useDeleteWorker();

  const worker = data?.data;
  const isWorkerResponse = worker && "name" in worker && "id" in worker;

  // Handle delete
  const handleDeleteClick = useCallback(() => {
    setDeleteDialogOpen(true);
  }, []);

  const handleDeleteConfirm = useCallback(async () => {
    try {
      await deleteMutation.mutateAsync({ workerId });
      queryClient.invalidateQueries({ queryKey: ["/api/v1/workers/"] });
      setDeleteDialogOpen(false);
      onDelete?.();
    } catch (error) {
      console.error("Failed to delete worker:", error);
    }
  }, [workerId, deleteMutation, queryClient, onDelete]);

  const handleDeleteCancel = useCallback(() => {
    setDeleteDialogOpen(false);
  }, []);

  // Format date for display
  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), "PPP 'at' pp");
    } catch {
      return dateString;
    }
  };

  // Loading state
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

  // Error state
  if (error) {
    return (
      <Alert severity="error">
        Error loading worker: {(error as Error).message}
      </Alert>
    );
  }

  // Not found state
  if (!worker || !isWorkerResponse) {
    return <Alert severity="warning">Worker not found</Alert>;
  }

  return (
    <>
      <Card>
        <CardContent>
          <Box sx={{ display: "flex", alignItems: "center", mb: 3, gap: 2 }}>
            <PersonIcon color="primary" sx={{ fontSize: 40 }} />
            <Box>
              <Typography variant="h5" component="div">
                {worker.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Worker ID: {worker.id}
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
                  {formatDate(worker.created_at)}
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
                  {formatDate(worker.updated_at)}
                </Typography>
              </Box>
            </Box>
          </Box>

          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>
              Skills (Coming Soon)
            </Typography>
            <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
              <Chip
                label="No skills assigned"
                color="default"
                variant="outlined"
              />
            </Box>
          </Box>

          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>
              Assigned Shifts (Coming Soon)
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Shift assignments will be displayed here when the scheduling
              feature is implemented.
            </Typography>
          </Box>
        </CardContent>

        <CardActions sx={{ p: 2, justifyContent: "space-between" }}>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => router.push("/workers")}
          >
            Back to Workers
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
        title="Delete Worker"
        message={`Are you sure you want to delete worker "${worker.name}"? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
        severity="error"
      />
    </>
  );
}
