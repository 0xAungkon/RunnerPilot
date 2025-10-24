"use client"

import { useState, useEffect, useRef } from "react"
import { X, Trash2, LoaderCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { toast } from "sonner"
import { getRunnerLogsApi, clearRunnerLogsApi } from "./service"

interface LogsPopupProps {
  open: boolean
  onClose: () => void
  instanceId?: number
}

export default function LogsPopup({ open, onClose, instanceId }: LogsPopupProps) {
    const [logs, setLogs] = useState<string[]>([])
    const [isLoading, setIsLoading] = useState(false)
    const [isClearing, setIsClearing] = useState(false)
    const logsEndRef = useRef<HTMLDivElement>(null)
    const abortControllerRef = useRef<AbortController | null>(null)

    // Auto-scroll to bottom when new logs arrive
    useEffect(() => {
      logsEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [logs])

    // Fetch logs when modal opens
    useEffect(() => {
      if (!open || !instanceId) return

      const fetchLogs = async () => {
        setIsLoading(true)
        setLogs([])
        
        // Create abort controller for this stream
        abortControllerRef.current = new AbortController()

        try {
          for await (const logEntry of getRunnerLogsApi(instanceId, abortControllerRef.current.signal)) {
            if (logEntry.status === "error") {
              toast.error(logEntry.message || "Failed to fetch logs", {
                style: {
                  background: "#fee2e2",
                  color: "#991b1b",
                  border: "1px solid #fecaca",
                },
              })
              break
            }

            if (logEntry.log) {
              setLogs((prevLogs) => [...prevLogs, logEntry.log])
            }
          }
        } catch (error: any) {
          // Don't show error if aborted (user closed modal)
          if (error.name !== "AbortError") {
            console.error("Error fetching logs:", error)
            toast.error("Failed to fetch logs", {
              style: {
                background: "#fee2e2",
                color: "#991b1b",
                border: "1px solid #fecaca",
              },
            })
          }
        } finally {
          setIsLoading(false)
        }
      }

      fetchLogs()

      // Cleanup function to close connection when modal closes
      return () => {
        if (abortControllerRef.current) {
          abortControllerRef.current.abort()
        }
      }
    }, [open, instanceId])

    const handleClearLogs = async () => {
      if (!instanceId) return

      setIsClearing(true)
      const result = await clearRunnerLogsApi(instanceId)
      if (result.success) {
        setLogs([])
        toast.success("Logs cleared successfully")
      } else {
        toast.error(result.message || "Failed to clear logs", {
          style: {
            background: "#fee2e2",
            color: "#991b1b",
            border: "1px solid #fecaca",
          },
        })
      }
      setIsClearing(false)
    }


  if (!open) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex justify-center items-center z-50 ">
    <div className="bg-background w-3/4 max-w-2xl h-3/4 rounded-lg shadow-lg flex flex-col border-[5px] border-gray-600">
        {/* Header */}
        <div className="flex justify-between items-center border-b border-border p-2" >
          <span className="font-medium">Logs {isLoading && <span className="ml-2 text-xs text-muted-foreground">(Loading...)</span>}</span>
          <div className="flex items-center gap-2">
            <Button
              size="icon"
              variant="outline"
              className="h-6 w-6 p-1"
              onClick={handleClearLogs}
              disabled={isClearing || logs.length === 0}
            >
              <Trash2 className="w-4 h-4" />
            </Button>
            <Button
              size="icon"
              variant="outline"
              className="h-6 w-6 p-1"
              onClick={onClose}
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Logs Body */}
        <div className="flex-1 p-2 bg-black text-green-400 font-mono overflow-y-auto text-sm">
          {isLoading && logs.length === 0 ? (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              <div className="flex flex-col items-center gap-2">
                <LoaderCircle className="w-6 h-6 animate-spin" />
                <span>Connecting to logs...</span>
              </div>
            </div>
          ) : logs.length === 0 ? (
            <div className="text-gray-500">No logs available</div>
          ) : (
            <>
              {logs.map((log, idx) => <div key={idx}>{log}</div>)}
              <div ref={logsEndRef} />
            </>
          )}
        </div>
      </div>
    </div>
  )
}
