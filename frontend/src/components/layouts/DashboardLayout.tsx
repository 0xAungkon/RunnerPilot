"use client"

import type { FC } from "react"
import { Outlet } from "react-router-dom"
import Header from "./fragments/Header"
import Navigation from "./fragments/Navigation"
import { useTheme } from "next-themes"

interface DashboardLayoutProps {
  title: string
  subtitle?: string
  link?: string
}

const DashboardLayout: FC<DashboardLayoutProps> = ({ title, subtitle, link }) => {
  const { theme } = useTheme()

  return (
    <div className="min-h-screen bg-background text-foreground transition-colors duration-300">
      {/* Header */}
      <Header />

      {/* Navigation */}
      <Navigation />

      {/* Main */}
      <main className="py-10 max-w-7xl mx-auto px-6">
        <div className="mb-8">
          <h1 className="mb-2 text-3xl font-semibold">{title}</h1>
          {subtitle && (
            <p className="text-muted-foreground text-sm">
              {subtitle}
              {link && (
                <>
                  .{" "}
                  <a href={link} className="text-primary hover:underline">
                    Learn more
                  </a>
                </>
              )}
            </p>
          )}
        </div>

        <Outlet />
      </main>
    </div>
  )
}

export default DashboardLayout
