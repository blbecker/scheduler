"use client";

import { ArrowBack as ArrowBackIcon } from "@mui/icons-material";
import { Box, Button, Typography } from "@mui/material";
import { useRouter } from "next/navigation";
import { CreateWorkerCardForm } from "@/components/workers/CreateWorkerCardForm";

export default function CreateWorkerPage() {
  const router = useRouter();

  const handleSuccess = () => {
    router.push("/workers");
  };

  const handleCancel = () => {
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

      <CreateWorkerCardForm onSuccess={handleSuccess} onCancel={handleCancel} />
    </Box>
  );
}
