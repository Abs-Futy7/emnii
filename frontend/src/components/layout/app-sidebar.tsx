"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LifeBuoy } from "lucide-react";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
  useSidebar,
} from "@/components/ui/sidebar";
import {
  dashboardNavigation,
  isNavigationItemActive,
} from "@/data/dashboard-navigation";

export function AppSidebar() {
  const pathname = usePathname();
  const { setOpenMobile } = useSidebar();

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="border-b border-sidebar-border p-3">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              size="lg"
              tooltip="ResolveOps"
              render={<Link href="/" aria-label="ResolveOps home" />}
              onClick={() => setOpenMobile(false)}
              className="hover:bg-transparent active:bg-transparent"
            >
              <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-xs">
                <LifeBuoy className="size-4" aria-hidden="true" />
              </span>
              <span className="grid min-w-0 flex-1 text-left leading-tight">
                <span className="truncate text-sm font-semibold">ResolveOps</span>
                <span className="truncate text-xs text-sidebar-foreground/60">
                  Operations Console
                </span>
              </span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup className="px-2 py-4">
          <SidebarGroupLabel>Workspace</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {dashboardNavigation.map((item) => {
                const isActive = isNavigationItemActive(pathname, item.href);

                return (
                  <SidebarMenuItem key={item.href}>
                    <SidebarMenuButton
                      tooltip={item.label}
                      isActive={isActive}
                      render={
                        <Link
                          href={item.href}
                          aria-current={isActive ? "page" : undefined}
                        />
                      }
                      onClick={() => setOpenMobile(false)}
                    >
                      <item.icon aria-hidden="true" />
                      <span>{item.label}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-sidebar-border p-3">
        <div className="flex items-center gap-2 px-1 text-xs text-sidebar-foreground/60 group-data-[collapsible=icon]:justify-center group-data-[collapsible=icon]:px-0">
          <span className="size-2 shrink-0 rounded-full bg-emerald-500" aria-hidden="true" />
          <span className="truncate group-data-[collapsible=icon]:hidden">
            All systems operational
          </span>
          <span className="sr-only">System status: operational</span>
        </div>
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}
