"use client"

import {
  BarChart,
  Server,
  Layers,
  FileText, // changed for Event Logs
  LifeBuoy,
  Users,
  Settings,
  BookOpen,
} from "lucide-react"
import { useNavigate } from "react-router-dom"
import { routes } from "@/lib/routes"

export default function Navigation() {
  const navigate = useNavigate()
  const navItems = [
    { icon: BarChart, label: "Overview", route: routes.dashboard },
    { icon: Server, label: "Runners", route: routes.runners },
    { icon: Layers, label: "Nodes", route: routes.nodes },
    { icon: FileText, label: "Event Logs", route: routes.events },
    { icon: LifeBuoy, label: "Support", route: routes.support },
    { icon: Users, label: "Workspace Users", route: routes.users },
    { icon: Settings, label: "Settings", route: routes.settings },
  ]

  return (
    <nav className="border-b bg-background text-foreground">
      <div className="flex items-center gap-6 max-w-7xl mx-auto px-6">
        {navItems.map(({ icon: Icon, label, route }) => (
          <button
            key={label}
            onClick={() => navigate(route)}
            className="flex items-center gap-2 border-b-2 px-1 py-4 text-sm font-medium transition-colors border-transparent text-muted-foreground hover:text-foreground"
          >
            <Icon className="h-4 w-4" />
            {label}
          </button>
        ))}

        <button className="ml-auto flex items-center gap-2 px-1 py-4 text-sm text-muted-foreground hover:text-foreground transition-colors">
          <BookOpen className="h-4 w-4" />
          Resource hub
        </button>
      </div>
    </nav>
  )
}
