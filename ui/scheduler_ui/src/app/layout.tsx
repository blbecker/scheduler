import type { Metadata } from "next";
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
            <QueryProvider>{children}</QueryProvider>
          </MuiProvider>
        </EmotionRegistry>
      </body>
    </html>
  );
}
