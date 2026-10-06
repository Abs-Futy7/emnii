"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { zodResolver } from "@hookform/resolvers/zod";
import { CheckCircle2, LoaderCircle } from "lucide-react";
import { Controller, useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Field,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import {
  dataRegionOptions,
  industryOptions,
  languageOptions,
  timezoneOptions,
} from "@/data/client-onboarding-options";
import { simulateCreateClient } from "@/lib/client-onboarding";
import {
  clientOnboardingSchema,
  type ClientOnboardingValues,
} from "@/lib/validations/client-onboarding";

function toWorkspaceSlug(value: string) {
  return value
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function ClientOnboardingForm() {
  const router = useRouter();
  const [slugEdited, setSlugEdited] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const form = useForm<ClientOnboardingValues>({
    resolver: zodResolver(clientOnboardingSchema),
    defaultValues: {
      companyName: "",
      workspaceSlug: "",
      industry: "",
      website: "",
      contactName: "",
      contactEmail: "",
      description: "",
      timezone: "",
      preferredLanguage: "en-US",
      dataRegion: "",
    },
  });

  async function onSubmit(values: ClientOnboardingValues) {
    const result = await simulateCreateClient(values);
    setSubmitted(true);
    await new Promise((resolve) => setTimeout(resolve, 450));
    router.push(`/clients/${result.clientId}?onboarding=created`);
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} noValidate className="space-y-5">
      <Card>
        <CardHeader className="border-b">
          <CardTitle>Company Information</CardTitle>
          <CardDescription>
            Create the organization identity and primary workspace contact.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <FieldGroup className="grid gap-5 md:grid-cols-2">
            <Controller
              name="companyName"
              control={form.control}
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="companyName">Company name</FieldLabel>
                  <Input
                    {...field}
                    id="companyName"
                    placeholder="Acme Commerce"
                    aria-invalid={fieldState.invalid}
                    onChange={(event) => {
                      field.onChange(event);
                      if (!slugEdited) {
                        form.setValue(
                          "workspaceSlug",
                          toWorkspaceSlug(event.target.value),
                          { shouldValidate: form.formState.isSubmitted },
                        );
                      }
                    }}
                  />
                  <FieldError errors={[fieldState.error]} />
                </Field>
              )}
            />

            <Controller
              name="workspaceSlug"
              control={form.control}
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="workspaceSlug">Workspace slug</FieldLabel>
                  <Input
                    {...field}
                    id="workspaceSlug"
                    placeholder="acme-commerce"
                    autoCapitalize="none"
                    spellCheck={false}
                    aria-invalid={fieldState.invalid}
                    onChange={(event) => {
                      setSlugEdited(true);
                      field.onChange(event);
                    }}
                  />
                  <FieldDescription>
                    Used in workspace URLs and integration identifiers.
                  </FieldDescription>
                  <FieldError errors={[fieldState.error]} />
                </Field>
              )}
            />

            <Controller
              name="industry"
              control={form.control}
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="industry">Industry</FieldLabel>
                  <Select value={field.value} onValueChange={(value) => field.onChange(value ?? "")}>
                    <SelectTrigger id="industry" className="w-full" aria-invalid={fieldState.invalid}>
                      <SelectValue placeholder="Select an industry" />
                    </SelectTrigger>
                    <SelectContent>
                      {industryOptions.map((option) => (
                        <SelectItem key={option} value={option}>{option}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FieldError errors={[fieldState.error]} />
                </Field>
              )}
            />

            <Controller
              name="website"
              control={form.control}
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="website">
                    Company website <span className="font-normal text-muted-foreground">(optional)</span>
                  </FieldLabel>
                  <Input {...field} id="website" type="url" placeholder="https://acme.example" aria-invalid={fieldState.invalid} />
                  <FieldError errors={[fieldState.error]} />
                </Field>
              )}
            />

            <Controller
              name="contactName"
              control={form.control}
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="contactName">Primary contact name</FieldLabel>
                  <Input {...field} id="contactName" placeholder="Jordan Lee" autoComplete="name" aria-invalid={fieldState.invalid} />
                  <FieldError errors={[fieldState.error]} />
                </Field>
              )}
            />

            <Controller
              name="contactEmail"
              control={form.control}
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="contactEmail">Contact email</FieldLabel>
                  <Input {...field} id="contactEmail" type="email" placeholder="jordan@acme.example" autoComplete="email" aria-invalid={fieldState.invalid} />
                  <FieldError errors={[fieldState.error]} />
                </Field>
              )}
            />

            <Controller
              name="description"
              control={form.control}
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid} className="md:col-span-2">
                  <FieldLabel htmlFor="description">
                    Description <span className="font-normal text-muted-foreground">(optional)</span>
                  </FieldLabel>
                  <Textarea {...field} id="description" placeholder="Add context about the client's support operation, products, or onboarding goals." rows={4} aria-invalid={fieldState.invalid} />
                  <FieldError errors={[fieldState.error]} />
                </Field>
              )}
            />
          </FieldGroup>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="border-b">
          <CardTitle>Settings</CardTitle>
          <CardDescription>
            Configure regional defaults for this client workspace.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <FieldGroup className="grid gap-5 md:grid-cols-3">
            <Controller
              name="timezone"
              control={form.control}
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="timezone">Default timezone</FieldLabel>
                  <Select value={field.value} onValueChange={(value) => field.onChange(value ?? "")}>
                    <SelectTrigger id="timezone" className="w-full" aria-invalid={fieldState.invalid}>
                      <SelectValue placeholder="Choose timezone" />
                    </SelectTrigger>
                    <SelectContent>
                      {timezoneOptions.map((option) => (
                        <SelectItem key={option.value} value={option.value}>{option.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FieldError errors={[fieldState.error]} />
                </Field>
              )}
            />

            <Controller
              name="preferredLanguage"
              control={form.control}
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="preferredLanguage">Preferred language</FieldLabel>
                  <Select value={field.value} onValueChange={(value) => field.onChange(value ?? "")}>
                    <SelectTrigger id="preferredLanguage" className="w-full" aria-invalid={fieldState.invalid}>
                      <SelectValue placeholder="Choose language" />
                    </SelectTrigger>
                    <SelectContent>
                      {languageOptions.map((option) => (
                        <SelectItem key={option.value} value={option.value}>{option.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FieldError errors={[fieldState.error]} />
                </Field>
              )}
            />

            <Controller
              name="dataRegion"
              control={form.control}
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="dataRegion">Data region</FieldLabel>
                  <Select value={field.value} onValueChange={(value) => field.onChange(value ?? "")}>
                    <SelectTrigger id="dataRegion" className="w-full" aria-invalid={fieldState.invalid}>
                      <SelectValue placeholder="Choose data region" />
                    </SelectTrigger>
                    <SelectContent>
                      {dataRegionOptions.map((option) => (
                        <SelectItem key={option.value} value={option.value}>{option.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FieldDescription>Placeholder selection for future data residency controls.</FieldDescription>
                  <FieldError errors={[fieldState.error]} />
                </Field>
              )}
            />
          </FieldGroup>
        </CardContent>
        <CardFooter className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-between">
          <p className="flex min-h-8 items-center text-sm text-muted-foreground" aria-live="polite">
            {submitted ? (
              <span className="inline-flex items-center gap-2 text-emerald-600 dark:text-emerald-400">
                <CheckCircle2 className="size-4" aria-hidden="true" />
                Workspace created. Redirecting…
              </span>
            ) : (
              "You can configure data sources after creating the client."
            )}
          </p>
          <div className="flex w-full gap-2 sm:w-auto">
            <Button variant="outline" render={<Link href="/clients" />} className="flex-1 sm:flex-none">
              Cancel
            </Button>
            <Button type="submit" disabled={form.formState.isSubmitting || submitted} className="flex-1 sm:flex-none">
              {form.formState.isSubmitting ? (
                <LoaderCircle data-icon="inline-start" className="animate-spin" aria-hidden="true" />
              ) : null}
              {form.formState.isSubmitting ? "Creating…" : "Create Client"}
            </Button>
          </div>
        </CardFooter>
      </Card>
    </form>
  );
}
