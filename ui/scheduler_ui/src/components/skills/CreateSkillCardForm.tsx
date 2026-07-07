"use client";

import {
  Alert,
  Button,
  Card,
  CardActions,
  CardContent,
  CircularProgress,
  TextField,
  Typography,
} from "@mui/material";
import { useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useCreateSkill } from "@/api/client/skills/skills";
import type { SkillCreate } from "@/api/models";

interface CreateSkillCardFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function CreateSkillCardForm({
  onSuccess,
  onCancel,
}: CreateSkillCardFormProps) {
  const queryClient = useQueryClient();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});

  const createMutation = useCreateSkill();

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
      const createData: SkillCreate = {
        name,
        description: description.trim() || null,
      };
      await createMutation.mutateAsync({ data: createData });

      queryClient.invalidateQueries({ queryKey: ["/api/v1/skills/"] });

      onSuccess?.();
    } catch (error) {
      console.error("Failed to create skill:", error);
      setErrors({
        submit: "Failed to create skill. Please try again.",
      });
    }
  };

  const isLoading = createMutation.isPending;

  const getMutationErrorMessage = () => {
    if (!createMutation.error) return "";

    const err = createMutation.error;
    if (err instanceof Error) return err.message;
    if (typeof err === "object" && err !== null && "message" in err) {
      return String((err as { message: string }).message);
    }
    return String(err);
  };

  const submitError = errors.submit || getMutationErrorMessage();
  const displayError = submitError;

  return (
    <Card sx={{ maxWidth: 600, mx: "auto" }}>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          Add New Skill
        </Typography>

        <form onSubmit={handleSubmit}>
          {displayError ? (
            <Alert severity="error" sx={{ mb: 2 }}>
              {displayError}
            </Alert>
          ) : null}

          <TextField
            autoFocus
            fullWidth
            label="Skill Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            error={!!errors.name}
            helperText={errors.name}
            disabled={isLoading}
            sx={{ mt: 2, mb: 2 }}
          />

          <TextField
            fullWidth
            multiline
            rows={3}
            label="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            error={!!errors.description}
            helperText={errors.description}
            disabled={isLoading}
            sx={{ mb: 2 }}
            placeholder="Optional description for this skill"
          />
        </form>
      </CardContent>

      <CardActions sx={{ p: 2, justifyContent: "flex-end" }}>
        <Button onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button
          type="submit"
          variant="contained"
          disabled={isLoading}
          onClick={handleSubmit}
        >
          {isLoading ? <CircularProgress size={24} /> : "Create Skill"}
        </Button>
      </CardActions>
    </Card>
  );
}