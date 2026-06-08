#!/usr/bin/env ts-node
/**
 * layout.tsx --- root layout for the llmjudge dashboard
 *
 * Contains:
 *   RootLayout: wraps every page with the app shell
 */

import "./globals.css";

export const metadata = {
  title: "llmjudge",
  description: "LLM evaluation regression dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="app-header">
          <h1>llmjudge</h1>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
