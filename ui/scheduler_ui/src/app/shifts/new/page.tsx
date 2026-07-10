"use client";

import { Box, Button, Typography } from "@mui/material";
import { ArrowBack as ArrowBackIcon } from "@mui/icons-material";
import { useRouter } from "next/navigation";
import { CreateShiftCardForm } from "@/components/shifts";

export default function NewShiftPage() {
  const router = useRouter();

  const handleSuccess = () => {
    router.push("/shifts");
  };

  return (
    <Box>
      <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 3 }}>
        <Button startIcon={<ArrowBackIcon />} onClick={() => router.push("/shifts")}>
          Back
        </Button>
        <Typography variant="h4">Create New Shift</Typography>
      </Box>

      <CreateShiftCardForm onSuccess={handleSuccess} />
    </Box>
  );
}
