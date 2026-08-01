"use client";

import {
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  DarkMode as DarkModeIcon,
  Dashboard as DashboardIcon,
  LightMode as LightModeIcon,
  People as PeopleIcon,
  Build as BuildIcon,
  CalendarToday as CalendarTodayIcon,
  AvTimer as AvTimerIcon,
  CalendarMonth as CalendarMonthIcon,
  Work as WorkIcon,
  Calculate as CalculateIcon,
} from "@mui/icons-material";
import {
  Box,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Tooltip,
  Typography,
  useTheme,
} from "@mui/material";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { useTheme as useAppTheme } from "@/hooks/useTheme";

const DRAWER_WIDTH = 240;
const COLLAPSED_WIDTH = 64;

const navigationItems = [
  { label: "Dashboard", icon: <DashboardIcon />, path: "/" },
  { label: "Workers", icon: <PeopleIcon />, path: "/workers" },
  { label: "Skills", icon: <BuildIcon />, path: "/skills" },
  { label: "Schedule Templates", icon: <CalendarTodayIcon />, path: "/schedule-templates" },
  { label: "Shift Templates", icon: <AvTimerIcon />, path: "/shift-templates" },
  { label: "Schedules", icon: <CalendarMonthIcon />, path: "/schedules" },
  { label: "Shifts", icon: <WorkIcon />, path: "/shifts" },
  { label: "Schedule Solves", icon: <CalculateIcon />, path: "/solves" },
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
                    sx={{
                      "& .MuiListItemText-primary": {
                        color: isActive(item.path) ? "primary.main" : "inherit",
                      },
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
            suppressHydrationWarning
          >
            {mode === "dark" ? <LightModeIcon /> : <DarkModeIcon />}
            {!collapsed && (
              <Typography sx={{ ml: 2 }} suppressHydrationWarning>
                {mode === "dark" ? "Light Mode" : "Dark Mode"}
              </Typography>
            )}
          </IconButton>
        </Tooltip>
      </Box>
    </Drawer>
  );
}
