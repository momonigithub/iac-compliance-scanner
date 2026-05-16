import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import clsx from "clsx";
import { Toaster } from "sonner";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });

export const metadata: Metadata = {
  title: "IaC Compliance Scanner",
  description: "Automated Infrastructure-as-Code security auditing tool.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body
        className={clsx(
          "min-h-screen bg-background font-sans antialiased selection:bg-primary selection:text-primary-foreground",
          inter.variable
        )}
      >
        {children}
        <Toaster position="bottom-center" theme="light" />
      </body>
    </html>
  );
}
