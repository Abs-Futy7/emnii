import { ClientOnboardingForm } from "@/components/clients/client-onboarding-form";
import { PageHeader } from "@/components/layout/page-header";

export default function NewClientPage() {
  return (
    <>
      <PageHeader
        eyebrow="Client onboarding"
        title="Create Client"
        description="Set up the organization profile and workspace defaults. Data connections come next."
      />
      <div className="mx-auto w-full max-w-5xl">
        <ClientOnboardingForm />
      </div>
    </>
  );
}
