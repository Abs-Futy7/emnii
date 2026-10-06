import type { DataQualityReport } from "@/types/data-quality";

export const dataQualityReport: DataQualityReport = {
  totalRecords: 50_231,
  validRecords: 48_942,
  warnings: 918,
  errors: 371,
  score: 96.4,
  issues: [
    { id: "issue-1", issue: "Missing email", description: "Required contact email is blank", severity: "Warning", affectedRows: 423, percentage: 0.84, action: "Review rows" },
    { id: "issue-2", issue: "Duplicate customer", description: "Likely duplicate based on email and phone", severity: "Warning", affectedRows: 188, percentage: 0.37, action: "Compare" },
    { id: "issue-3", issue: "Invalid phone", description: "Phone cannot be normalized to E.164", severity: "Error", affectedRows: 307, percentage: 0.61, action: "Review rows" },
    { id: "issue-4", issue: "Invalid date", description: "Date is malformed or outside expected range", severity: "Error", affectedRows: 64, percentage: 0.13, action: "Review rows" },
    { id: "issue-5", issue: "Missing customer ID", description: "Unique source identifier is absent", severity: "Error", affectedRows: 52, percentage: 0.1, action: "Resolve" },
    { id: "issue-6", issue: "Unknown columns", description: "Three source columns are not mapped", severity: "Info", affectedRows: 147, percentage: 0.29, action: "Map columns" },
  ],
  dimensions: [
    { name: "Completeness", score: 97.8, detail: "Required fields populated" },
    { name: "Validity", score: 96.1, detail: "Values match expected formats" },
    { name: "Uniqueness", score: 99.2, detail: "Duplicate records controlled" },
    { name: "Consistency", score: 92.6, detail: "Values agree across sources" },
  ],
  pii: [
    { type: "Names", count: 48_201 },
    { type: "Emails", count: 47_894 },
    { type: "Phone numbers", count: 46_552 },
    { type: "Addresses", count: 39_118 },
  ],
  redactionStatus: "Ready",
};
