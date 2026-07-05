"use client";

import { useState, useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  CircularProgress,
  Alert,
} from "@mui/material";
import { useCreateWorker, useUpdateWorker, useGetWorker } from "@/api/client/workers/workers";
import type { Worker, WorkerUpdate } from "@/api/models";
import { useQueryClient } from "@tanstack/react-query";

interface WorkerFormProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  workerId?: string;
  mode?: "create" | "edit";
}

export function WorkerForm({
  open,
  onClose,
  onSuccess,
  workerId,
  mode = "create",
}: WorkerFormProps) {
  const queryClient = useQueryClient();
  const isEdit = mode === "edit" && workerId;
  
  // State
  const [name, setName] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});
  
  // API hooks
  const createMutation = useCreateWorker();
  const updateMutation = useUpdateWorker();
  
  // Fetch worker data for edit mode
  const { data: workerData, isLoading: isLoadingWorker } = useGetWorker(
    workerId!,
    { query: { enabled: isEdit } }
  );

  // Reset form when opening/closing
  useEffect(() => {
    if (open) {
      setName("");
      setErrors({});
    }
  }, [open]);

  // Populate form with worker data for edit mode
  useEffect(() => {
    if (isEdit && workerData?.data) {
      setName(workerData.data.name);
    }
  }, [isEdit, workerData]);

  // Validate form
  const validate = () => {
    const newErrors: Record<string, string> = {};
    
    if (!name.trim()) {
      newErrors.name = "Name is required";
    } else if (name.length > 52) {
      newErrors.name = "Name must be 52 characters or less";
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validate()) {
      return;
    }

    try {
      if (isEdit) {
        const updateData: WorkerUpdate = { name };
        await updateMutation.mutateAsync({
          workerId: workerId!,
          data: updateData,
        });
      } else {
        const createData: Worker = { name };
        await createMutation.mutateAsync({ data: createData });
      }
      
      // Invalidate queries to refresh data
      queryClient.invalidateQueries({ queryKey: ["/api/v1/workers/"] });
      if (isEdit) {
        queryClient.invalidateQueries({ queryKey: [`/api/v1/workers/${workerId}`] });
      }
      
      onSuccess?.();
      onClose();
    } catch (error) {
      console.error("Failed to save worker:", error);
      setErrors({
        submit: "Failed to save worker. Please try again.",
      });
    }
  };

  const isLoading = createMutation.isPending || updateMutation.isPending || isLoadingWorker;
  const submitError = errors.submit || createMutation.error?.message || updateMutation.error?.message;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>
          {isEdit ? "Edit Worker" : "Add New Worker"}
        </DialogTitle>
        
        <DialogContent>
          {submitError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {submitError}
            </Alert>
          )}
          
          <TextField
            autoFocus
            margin="dense"
            label="Worker Name"
            fullWidth
            value={name}
            onChange={(e) => setName(e.target.value)}
            error={!!errors.name}
            helperText={errors.name}
            disabled={isLoading}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        
        <DialogActions>
          <Button onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={isLoading}
          >
            {isLoading ? (
              <CircularProgress size={24} />
            ) : isEdit ? (
              "Update Worker"
            ) : (
              "Create Worker"
            )}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}