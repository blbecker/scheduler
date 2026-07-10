"use client";

import { useState } from "react";
import React from "react";
import { Box, Typography } from "@mui/material";
import { useRouter } from "next/navigation";
import { ShiftTemplateDetailCard } from "@/components/shift-templates/ShiftTemplateDetailCard";
import { EditShiftTemplateForm } from "@/components/shift-templates/EditShiftTemplateForm";

interface ShiftTemplateDetailPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default function ShiftTemplateDetailPage({ params }: ShiftTemplateDetailPageProps) {
  const router = useRouter();
  const resolvedParams = React.use(params);
  const shiftTemplateId = resolvedParams.id;
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
    router.push("/shift-templates");
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4">Shift Template Details</Typography>
        <Typography variant="body2" color="text.secondary">
          View and manage shift template information
        </Typography>
      </Box>

      <ShiftTemplateDetailCard
        shiftTemplateId={shiftTemplateId}
        onEdit={handleEditClick}
        onDelete={handleDeleteSuccess}
      />

      <EditShiftTemplateForm
        open={editFormOpen}
        onClose={handleEditClose}
        onSuccess={handleEditSuccess}
        shiftTemplateId={shiftTemplateId}
      />
    </Box>
  );
}
