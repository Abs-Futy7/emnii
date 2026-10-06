import {
  Activity,
  BookOpen,
  Building2,
  LayoutDashboard,
  PlugZap,
  Settings,
  Ticket,
  type LucideIcon,
} from "lucide-react";

export type DashboardNavigationItem = {
  label: string;
  href: string;
  icon: LucideIcon;
};

export const dashboardNavigation: DashboardNavigationItem[] = [
  { label: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { label: "Clients", href: "/clients", icon: Building2 },
  { label: "Tickets", href: "/tickets", icon: Ticket },
  { label: "Knowledge Base", href: "/knowledge-base", icon: BookOpen },
  { label: "Integrations", href: "/integrations", icon: PlugZap },
  { label: "Monitoring", href: "/monitoring", icon: Activity },
  { label: "Settings", href: "/settings", icon: Settings },
];

export function isNavigationItemActive(pathname: string, href: string) {
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function getNavigationItem(pathname: string) {
  return dashboardNavigation.find((item) =>
    isNavigationItemActive(pathname, item.href),
  );
}
