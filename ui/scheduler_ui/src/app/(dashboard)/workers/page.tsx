"use client";

import { useState } from "react";
import { Box, Typography, Button } from "@mui/material";
import { Add as AddIcon } from "@mui/icons-material";
import { WorkersDataGrid } from "@/components/workers/WorkersDataGrid";
import { useRouter } from "next/navigation";

export default function WorkersPage() {
  const router = useRouter();
  const [formOpen, setFormOpen] = useState(false);

  const handleCreate = () => {
    router.push("/workers/new");
  };

  const handleEdit = (workerId: string) => {
    router.push(`/workers/${workerId}`);
  };

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
        <Typography variant="h4">Workers</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreate}
        >
          Add Worker
        </Button>
      </Box>

      <WorkersDataGrid onCreate={handleCreate} />
    </Box>
  );
}