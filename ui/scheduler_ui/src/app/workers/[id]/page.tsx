"use client";

import { useState } from "react";
import React from "react";
import { Box, Typography } from "@mui/material";
import { useRouter } from "next/navigation";
import { WorkerDetailCard } from "@/components/workers/WorkerDetailCard";
import { EditWorkerForm } from "@/components/workers/EditWorkerForm";

interface WorkerDetailPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default function WorkerDetailPage({ params }: WorkerDetailPageProps) {
  const router = useRouter();
  const resolvedParams = React.use(params);
  const workerId = resolvedParams.id;
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
    router.push("/workers");
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4">Worker Details</Typography>
        <Typography variant="body2" color="text.secondary">
          View and manage worker information
        </Typography>
      </Box>

      <WorkerDetailCard
        workerId={workerId}
        onEdit={handleEditClick}
        onDelete={handleDeleteSuccess}
      />

      <EditWorkerForm
        open={editFormOpen}
        onClose={handleEditClose}
        onSuccess={handleEditSuccess}
        workerId={workerId}
      />
    </Box>
  );
}
