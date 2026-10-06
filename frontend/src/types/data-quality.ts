export type ValidationSeverity = "Info" | "Warning" | "Error";

export type ValidationIssue = {
  id: string;
  issue: string;
  description: string;
  severity: ValidationSeverity;
  affectedRows: number;
  percentage: number;
  action: string;
};

export type QualityDimension = {
  name: "Completeness" | "Validity" | "Uniqueness" | "Consistency";
  score: number;
  detail: string;
};

export type PiiDetection = {
  type: "Names" | "Emails" | "Phone numbers" | "Addresses";
  count: number;
};

export type DataQualityReport = {
  totalRecords: number;
  validRecords: number;
  warnings: number;
  errors: number;
  score: number;
  issues: ValidationIssue[];
  dimensions: QualityDimension[];
  pii: PiiDetection[];
  redactionStatus: "Ready" | "In Progress" | "Not Configured";
};
