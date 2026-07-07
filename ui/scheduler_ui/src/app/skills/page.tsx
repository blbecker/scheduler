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
import { useListSkills, useDeleteSkill } from "@/api/client/skills/skills";
import { useQueryClient } from "@tanstack/react-query";
import { ConfirmationDialog } from "@/components/common/ConfirmationDialog";
import { ExportButton } from "@/components/common/ExportButton";
import { SkillsTable } from "@/components/skills/SkillsTable";
import { SkillResponse } from "@/api/models";

export default function SkillsPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState("");
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [skillToDelete, setSkillToDelete] = useState<SkillResponse | null>(
    null,
  );

  const { data, isLoading, error } = useListSkills();

  const skills = useMemo(() => {
    if (!data) return [];
    return Array.isArray(data) ? data : data.data || [];
  }, [data]);

  const deleteMutation = useDeleteSkill();

  const filteredSkills = useMemo(() => {
    if (!searchTerm.trim()) return skills;
    const term = searchTerm.toLowerCase();
    return skills.filter(
      (skill) =>
        skill.name.toLowerCase().includes(term) ||
        skill.id.toLowerCase().includes(term) ||
        (skill.description && skill.description.toLowerCase().includes(term)),
    );
  }, [skills, searchTerm]);

  const handleDeleteClick = useCallback((skill: SkillResponse) => {
    setSkillToDelete(skill);
    setDeleteDialogOpen(true);
  }, []);

  const handleDeleteConfirm = useCallback(async () => {
    if (!skillToDelete) return;
    try {
      await deleteMutation.mutateAsync({ skillId: skillToDelete.id });
      queryClient.invalidateQueries({ queryKey: ["/api/v1/skills/"] });
      setDeleteDialogOpen(false);
      setSkillToDelete(null);
    } catch (error) {
      console.error("Failed to delete skill:", error);
    }
  }, [skillToDelete, deleteMutation, queryClient]);

  const handleDeleteCancel = useCallback(() => {
    setDeleteDialogOpen(false);
    setSkillToDelete(null);
  }, []);

  const handleView = useCallback(
    (skillId: string) => {
      router.push(`/skills/${skillId}`);
    },
    [router],
  );

  const handleCreate = () => {
    router.push("/skills/new");
  };

  const hasError = error || (data && data.status && data.status !== 200);
  if (hasError) {
    return <Alert severity="error">Error loading skills.</Alert>;
  }

  if (isLoading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (skills.length === 0) {
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
          <Typography variant="h4">Skills</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreate}
          >
            Add Skill
          </Button>
        </Box>
        <Box sx={{ textAlign: "center", p: 4 }}>
          <Typography variant="h6" gutterBottom>
            No skills found
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Get started by adding your first skill.
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreate}
          >
            Add First Skill
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
        <Typography variant="h4">Skills</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreate}
        >
          Add Skill
        </Button>
      </Box>

      <Box sx={{ mb: 2, display: "flex", gap: 1, alignItems: "center" }}>
        <TextField
          size="small"
          placeholder="Search skills..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{ width: 300 }}
        />

        <ExportButton<SkillResponse>
          data={filteredSkills}
          filename="skills"
          getHeaders={() => ["ID", "Name", "Description", "Created At", "Updated At"]}
          getRowData={(skill) => [
            skill.id,
            skill.name,
            skill.description || "",
            skill.created_at,
            skill.updated_at,
          ]}
          disabled={filteredSkills.length === 0}
        />
      </Box>

      <SkillsTable
        skills={filteredSkills}
        onView={handleView}
        onDelete={handleDeleteClick}
      />

      <ConfirmationDialog
        open={deleteDialogOpen}
        title="Delete Skill"
        message={`Are you sure you want to delete "${skillToDelete?.name}"?`}
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
      />
    </Box>
  );
}