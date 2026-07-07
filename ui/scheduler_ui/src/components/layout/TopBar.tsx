"use client";

import { Menu as MenuIcon } from "@mui/icons-material";
import { AppBar, Box, IconButton, Toolbar, Typography } from "@mui/material";

interface TopBarProps {
  title?: string;
  onMenuClick?: () => void;
}

export function TopBar({ title = "Scheduler", onMenuClick }: TopBarProps) {
  return (
    <AppBar
      position="fixed"
      sx={{
        zIndex: (theme) => theme.zIndex.drawer + 1,
        backgroundColor: "background.paper",
        color: "text.primary",
        boxShadow: "none",
        borderBottom: 1,
        borderColor: "divider",
      }}
    >
      <Toolbar>
        <IconButton
          color="inherit"
          aria-label="open drawer"
          onClick={onMenuClick}
          edge="start"
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>

        <Box sx={{ flexGrow: 1 }}>
          <Typography variant="h6" noWrap component="div">
            {title}
          </Typography>
        </Box>
      </Toolbar>
    </AppBar>
  );
}
