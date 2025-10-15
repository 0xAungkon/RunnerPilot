"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Server,
  Grid3x3,
  Wrench,
  Users,
  Lock,
  FileText,
  Globe,
  Settings,
  BookOpen,
  Search,
  Filter,
  Download,
  MoreVertical,
  ChevronDown,
  HelpCircle,
  Info,
  Circle,
} from "lucide-react"

interface Machine {
  id: string
  name: string
  email: string
  address: string
  version: string
  os: string
  lastSeen: string
  status: "connected" | "offline"
  badges: string[]
}

const machines: Machine[] = [
  {
    id: "1",
    name: "monika-latitude-3410",
    email: "monikapal69420@gmail.com",
    address: "100.70.233.117",
    version: "1.86.2",
    os: "Linux 6.11.0-29-generic",
    lastSeen: "Sep 24",
    status: "offline",
    badges: ["Shared in", "Expiry disabled"],
  },
  {
    id: "2",
    name: "hpx360",
    email: "tajdrivestorage1@gmail.com",
    address: "100.88.19.50",
    version: "1.86.2",
    os: "Windows 11 24H2",
    lastSeen: "Oct 6, 8:23 PM GMT+6",
    status: "offline",
    badges: ["Shared in", "Expiry disabled"],
  },
  {
    id: "3",
    name: "0x-personal-dell",
    email: "aungkonmalakar@gmail.com",
    address: "100.98.85.42",
    version: "1.86.2",
    os: "Linux 6.12.38+kali-amd64",
    lastSeen: "Connected",
    status: "connected",
    badges: ["Expiry disabled", "Funnel", "Exit Node"],
  },
]

export default function TestPage() {
  const [searchQuery, setSearchQuery] = useState("")

  return (
    <>
        {/* Actions */}
        <div className="mb-6 flex items-center gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500" />
            <Input
              placeholder="Search by name, owner, tag, version..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="border-gray-700 bg-[#1e1e1e] pl-10 text-sm text-white placeholder:text-gray-500 rounded-lg"
            />
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="outline"
                className="border-gray-700 bg-[#1e1e1e] text-white hover:bg-[#2a2a2a] rounded-lg"
              >
                <Filter className="mr-2 h-4 w-4" />
                Filters
                <ChevronDown className="ml-2 h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="bg-[#1e1e1e] border-gray-700">
              <DropdownMenuItem className="text-white">All machines</DropdownMenuItem>
              <DropdownMenuItem className="text-white">Connected</DropdownMenuItem>
              <DropdownMenuItem className="text-white">Offline</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <Button className="bg-blue-600 hover:bg-blue-700 text-white rounded-lg">
            Add device
            <ChevronDown className="ml-2 h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" className="text-gray-400 hover:text-white">
            <Download className="h-4 w-4" />
          </Button>
        </div>

        {/* Machine Count */}
        <Badge variant="secondary" className="bg-gray-800 text-gray-300 px-3 py-1 rounded-md mb-4">
          25 machines
        </Badge>

        {/* Table */}
        <div className="overflow-hidden rounded-xl border border-gray-800">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-[#161616] border-b border-gray-800">
                {["Machine", "Addresses", "Version", "Last seen", ""].map((head, i) => (
                  <th
                    key={i}
                    className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-400"
                  >
                    {head === "Addresses" ? (
                      <div className="flex items-center gap-1">
                        {head} <Info className="h-3 w-3 text-gray-500" />
                      </div>
                    ) : (
                      head
                    )}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {machines.map((m) => (
                <tr key={m.id} className="hover:bg-[#1f1f1f] transition">
                  <td className="px-6 py-4 align-top">
                    <div className="flex flex-col gap-1">
                      <span className="font-medium text-white">{m.name}</span>
                      <span className="text-sm text-gray-400">{m.email}</span>
                      <div className="flex flex-wrap gap-1.5 mt-1">
                        {m.badges.map((b, i) => (
                          <Badge
                            key={i}
                            className={`text-xs ${
                              b === "Shared in"
                                ? "bg-orange-900/30 text-orange-400"
                                : b === "Funnel"
                                ? "bg-teal-900/30 text-teal-400"
                                : b === "Exit Node"
                                ? "bg-blue-900/30 text-blue-400"
                                : "bg-gray-800 text-gray-400"
                            }`}
                          >
                            {b}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 align-top">
                    <div className="flex items-center gap-2">
                      <span className="text-white text-sm">{m.address}</span>
                      <ChevronDown className="h-4 w-4 text-gray-500" />
                    </div>
                  </td>
                  <td className="px-6 py-4 align-top">
                    <div className="flex flex-col gap-0.5">
                      <div className="flex items-center gap-2">
                        {m.status === "offline" && (
                          <Circle className="h-2 w-2 fill-gray-600 text-gray-600" />
                        )}
                        <span className="text-white text-sm">{m.version}</span>
                      </div>
                      <span className="text-xs text-gray-400">{m.os}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 align-top">
                    <div className="flex items-center gap-2">
                      <Circle
                        className={`h-2 w-2 ${
                          m.status === "connected"
                            ? "fill-green-500 text-green-500"
                            : "fill-gray-600 text-gray-600"
                        }`}
                      />
                      <span
                        className={`text-sm ${
                          m.status === "connected" ? "text-green-500" : "text-gray-400"
                        }`}
                      >
                        {m.lastSeen}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 align-top text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-gray-400 hover:text-white"
                        >
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent
                        align="end"
                        className="bg-[#1e1e1e] border-gray-700"
                      >
                        <DropdownMenuItem className="text-white">Edit</DropdownMenuItem>
                        <DropdownMenuItem className="text-white">Disable</DropdownMenuItem>
                        <DropdownMenuItem className="text-red-500">Delete</DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        </>
  )
}
