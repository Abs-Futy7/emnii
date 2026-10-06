import { z } from "zod";

export const clientOnboardingSchema = z.object({
  companyName: z
    .string()
    .trim()
    .min(2, "Enter a company name with at least 2 characters."),
  workspaceSlug: z
    .string()
    .trim()
    .min(3, "Workspace slug must be at least 3 characters.")
    .max(48, "Workspace slug must be 48 characters or fewer.")
    .regex(
      /^[a-z0-9]+(?:-[a-z0-9]+)*$/,
      "Use lowercase letters, numbers, and single hyphens only.",
    ),
  industry: z.string().min(1, "Choose an industry."),
  website: z
    .string()
    .trim()
    .url("Enter a complete website URL, including https://.")
    .or(z.literal("")),
  contactName: z
    .string()
    .trim()
    .min(2, "Enter the primary contact's name."),
  contactEmail: z
    .string()
    .trim()
    .email("Enter a valid business email address."),
  description: z
    .string()
    .trim()
    .max(500, "Description must be 500 characters or fewer."),
  timezone: z.string().min(1, "Choose a default timezone."),
  preferredLanguage: z.string().min(1, "Choose a preferred language."),
  dataRegion: z.string().min(1, "Choose a data region."),
});

export type ClientOnboardingValues = z.infer<typeof clientOnboardingSchema>;
