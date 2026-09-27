import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RepoLens",
  description: "Analyze GitHub repositories with ease",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col">
        <header className="bg-gray-800 text-white p-4">
          <div className="container mx-auto">
            <h1 className="text-2xl font-bold">
              <a href="/" className="hover:underline">RepoLens</a>
            </h1>
            <p className="text-sm">Analyze public GitHub repositories quickly.</p>
          </div>
        </header>
        <main className="flex-grow container mx-auto p-4">{children}</main>
        <footer className="bg-gray-200 text-center py-2 text-sm">© 2026 RepoLens</footer>
      </body>
    </html>
  );
}
