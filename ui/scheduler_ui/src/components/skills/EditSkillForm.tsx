"use client";

import {
  Alert,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
} from "@mui/material";
import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useState, useMemo } from "react";
import { useGetSkill, useUpdateSkill } from "@/api/client/skills/skills";
import type { SkillUpdate } from "@/api/models";

interface EditSkillFormProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  skillId: string;
}

export function EditSkillForm({
  open,
  onClose,
  onSuccess,
  skillId,
}: EditSkillFormProps) {
  const queryClient = useQueryClient();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});

  const updateMutation = useUpdateSkill();

  const { data: skillData, isLoading: isLoadingSkill } = useGetSkill(
    skillId,
    { query: { enabled: Boolean(open && skillId) } },
  );

  useEffect(() => {
    if (skillData?.data && "name" in skillData.data) {
      setName(skillData.data.name);
      setDescription(skillData.data.description || "");
    }
  }, [skillData]);

  useEffect(() => {
    if (open) {
      setErrors({});
    }
  }, [open]);

  const validate = () => {
    const newErrors: Record<string, string> = {};

    if (!name.trim()) {
      newErrors.name = "Name is required";
    } else if (name.length > 52) {
      newErrors.name = "Name must be 52 characters or less";
    }

    if (description.length > 255) {
      newErrors.description = "Description must be 255 characters or less";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    try {
      const updateData: SkillUpdate = {
        name,
        description: description.trim() || null,
      };
      await updateMutation.mutateAsync({
        skillId,
        data: updateData,
      });

      queryClient.invalidateQueries({ queryKey: ["/api/v1/skills/"] });
      queryClient.invalidateQueries({
        queryKey: [`/api/v1/skills/${skillId}`],
      });

      onSuccess?.();
      onClose();
    } catch (error) {
      console.error("Failed to update skill:", error);
      setErrors({
        submit: "Failed to update skill. Please try again.",
      });
    }
  };

  const isLoading = updateMutation.isPending || isLoadingSkill;
  const submitError = errors.submit || "";

  const mutationErrorMessage = useMemo(() => {
    if (!updateMutation.error) return "";

    const err = updateMutation.error;
    if (err instanceof Error) return err.message;
    if (typeof err === "object" && err !== null && "message" in err) {
      return String((err as { message: string }).message);
    }
    return String(err);
  }, [updateMutation.error]);

  const displayError = submitError || mutationErrorMessage;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>Edit Skill</DialogTitle>

        <DialogContent>
          {displayError ? (
            <Alert severity="error" sx={{ mb: 2 }}>
              {displayError}
            </Alert>
          ) : null}

          <TextField
            autoFocus
            margin="dense"
            label="Skill Name"
            fullWidth
            value={name}
            onChange={(e) => setName(e.target.value)}
            error={!!errors.name}
            helperText={errors.name}
            disabled={isLoading}
            sx={{ mt: 2 }}
          />

          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            error={!!errors.description}
            helperText={errors.description}
            disabled={isLoading}
            sx={{ mt: 2 }}
            placeholder="Optional description for this skill"
          />
        </DialogContent>

        <DialogActions>
          <Button onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button type="submit" variant="contained" disabled={isLoading}>
            {isLoading ? <CircularProgress size={24} /> : "Update Skill"}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}
