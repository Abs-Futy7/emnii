"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { clientWorkspaceNavigation } from "@/data/client-workspace-navigation";
import { cn } from "@/lib/utils";

export function ClientWorkspaceNav({ clientId }: { clientId: string }) {
  const pathname = usePathname();
  const basePath = `/clients/${clientId}`;

  return (
    <nav
      aria-label="Client workspace"
      className="overflow-x-auto border-b [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
    >
      <ul className="flex min-w-max gap-1">
        {clientWorkspaceNavigation.map((item) => {
          const href = item.segment ? `${basePath}/${item.segment}` : basePath;
          const isActive = item.segment
            ? pathname === href || pathname.startsWith(`${href}/`)
            : pathname === basePath;

          return (
            <li key={item.label}>
              <Link
                href={href}
                aria-current={isActive ? "page" : undefined}
                className={cn(
                  "relative flex h-11 items-center px-3 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground focus-visible:rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                  isActive &&
                    "text-foreground after:absolute after:inset-x-3 after:bottom-0 after:h-0.5 after:rounded-full after:bg-primary",
                )}
              >
                {item.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
