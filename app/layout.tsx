import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Больше не буду меньше",
  description:
    "Адаптивный сайт-ридер для книги Саши Довгополовой с разворотами и оглавлением"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
