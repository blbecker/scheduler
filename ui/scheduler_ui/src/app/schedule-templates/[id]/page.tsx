"use client";

import { useState } from "react";
import React from "react";
import { Box, Typography } from "@mui/material";
import { useRouter } from "next/navigation";
import { ScheduleTemplateDetailCard } from "@/components/schedule-templates/ScheduleTemplateDetailCard";
import { EditScheduleTemplateForm } from "@/components/schedule-templates/EditScheduleTemplateForm";

interface ScheduleTemplateDetailPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default function ScheduleTemplateDetailPage({ params }: ScheduleTemplateDetailPageProps) {
  const router = useRouter();
  const resolvedParams = React.use(params);
  const scheduleTemplateId = resolvedParams.id;
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
    router.push("/schedule-templates");
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4">Schedule Template Details</Typography>
        <Typography variant="body2" color="text.secondary">
          View and manage schedule template information
        </Typography>
      </Box>

      <ScheduleTemplateDetailCard
        scheduleTemplateId={scheduleTemplateId}
        onEdit={handleEditClick}
        onDelete={handleDeleteSuccess}
      />

      <EditScheduleTemplateForm
        open={editFormOpen}
        onClose={handleEditClose}
        onSuccess={handleEditSuccess}
        scheduleTemplateId={scheduleTemplateId}
      />
    </Box>
  );
}