"use client"

import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Filter, Download, Plus, MoreVertical } from "lucide-react"

const machines = [
  {
    name: "monika-latitude-3410",
    owner: "monikapal69420@gmail.com",
    address: "100.70.233.117",
    version: "1.86.2",
    os: "Linux 6.11.0-29-generic",
    lastSeen: "Sep 24",
    status: "Offline",
    shared: true,
    funnel: false,
    exitNode: false,
  },
  {
    name: "hpx360",
    owner: "tajdrivestorage1@gmail.com",
    address: "100.88.19.50",
    version: "1.86.2",
    os: "Windows 11 24H2",
    lastSeen: "Oct 6, 8:23 PM GMT+6",
    status: "Offline",
    shared: true,
    funnel: false,
    exitNode: false,
  },
  {
    name: "0x-personal-dell",
    owner: "aungkonmalakar@gmail.com",
    address: "100.98.85.42",
    version: "1.86.2",
    os: "Linux 6.12.38+kali-amd64",
    lastSeen: "Connected",
    status: "Online",
    shared: false,
    funnel: true,
    exitNode: true,
  },
]

export default function MachineList() {
  return (
    <div className="min-h-screen bg-background text-foreground p-6">
      {/* Toolbar */}
      <div className="flex justify-between items-center mb-5">
        <div className="w-1/2">
          <Input
            placeholder="Search by name, owner, tag, version..."
            className="h-8 text-sm bg-muted text-foreground border border-border"
          />
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" className="h-8 px-3 text-xs gap-1">
            <Filter className="w-3.5 h-3.5" />
            Filters
          </Button>
          <Button variant="outline" size="icon" className="h-8 w-8">
            <Download className="w-3.5 h-3.5" />
          </Button>
          <Button className="h-8 px-3 text-xs gap-1">
            <Plus className="w-3.5 h-3.5" />
            Add
          </Button>
        </div>
      </div>

      {/* List Header */}
      <div className="grid grid-cols-[1.5fr_1.5fr_1fr_1fr_0.5fr] text-xs font-medium text-muted-foreground border-b border-border pb-2 mb-1">
        <div>Name / Owner</div>
        <div>Address</div>
        <div>Version</div>
        <div>Last Seen</div>
        <div className="text-right pr-2">Actions</div>
      </div>

      {/* Machine Rows */}
      <div className="divide-y divide-border text-xs">
        {machines.map((machine, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2, delay: idx * 0.04 }}
            className="grid grid-cols-[1.5fr_1.5fr_1fr_1fr_0.5fr] items-center py-2.5 hover:bg-muted/40 transition-colors"
          >
            {/* Name + Owner + Tags */}
            <div>
                <div className="font-medium text-foreground truncate text-lg capitalize">{machine.name}</div>
              <div className="text-muted-foreground truncate">{machine.owner}</div>
              <div className="flex flex-wrap gap-1 mt-1">
                {machine.shared && (
                  <Badge variant="secondary" className="text-[10px] px-2 py-0">
                    Shared
                  </Badge>
                )}
                <Badge variant="secondary" className="text-[10px] px-2 py-0">
                  Expiry disabled
                </Badge>
                {machine.funnel && (
                  <Badge className="bg-green-600 text-[10px] px-2 py-0 text-white">
                    Funnel
                  </Badge>
                )}
                {machine.exitNode && (
                  <Badge className="bg-blue-600 text-[10px] px-2 py-0 text-white">
                    Exit Node
                  </Badge>
                )}
              </div>
            </div>

            {/* Address */}
            <div className="truncate">{machine.address}</div>

            {/* Version + OS */}
            <div>
              <div>{machine.version}</div>
              <div className="text-muted-foreground truncate">{machine.os}</div>
            </div>

            {/* Last Seen + Status */}
            <div className="flex items-center">
              <span
                className={`inline-block w-2 h-2 rounded-full mr-2 ${
                  machine.status === "Online"
                    ? "bg-green-500"
                    : "bg-muted-foreground"
                }`}
              />
              {machine.lastSeen}
            </div>

            {/* Actions */}
            <div className="text-right pr-2">
              <MoreVertical className="w-4 h-4 text-muted-foreground cursor-pointer" />
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
