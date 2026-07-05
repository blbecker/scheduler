"use client";

import { Button } from "@mui/material";
import { Download as DownloadIcon } from "@mui/icons-material";

interface ExportButtonProps<T> {
  data: T[];
  filename?: string;
  getRowData: (item: T) => string[];
  getHeaders: () => string[];
  disabled?: boolean;
}

export function ExportButton<T>({
  data,
  filename = "export",
  getRowData,
  getHeaders,
  disabled = false,
}: ExportButtonProps<T>) {
  const exportToCsv = () => {
    if (data.length === 0) return;

    const headers = getHeaders();
    const rows = data.map((item) => getRowData(item));

    // Format CSV content
    const csvContent = [
      headers.join(","),
      ...rows.map((row) =>
        row
          .map((cell) => {
            // Escape quotes and wrap in quotes if contains comma, quote, or newline
            const escaped = cell.toString().replace(/"/g, '""');
            if (escaped.includes(",") || escaped.includes('"') || escaped.includes("\n")) {
              return `"${escaped}"`;
            }
            return escaped;
          })
          .join(",")
      ),
    ].join("\n");

    // Create and trigger download
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", `${filename}-${new Date().toISOString().split("T")[0]}.csv`);
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Button
      variant="outlined"
      startIcon={<DownloadIcon />}
      onClick={exportToCsv}
      disabled={disabled || data.length === 0}
      size="small"
    >
      Export CSV
    </Button>
  );
}