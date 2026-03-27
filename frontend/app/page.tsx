"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { Loader2, FileText, Upload, AlertCircle } from "lucide-react";
import { DropZone } from "@/components/DropZone";
import { analyzeText, analyzeUpload } from "@/lib/api";

export default function Home() {
  const router = useRouter();

  const [activeTab, setActiveTab] = useState("upload");
  const [file, setFile] = useState<File | null>(null);
  const [cvText, setCvText] = useState("");

  const [jobTitle, setJobTitle] = useState("");
  const [jdText, setJdText] = useState("");
  const [strictMode, setStrictMode] = useState(false);

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    setError(null);
    setIsAnalyzing(true);

    try {
      let res;
      if (activeTab === "upload") {
        if (!file) throw new Error("Please select a file first.");
        res = await analyzeUpload(file, jdText || undefined);
      } else {
        if (!cvText.trim()) throw new Error("Please paste your CV text.");
        res = await analyzeText({
          cv_text: cvText,
          jd_text: jdText || undefined,
          job_title: jobTitle || undefined,
          strict_mode: strictMode,
        });
      }

      router.push(`/dashboard/${res.run_id}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "An unexpected error occurred during analysis.");
      setIsAnalyzing(false);
    }
  };

  const isSubmitDisabled = activeTab === "upload" ? !file : !cvText.trim();

  return (
    <main className="flex-1 flex flex-col items-center justify-center p-4 md:p-12 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-primary/10 blur-3xl opacity-50 -z-10 pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-info/10 blur-3xl opacity-50 -z-10 pointer-events-none" />

      <div className="max-w-3xl w-full space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">

        <div className="text-center space-y-3">
          <div className="inline-flex items-center justify-center p-2 bg-primary/10 text-primary rounded-2xl mb-2 ring-1 ring-primary/20 backdrop-blur-md">
            <span className="text-xs font-semibold tracking-widest uppercase">Smart AI Resume</span>
          </div>
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight text-balance">
            Executive Check
          </h1>
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto">
            Deep algorithmic analysis of your CV&apos;s impact, ATS compatibility, and executive presence against industry benchmarks.
          </p>
        </div>

        <Card className="glass-panel border-muted/50 shadow-2xl relative z-10 overflow-visible">
          <CardHeader className="pb-4">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="upload" className="flex items-center gap-2">
                  <Upload className="w-4 h-4" />
                  Upload PDF/DOCX
                </TabsTrigger>
                <TabsTrigger value="paste" className="flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  Paste Text
                </TabsTrigger>
              </TabsList>

              <div className="mt-6">
                <TabsContent value="upload" className="mt-0 outline-none">
                  <DropZone onFileSelect={setFile} />
                </TabsContent>

                <TabsContent value="paste" className="mt-0 outline-none">
                  <div className="space-y-2">
                    <Label htmlFor="cv-text" className="text-sm font-medium ml-1">Paste your CV content</Label>
                    <Textarea
                      id="cv-text"
                      className="min-h-[192px] resize-y bg-background/50 focus:bg-background"
                      placeholder="John Doe&#10;Senior Software Engineer&#10;..."
                      value={cvText}
                      onChange={(e) => setCvText(e.target.value)}
                    />
                  </div>
                </TabsContent>
              </div>
            </Tabs>
          </CardHeader>

          <CardContent className="pb-6">
            <Accordion className="w-full">
              <AccordionItem value="settings" className="border-muted/50 border rounded-lg px-4 bg-background/30 backdrop-blur-sm">
                <AccordionTrigger className="hover:no-underline py-3 text-sm font-medium">
                  Advanced Context (Optional)
                </AccordionTrigger>
                <AccordionContent className="space-y-4 pt-2 pb-4">
                  <div className="grid gap-2">
                    <Label htmlFor="job-title" className="text-xs">Job Title</Label>
                    <input
                      id="job-title"
                      type="text"
                      placeholder="e.g. Director of Engineering"
                      className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                      value={jobTitle}
                      onChange={(e) => setJobTitle(e.target.value)}
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="jd" className="text-xs">Job Description / Requirements</Label>
                    <Textarea
                      id="jd"
                      placeholder="Paste the target job description here to check alignment..."
                      className="h-20 bg-background/50"
                      value={jdText}
                      onChange={(e) => setJdText(e.target.value)}
                    />
                  </div>
                  <div className="flex items-center justify-between mt-2 pt-2 border-t border-border/50">
                    <div className="space-y-0.5">
                      <Label htmlFor="strict-mode" className="text-xs">Strict Mode</Label>
                      <p className="text-[10px] text-muted-foreground leading-tight">Apply harsher benchmark scoring.</p>
                    </div>
                    <Switch id="strict-mode" checked={strictMode} onCheckedChange={setStrictMode} />
                  </div>
                </AccordionContent>
              </AccordionItem>
            </Accordion>

            {error && (
              <div className="mt-4 p-3 bg-destructive/10 border border-destructive/20 rounded-md text-destructive text-sm font-medium flex items-start gap-2">
                <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
                <span>{error}</span>
              </div>
            )}
          </CardContent>

          <CardFooter className="bg-muted/10 border-t border-muted/50 rounded-b-xl p-6">
            <Button
              className="w-full h-12 text-base font-bold shadow-lg transition-all"
              size="lg"
              disabled={isSubmitDisabled || isAnalyzing}
              onClick={handleAnalyze}
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Running Neural Analysis...
                </>
              ) : (
                "Analyze Resume"
              )}
            </Button>
          </CardFooter>
        </Card>
      </div>
    </main>
  );
}
