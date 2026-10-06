import type { IngestionHistoryItem } from "@/types/data-ingestion";

export const ingestionHistory: IngestionHistoryItem[] = [
  { id: "ing-101", fileName: "customers_2026_10.csv", format: "CSV", records: 50_231, uploadedBy: "Maya Chen", uploadedAt: "Oct 6, 2026 · 09:42", status: "Completed" },
  { id: "ing-102", fileName: "tickets_incremental.json", format: "JSON", records: 18_492, uploadedBy: "Automation", uploadedAt: "Oct 6, 2026 · 08:15", status: "Processing" },
  { id: "ing-103", fileName: "legacy_contacts.xlsx", format: "XLSX", records: 12_804, uploadedBy: "Jon Bell", uploadedAt: "Oct 5, 2026 · 16:28", status: "Needs Review" },
  { id: "ing-104", fileName: "orders_archive.csv", format: "CSV", records: 284_115, uploadedBy: "Maya Chen", uploadedAt: "Oct 5, 2026 · 11:03", status: "Completed" },
  { id: "ing-105", fileName: "returns_export.json", format: "JSON", records: 0, uploadedBy: "Automation", uploadedAt: "Oct 4, 2026 · 22:40", status: "Failed" },
];
