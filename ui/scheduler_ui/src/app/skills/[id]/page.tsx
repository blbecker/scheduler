"use client";

import { useState } from "react";
import React from "react";
import { Box, Typography } from "@mui/material";
import { useRouter } from "next/navigation";
import { SkillDetailCard } from "@/components/skills/SkillDetailCard";
import { EditSkillForm } from "@/components/skills/EditSkillForm";

interface SkillDetailPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default function SkillDetailPage({ params }: SkillDetailPageProps) {
  const router = useRouter();
  const resolvedParams = React.use(params);
  const skillId = resolvedParams.id;
  const [editFormOpen, setEditFormOpen] = useState(false);

  const handleEditClick = () => {
    setEditFormOpen(true);
  };

  const handleEditClose = () => {
    setEditFormOpen(false);
  };

  const handleEditSuccess = () => {
    setEditFormOpen(false);
  };

  const handleDeleteSuccess = () => {
    router.push("/skills");
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4">Skill Details</Typography>
        <Typography variant="body2" color="text.secondary">
          View and manage skill information
        </Typography>
      </Box>

      <SkillDetailCard
        skillId={skillId}
        onEdit={handleEditClick}
        onDelete={handleDeleteSuccess}
      />

      <EditSkillForm
        open={editFormOpen}
        onClose={handleEditClose}
        onSuccess={handleEditSuccess}
        skillId={skillId}
      />
    </Box>
  );
}