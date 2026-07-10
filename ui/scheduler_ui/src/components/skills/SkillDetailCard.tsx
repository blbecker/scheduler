"use client";

import {
  ArrowBack as ArrowBackIcon,
  Build as BuildIcon,
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
import { useDeleteSkill, useGetSkill } from "@/api/client/skills/skills";
import { ConfirmationDialog } from "@/components/common/ConfirmationDialog";

interface SkillDetailCardProps {
  skillId: string;
  onEdit?: () => void;
  onDelete?: () => void;
}

export function SkillDetailCard({
  skillId,
  onEdit,
  onDelete,
}: SkillDetailCardProps) {
  const router = useRouter();
  const queryClient = useQueryClient();

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  const { data, isLoading, error } = useGetSkill(skillId);
  const deleteMutation = useDeleteSkill();

  const skill = data?.data;
  const isSkillResponse = skill && "name" in skill && "id" in skill;

  const handleDeleteClick = useCallback(() => {
    setDeleteDialogOpen(true);
  }, []);

  const handleDeleteConfirm = useCallback(async () => {
    try {
      await deleteMutation.mutateAsync({ skillId });
      queryClient.invalidateQueries({ queryKey: ["/api/v1/skills/"] });
      setDeleteDialogOpen(false);
      onDelete?.();
    } catch (error) {
      console.error("Failed to delete skill:", error);
    }
  }, [skillId, deleteMutation, queryClient, onDelete]);

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
        Error loading skill: {(error as Error).message}
      </Alert>
    );
  }

  if (!skill || !isSkillResponse) {
    return <Alert severity="warning">Skill not found</Alert>;
  }

  return (
    <>
      <Card>
        <CardContent>
          <Box sx={{ display: "flex", alignItems: "center", mb: 3, gap: 2 }}>
            <BuildIcon color="primary" sx={{ fontSize: 40 }} />
            <Box>
              <Typography variant="h5" component="div">
                {skill.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Skill ID: {skill.id}
              </Typography>
            </Box>
          </Box>

          <Divider sx={{ my: 2 }} />

          {skill.description && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Description
              </Typography>
              <Typography variant="body1" sx={{ whiteSpace: "pre-wrap" }}>
                {skill.description}
              </Typography>
            </Box>
          )}

          <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <CalendarIcon color="action" />
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Created
                </Typography>
                <Typography variant="body1">
                  {formatDate(skill.created_at)}
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
                  {formatDate(skill.updated_at)}
                </Typography>
              </Box>
            </Box>
          </Box>

          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>
              Assigned Workers (Coming Soon)
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Workers with this skill will be displayed here when the feature is implemented.
            </Typography>
          </Box>
        </CardContent>

        <CardActions sx={{ p: 2, justifyContent: "space-between" }}>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => router.push("/skills")}
          >
            Back to Skills
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
        title="Delete Skill"
        message={`Are you sure you want to delete skill "${skill.name}"? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
        severity="error"
      />
    </>
  );
}
