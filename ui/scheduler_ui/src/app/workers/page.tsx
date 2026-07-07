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
import { useListWorkers, useDeleteWorker } from "@/api/client/workers/workers";
import { useQueryClient } from "@tanstack/react-query";
import { ConfirmationDialog } from "@/components/common/ConfirmationDialog";
import { ExportButton } from "@/components/common/ExportButton";
import { WorkersTable } from "@/components/workers/WorkersTable";
import { WorkerResponse } from "@/api/models";

export default function WorkersPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState("");
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [workerToDelete, setWorkerToDelete] = useState<WorkerResponse | null>(
    null,
  );

  const { data, isLoading, error } = useListWorkers();

  // Extract workers from response
  const workers = useMemo(() => {
    if (!data) return [];
    // Handle both array response and { data: array } response
    return Array.isArray(data) ? data : data.data || [];
  }, [data]);

  const deleteMutation = useDeleteWorker();

  const filteredWorkers = useMemo(() => {
    if (!searchTerm.trim()) return workers;
    const term = searchTerm.toLowerCase();
    return workers.filter(
      (worker) =>
        worker.name.toLowerCase().includes(term) ||
        worker.id.toLowerCase().includes(term),
    );
  }, [workers, searchTerm]);

  // Handle delete
  const handleDeleteClick = useCallback((worker: WorkerResponse) => {
    setWorkerToDelete(worker);
    setDeleteDialogOpen(true);
  }, []);

  const handleDeleteConfirm = useCallback(async () => {
    if (!workerToDelete) return;
    try {
      await deleteMutation.mutateAsync({ workerId: workerToDelete.id });
      queryClient.invalidateQueries({ queryKey: ["/api/v1/workers/"] });
      setDeleteDialogOpen(false);
      setWorkerToDelete(null);
    } catch (error) {
      console.error("Failed to delete worker:", error);
    }
  }, [workerToDelete, deleteMutation, queryClient]);

  const handleDeleteCancel = useCallback(() => {
    setDeleteDialogOpen(false);
    setWorkerToDelete(null);
  }, []);

  // Handle view
  const handleView = useCallback(
    (workerId: string) => {
      router.push(`/workers/${workerId}`);
    },
    [router],
  );

  const handleCreate = () => {
    router.push("/workers/new");
  };

  // Error state - check both React Query error and Orval HTTP error pattern
  const hasError = error || (data && data.status && data.status !== 200);
  if (hasError) {
    return <Alert severity="error">Error loading workers.</Alert>;
  }

  // Loading state
  if (isLoading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  // Empty state
  if (workers.length === 0) {
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
          <Typography variant="h4">Workers</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreate}
          >
            Add Worker
          </Button>
        </Box>
        <Box sx={{ textAlign: "center", p: 4 }}>
          <Typography variant="h6" gutterBottom>
            No workers found
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Get started by adding your first worker.
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreate}
          >
            Add First Worker
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
        <Typography variant="h4">Workers</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreate}
        >
          Add Worker
        </Button>
      </Box>

      <Box sx={{ mb: 2, display: "flex", gap: 1, alignItems: "center" }}>
        <TextField
          size="small"
          placeholder="Search workers..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{ width: 300 }}
        />

        <ExportButton<WorkerResponse>
          data={filteredWorkers}
          filename="workers"
          getHeaders={() => ["ID", "Name", "Created At", "Updated At"]}
          getRowData={(worker) => [
            worker.id,
            worker.name,
            worker.created_at,
            worker.updated_at,
          ]}
          disabled={filteredWorkers.length === 0}
        />
      </Box>

      <WorkersTable
        workers={filteredWorkers}
        onView={handleView}
        onDelete={handleDeleteClick}
      />

      <ConfirmationDialog
        open={deleteDialogOpen}
        title="Delete Worker"
        message={`Are you sure you want to delete "${workerToDelete?.name}"?`}
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
      />
    </Box>
  );
}
