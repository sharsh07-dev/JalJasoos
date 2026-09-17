import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "JalJasoos Command Center",
  description: "Water Pipeline Monitoring & Automation",
};

import { AuthProvider } from "@/contexts/AuthContext";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased dark">
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
