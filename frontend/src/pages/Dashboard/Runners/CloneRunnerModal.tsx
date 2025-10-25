"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { LoaderCircle } from "lucide-react"
import { toast } from "sonner"
import { cloneRunnerApi } from "./service"

interface CloneRunnerModalProps {
  open: boolean
  onOpenChange: (v: boolean) => void
  instanceId?: number
  onSuccess?: () => void
}

export default function CloneRunnerModal({ 
  open, 
  onOpenChange, 
  instanceId,
  onSuccess 
}: CloneRunnerModalProps) {
  const [count, setCount] = useState<number>(1)
  const [token, setToken] = useState<string>("")
  const [isLoading, setIsLoading] = useState(false)

  const handleClone = async () => {
    if (!instanceId) {
      toast.error("Instance ID not found", {
        style: {
          background: "#fee2e2",
          color: "#991b1b",
          border: "1px solid #fecaca",
        },
      })
      return
    }

    if (count < 1) {
      toast.error("Count must be at least 1", {
        style: {
          background: "#fee2e2",
          color: "#991b1b",
          border: "1px solid #fecaca",
        },
      })
      return
    }

    setIsLoading(true)
    try {
      const result = await cloneRunnerApi(instanceId, count, token || undefined)
      if (result.success) {
        toast.success(`Runner cloned successfully (${count} clone${count > 1 ? "s" : ""})`)
        setCount(1)
        setToken("")
        onOpenChange(false)
        if (onSuccess) {
          onSuccess()
        }
      } else {
        toast.error(result.message || "Failed to clone runner", {
          style: {
            background: "#fee2e2",
            color: "#991b1b",
            border: "1px solid #fecaca",
          },
        })
      }
    } catch (error: any) {
      console.error("Error cloning runner:", error)
      toast.error("Failed to clone runner", {
        style: {
          background: "#fee2e2",
          color: "#991b1b",
          border: "1px solid #fecaca",
        },
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleClose = () => {
    setCount(1)
    setToken("")
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-sm">
        <DialogHeader>
          <DialogTitle>Clone Runner</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-2">
          <div className="space-y-1">
            <Label htmlFor="count">Number of Clones</Label>
            <Input
              id="count"
              placeholder="Number of clones to create"
              type="number"
              min="1"
              value={count}
              onChange={(e) => setCount(Math.max(1, parseInt(e.target.value) || 1))}
              disabled={isLoading}
            />
          </div>

          <div className="space-y-1">
            <Label htmlFor="token">Access Token (Optional)</Label>
            <Input
              id="token"
              placeholder="Enter access token for clones (if different)"
              type="password"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              disabled={isLoading}
            />
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={handleClose}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            onClick={handleClone}
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <LoaderCircle className="w-4 h-4 mr-2 animate-spin" />
                Cloning...
              </>
            ) : (
              "Clone"
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
