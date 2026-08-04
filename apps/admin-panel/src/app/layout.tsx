import type { Metadata } from "next";
import { AppShell } from "@/components/layout/app-shell";
import { AppProviders } from "@/app/providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI VPS Management",
  description: "Admin panel for AI-assisted VPS monitoring and operations.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ar" dir="rtl">
      <body>
        <AppProviders>
          <AppShell>{children}</AppShell>
        </AppProviders>
      </body>
    </html>
  );
}
