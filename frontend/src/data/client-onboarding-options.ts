export const industryOptions = [
  "B2B SaaS",
  "Consumer Electronics",
  "E-commerce",
  "Financial Services",
  "Healthcare",
  "Logistics",
  "Retail",
] as const;

export const timezoneOptions = [
  { value: "America/Los_Angeles", label: "Pacific Time (UTC−08:00)" },
  { value: "America/Chicago", label: "Central Time (UTC−06:00)" },
  { value: "America/New_York", label: "Eastern Time (UTC−05:00)" },
  { value: "Europe/London", label: "London (UTC+00:00)" },
  { value: "Europe/Berlin", label: "Central European Time (UTC+01:00)" },
  { value: "Asia/Dhaka", label: "Bangladesh Time (UTC+06:00)" },
  { value: "Asia/Singapore", label: "Singapore Time (UTC+08:00)" },
] as const;

export const languageOptions = [
  { value: "en-US", label: "English (United States)" },
  { value: "en-GB", label: "English (United Kingdom)" },
  { value: "de-DE", label: "German" },
  { value: "es-ES", label: "Spanish" },
  { value: "fr-FR", label: "French" },
] as const;

export const dataRegionOptions = [
  { value: "us-east", label: "United States — East" },
  { value: "us-west", label: "United States — West" },
  { value: "eu-central", label: "European Union — Central" },
  { value: "ap-southeast", label: "Asia Pacific — Southeast" },
] as const;
