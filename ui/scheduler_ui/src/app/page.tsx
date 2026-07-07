"use client";

import { Add as AddIcon, People as PeopleIcon } from "@mui/icons-material";
import { Box, Button, Card, CardContent, Typography } from "@mui/material";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const router = useRouter();

  const handleNavigateToWorkers = () => {
    router.push("/workers");
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1200, margin: "0 auto" }}>
      <Typography variant="h4" gutterBottom>
        Welcome to Scheduler
      </Typography>

      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Manage your workforce, schedules, and optimize assignments with our
        scheduling system.
      </Typography>

      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 3, mt: 2 }}>
        <Box sx={{ flex: "1 1 300px", minWidth: 300 }}>
          <Card>
            <CardContent>
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  mb: 2,
                }}
              >
                <Typography variant="h6">Workers</Typography>
                <PeopleIcon color="primary" />
              </Box>

              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Manage your workforce. Add, edit, or remove workers from the
                system.
              </Typography>

              <Box sx={{ display: "flex", gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<PeopleIcon />}
                  onClick={handleNavigateToWorkers}
                >
                  View Workers
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<AddIcon />}
                  onClick={() => router.push("/workers/new")}
                >
                  Add Worker
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Box>

        <Box sx={{ flex: "1 1 300px", minWidth: 300 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Stats
              </Typography>

              <Typography variant="body2" color="text.secondary">
                More features coming soon: Skills management, schedule
                templates, and optimization tools.
              </Typography>
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Box>
  );
}
