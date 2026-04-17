import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'PropIQ — Property Investment Intelligence',
  description: 'Analyze any U.S. property. Get property details, neighborhood data, and market intelligence.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-slate text-ink min-h-screen">
        {children}
      </body>
    </html>
  );
}
