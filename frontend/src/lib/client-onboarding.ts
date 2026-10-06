import type { ClientOnboardingValues } from "@/lib/validations/client-onboarding";

export type CreateClientResult = {
  clientId: string;
};

export async function simulateCreateClient(
  values: ClientOnboardingValues,
): Promise<CreateClientResult> {
  void values;
  await new Promise((resolve) => setTimeout(resolve, 700));

  return { clientId: "shopnest" };
}
