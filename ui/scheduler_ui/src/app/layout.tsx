import { AppRouterCacheProvider } from "@mui/material-nextjs/v16-appRouter";
import type { Metadata } from "next";
import { MainLayout } from "@/components/layout/MainLayout";
import EmotionRegistry from "@/lib/emotion-registry";
import { MuiProvider } from "@/providers/mui-provider";
import { QueryProvider } from "@/providers/query-provider";

export const metadata: Metadata = {
  title: "Scheduler",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <EmotionRegistry>
          <MuiProvider>
            <QueryProvider>
              <AppRouterCacheProvider>
                <MainLayout>{children}</MainLayout>
              </AppRouterCacheProvider>
            </QueryProvider>
          </MuiProvider>
        </EmotionRegistry>
      </body>
    </html>
  );
}
