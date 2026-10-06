import type { CanonicalField, SchemaMappingRow } from "@/types/schema-mapping";

export const canonicalFields: CanonicalField[] = [
  { id: "customer_name", name: "customer_name", dataType: "string", description: "Full customer or account name", required: true },
  { id: "phone", name: "phone", dataType: "phone", description: "Normalized international phone number", required: false },
  { id: "email", name: "email", dataType: "email", description: "Primary customer email address", required: true },
  { id: "created_at", name: "created_at", dataType: "datetime", description: "Customer creation timestamp", required: true },
  { id: "district", name: "district", dataType: "string", description: "Normalized geographic district", required: false },
  { id: "customer_id", name: "customer_id", dataType: "string", description: "Unique source-system identifier", required: true },
];

export const schemaMappings: SchemaMappingRow[] = [
  { id: "map-1", sourceColumn: "cust_nm", sampleValue: "Amina Rahman", detectedType: "Text", canonicalField: "customer_name", confidence: 97, status: "suggested" },
  { id: "map-2", sourceColumn: "mob_no", sampleValue: "+8801712345678", detectedType: "Phone", canonicalField: "phone", confidence: 99, status: "suggested" },
  { id: "map-3", sourceColumn: "mail", sampleValue: "amina@example.com", detectedType: "Email", canonicalField: "email", confidence: 99, status: "suggested" },
  { id: "map-4", sourceColumn: "join_dt", sampleValue: "2026/09/18", detectedType: "Date", canonicalField: "created_at", confidence: 91, status: "suggested" },
  { id: "map-5", sourceColumn: "district_code", sampleValue: "DHK-07", detectedType: "Text", canonicalField: "unmapped", confidence: 42, status: "review" },
];
