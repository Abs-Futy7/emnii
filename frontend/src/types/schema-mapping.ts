export type MappingStatus = "suggested" | "approved" | "ignored" | "review";

export type CanonicalField = {
  id: string;
  name: string;
  dataType: string;
  description: string;
  required: boolean;
};

export type SchemaMapping = {
  id: string;
  sourceColumn: string;
  sampleValue: string;
  detectedType: string;
  canonicalField: string;
  confidence: number;
  status: MappingStatus;
};

export type SchemaMappingRow = SchemaMapping;
