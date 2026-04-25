import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Internal Knowledge Copilot",
  description: "Enterprise-style AI knowledge assistant with grounded answers and admin controls."
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
