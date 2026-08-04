import type { LucideIcon } from "lucide-react";

export type NavigationItem = {
  label: string;
  href: string;
  icon: LucideIcon;
};

export type NavigationGroup = {
  title: string;
  items: NavigationItem[];
};
