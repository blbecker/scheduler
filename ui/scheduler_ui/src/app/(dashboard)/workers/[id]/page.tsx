"use client";

import { useState } from "react";
import { Box, Typography, Button } from "@mui/material";
import { useRouter } from "next/navigation";
import { WorkerDetailCard } from "@/components/workers/WorkerDetailCard";
import { WorkerForm } from "@/components/workers/WorkerForm";

interface WorkerDetailPageProps {
  params: {
    id: string;
  };
}

export default function WorkerDetailPage({ params }: WorkerDetailPageProps) {
  const router = useRouter();
  const workerId = params.id;
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

      <WorkerForm
        open={editFormOpen}
        onClose={handleEditClose}
        onSuccess={handleEditSuccess}
        workerId={workerId}
        mode="edit"
      />
    </Box>
  );
}