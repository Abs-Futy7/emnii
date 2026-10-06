import { AssistantWorkspace } from "@/components/clients/assistant-workspace";
import { supportAssistantCase } from "@/data/mock-support-assistant";

export default function AssistantPage() {
  return <AssistantWorkspace supportCase={supportAssistantCase} />;
}
