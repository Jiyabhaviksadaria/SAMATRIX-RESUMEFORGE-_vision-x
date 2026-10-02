import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "ResumeForge AI — Resume Intelligence Hackathon Kit",
  description: "Modular, dataset-independent NLP & ML starter kit for resume intelligence hackathons.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-slate-950 text-slate-100 antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
