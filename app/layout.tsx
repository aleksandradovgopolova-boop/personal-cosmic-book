import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Personal Cosmic Book",
  description:
    "Сервис генерации персональных digital-книг на основе натальной карты"
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
