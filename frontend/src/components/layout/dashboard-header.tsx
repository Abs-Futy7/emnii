"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Bell, ChevronDown, LogOut, Settings, UserRound } from "lucide-react";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Separator } from "@/components/ui/separator";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { getNavigationItem } from "@/data/dashboard-navigation";

export function DashboardHeader() {
  const pathname = usePathname();
  const currentItem = getNavigationItem(pathname);

  return (
    <header className="sticky top-0 z-20 flex h-14 shrink-0 items-center gap-3 border-b bg-background/95 px-4 backdrop-blur supports-backdrop-filter:bg-background/80 sm:px-6">
      <SidebarTrigger className="-ml-1" />
      <Separator orientation="vertical" className="h-4" />

      <nav aria-label="Breadcrumb" className="min-w-0 flex-1">
        <ol className="flex min-w-0 items-center gap-2 text-sm">
          <li className="hidden text-muted-foreground sm:block">ResolveOps</li>
          <li className="hidden text-muted-foreground sm:block" aria-hidden="true">
            /
          </li>
          <li className="truncate font-medium" aria-current="page">
            {currentItem?.label ?? "Dashboard"}
          </li>
        </ol>
      </nav>

      <div className="flex items-center gap-1.5">
        <Button
          variant="ghost"
          size="icon"
          aria-label="Notifications"
          title="Notifications"
          className="relative"
        >
          <Bell aria-hidden="true" />
          <span
            className="absolute top-1.5 right-1.5 size-1.5 rounded-full bg-primary ring-2 ring-background"
            aria-hidden="true"
          />
        </Button>

        <DropdownMenu>
          <DropdownMenuTrigger
            render={
              <button
                type="button"
                className="flex items-center gap-2 rounded-lg p-1 text-left outline-none transition-colors hover:bg-muted focus-visible:ring-2 focus-visible:ring-ring"
                aria-label="Open user menu"
              >
                <Avatar>
                  <AvatarFallback className="bg-primary/10 font-semibold text-primary">
                    RO
                  </AvatarFallback>
                </Avatar>
                <span className="hidden min-w-0 sm:grid">
                  <span className="truncate text-xs font-medium">Operations Admin</span>
                  <span className="truncate text-[11px] text-muted-foreground">
                    admin@resolveops.io
                  </span>
                </span>
                <ChevronDown className="hidden size-3.5 text-muted-foreground sm:block" aria-hidden="true" />
              </button>
            }
          />
          <DropdownMenuContent align="end" sideOffset={8} className="w-56">
            <DropdownMenuLabel>
              <span className="block text-foreground">Operations Admin</span>
              <span className="block font-normal">admin@resolveops.io</span>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuGroup>
              <DropdownMenuItem disabled>
                <UserRound aria-hidden="true" />
                Profile
              </DropdownMenuItem>
              <DropdownMenuItem render={<Link href="/settings" />}>
                <Settings aria-hidden="true" />
                Settings
              </DropdownMenuItem>
            </DropdownMenuGroup>
            <DropdownMenuSeparator />
            <DropdownMenuItem disabled>
              <LogOut aria-hidden="true" />
              Sign out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
