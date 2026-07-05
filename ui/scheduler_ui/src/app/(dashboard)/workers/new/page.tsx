"use client";

import { Box, Typography, Button } from "@mui/material";
import { ArrowBack as ArrowBackIcon } from "@mui/icons-material";
import { useRouter } from "next/navigation";
import { WorkerForm } from "@/components/workers/WorkerForm";

export default function CreateWorkerPage() {
  const router = useRouter();

  const handleSuccess = () => {
    router.push("/workers");
  };

  const handleClose = () => {
    router.back();
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => router.push("/workers")}
          sx={{ mb: 2 }}
        >
          Back to Workers
        </Button>
        
        <Typography variant="h4">Add New Worker</Typography>
        <Typography variant="body2" color="text.secondary">
          Create a new worker by providing the required information
        </Typography>
      </Box>

      <WorkerForm
        open={true}
        onClose={handleClose}
        onSuccess={handleSuccess}
        mode="create"
      />
    </Box>
  );
}