"use client"

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export default function AddRunnerModal({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
    <DialogContent className="sm:max-w-md" style={{ maxWidth: 600 }}>
      <DialogHeader>
        <DialogTitle>Add New Runner</DialogTitle>
      </DialogHeader>

      <div className="space-y-4 py-2">
        <div className="space-y-1">
        <Label>Runner Name</Label>
        <Input placeholder="e.g. production-runner-1" />
        </div>

        <div className="space-y-1">
        <Label>GitHub Repository URL</Label>
        <Input placeholder="https://github.com/username/repo" />
        </div>

        <div className="space-y-1">
        <Label>Access Token</Label>
        <Input placeholder="Enter GitHub PAT (Personal Access Token)" type="password" />
        </div>

        <div className="space-y-1">
        <Label>Labels</Label>
        <Input placeholder="Enter multiple labels separated by commas" />
        </div>
      </div>

      <DialogFooter>
        <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
        <Button>Add Runner</Button>
      </DialogFooter>
    </DialogContent>
    </Dialog>
  )
}
