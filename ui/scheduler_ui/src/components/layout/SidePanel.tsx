"use client";

import { useState } from "react";
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Typography,
  useTheme,
  Divider,
  Tooltip,
} from "@mui/material";
import {
  Menu as MenuIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  People as PeopleIcon,
  Dashboard as DashboardIcon,
  LightMode as LightModeIcon,
  DarkMode as DarkModeIcon,
} from "@mui/icons-material";
import { useTheme as useAppTheme } from "@/hooks/useTheme";
import { useRouter, usePathname } from "next/navigation";

const DRAWER_WIDTH = 240;
const COLLAPSED_WIDTH = 64;

const navigationItems = [
  { label: "Dashboard", icon: <DashboardIcon />, path: "/" },
  { label: "Workers", icon: <PeopleIcon />, path: "/workers" },
];

export function SidePanel() {
  const [collapsed, setCollapsed] = useState(false);
  const theme = useTheme();
  const { mode, toggleTheme } = useAppTheme();
  const router = useRouter();
  const pathname = usePathname();

  const handleNavigation = (path: string) => {
    router.push(path);
  };

  const isActive = (path: string) => {
    if (path === "/") return pathname === "/";
    return pathname?.startsWith(path);
  };

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: collapsed ? COLLAPSED_WIDTH : DRAWER_WIDTH,
        flexShrink: 0,
        "& .MuiDrawer-paper": {
          width: collapsed ? COLLAPSED_WIDTH : DRAWER_WIDTH,
          boxSizing: "border-box",
          transition: theme.transitions.create("width", {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
          overflowX: "hidden",
        },
      }}
    >
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          p: 2,
          minHeight: 64,
        }}
      >
        {!collapsed && (
          <Typography variant="h6" noWrap component="div">
            Scheduler
          </Typography>
        )}
        <IconButton onClick={() => setCollapsed(!collapsed)}>
          {collapsed ? <ChevronRightIcon /> : <ChevronLeftIcon />}
        </IconButton>
      </Box>
      
      <Divider />
      
      <List sx={{ flex: 1 }}>
        {navigationItems.map((item) => (
          <ListItem key={item.label} disablePadding sx={{ display: "block" }}>
            <Tooltip title={collapsed ? item.label : ""} placement="right">
              <ListItemButton
                selected={isActive(item.path)}
                onClick={() => handleNavigation(item.path)}
                sx={{
                  minHeight: 48,
                  justifyContent: collapsed ? "center" : "initial",
                  px: 2.5,
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 0,
                    mr: collapsed ? 0 : 2,
                    justifyContent: "center",
                    color: isActive(item.path) ? "primary.main" : "inherit",
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                {!collapsed && (
                  <ListItemText
                    primary={item.label}
                    primaryTypographyProps={{
                      color: isActive(item.path) ? "primary.main" : "inherit",
                    }}
                  />
                )}
              </ListItemButton>
            </Tooltip>
          </ListItem>
        ))}
      </List>
      
      <Divider />
      
      <Box sx={{ p: 2 }}>
        <Tooltip title={collapsed ? "Toggle theme" : ""} placement="right">
          <IconButton
            onClick={toggleTheme}
            sx={{
              width: "100%",
              justifyContent: collapsed ? "center" : "flex-start",
            }}
          >
            {mode === "dark" ? <LightModeIcon /> : <DarkModeIcon />}
            {!collapsed && (
              <Typography sx={{ ml: 2 }}>
                {mode === "dark" ? "Light Mode" : "Dark Mode"}
              </Typography>
            )}
          </IconButton>
        </Tooltip>
      </Box>
    </Drawer>
  );
}