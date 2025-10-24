"use client"

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Button } from "@/components/ui/button"
import {
  MoreVertical,
  Play,
  Square,
  RotateCw,
  Edit,
  Trash2,
} from "lucide-react"
import type { RunnerInstanceOut } from "@/lib/api"

interface RunnerActionsProps {
  runner: RunnerInstanceOut
  onStart: (instance_id: number) => void
  onStop: (instance_id: number) => void
  onRestart: (instance_id: number) => void
  onEdit: (runner: RunnerInstanceOut) => void
  onDelete: (instance_id: number) => void
  loading?: boolean
}

export function RunnerActions({
  runner,
  onStart,
  onStop,
  onRestart,
  onEdit,
  onDelete,
  loading = false,
}: RunnerActionsProps) {
  const isOnline = runner.status === "online" || runner.status === "Online"
  const isOffline = runner.status === "offline" || runner.status === "Offline"

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="h-8 w-8">
          <MoreVertical className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        {isOffline && (
          <DropdownMenuItem
            onClick={() => onStart(runner.id)}
            disabled={loading}
            className="flex items-center gap-2"
          >
            <Play className="h-4 w-4" />
            Start
          </DropdownMenuItem>
        )}

        {isOnline && (
          <>
            <DropdownMenuItem
              onClick={() => onStop(runner.id)}
              disabled={loading}
              className="flex items-center gap-2"
            >
              <Square className="h-4 w-4" />
              Stop
            </DropdownMenuItem>

            <DropdownMenuItem
              onClick={() => onRestart(runner.id)}
              disabled={loading}
              className="flex items-center gap-2"
            >
              <RotateCw className="h-4 w-4" />
              Restart
            </DropdownMenuItem>
          </>
        )}

        <DropdownMenuSeparator />

        <DropdownMenuItem
          onClick={() => onEdit(runner)}
          disabled={loading}
          className="flex items-center gap-2"
        >
          <Edit className="h-4 w-4" />
          Edit
        </DropdownMenuItem>

        <DropdownMenuItem
          onClick={() => onDelete(runner.id)}
          disabled={loading}
          className="flex items-center gap-2 text-red-600"
        >
          <Trash2 className="h-4 w-4" />
          Delete
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
