import { useState } from "react";
import { motion } from "framer-motion";
import { Search, Brain, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import translations from "../lib/translations";
import { analyzeArticle, SAMPLE_ARTICLE } from "../lib/analyzer";
import Sidebar from "../components/Sidebar";
import ScoreGauge from "../components/ScoreGauge";
import MetricCard from "../components/MetricCard";
import ClaimTable from "../components/ClaimTable";
import StrengthsWeaknesses from "../components/StrengthsWeaknesses";
import LLMAnalysis from "../components/LLMAnalysis";
import MethodPanel from "../components/MethodPanel";
import CorroborationModule from "../components/CorroborationModule";

export default function Home() {
  const [lang, setLang] = useState("Français");
  const [articleText, setArticleText] = useState(SAMPLE_ARTICLE);
  const [result, setResult] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);

  const t = translations[lang] || translations["Français"];

  const handleAnalyze = () => {
    if (!articleText.trim()) return;
    setAnalyzing(true);
    // Small timeout for animation feel
    setTimeout(() => {
      const res = analyzeArticle(articleText, t);
      setResult(res);
      setAnalyzing(false);
    }, 400);
  };

  const loadExample = () => {
    setArticleText(SAMPLE_ARTICLE);
    setResult(null);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary rounded-xl">
              <Brain className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">{t.title}</h1>
              <p className="text-xs text-muted-foreground">{t.tagline}</p>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          <Sidebar lang={lang} setLang={setLang} t={t} />

          {/* Main content */}
          <main className="flex-1 space-y-8">
            {/* Input area */}
            <div className="bg-card border border-border rounded-xl p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">{t.paste}</h2>
                <Button variant="ghost" size="sm" onClick={loadExample} className="text-xs">
                  {t.load_example}
                </Button>
              </div>
              <Textarea
                value={articleText}
                onChange={(e) => { setArticleText(e.target.value); setResult(null); }}
                rows={10}
                className="resize-none font-inter text-sm leading-relaxed bg-background"
                placeholder={t.paste}
              />
              <Button 
                onClick={handleAnalyze} 
                disabled={analyzing || !articleText.trim()}
                className="w-full gap-2 h-11"
              >
                {analyzing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                {t.analyze}
              </Button>
            </div>

            {/* Results */}
            {result && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-8"
              >
                {/* Top scores */}
                <div className="grid grid-cols-3 gap-3">
                  <MetricCard label={t.classic_score} value={result.M} subtitle={t.help_classic_score} delay={0} />
                  <MetricCard label={t.improved_score} value={result.improved} subtitle={t.help_improved_score} delay={0.1} />
                  <MetricCard label={t.hard_fact_score} value={result.hardFactScore} subtitle={t.help_hard_fact_score} delay={0.2} />
                </div>

                {/* Gauge */}
                <div className="bg-card border border-border rounded-xl p-6">
                  <ScoreGauge score={result.hardFactScore} t={t} />
                </div>

                {/* Verdict */}
                <div className="bg-primary/5 border border-primary/20 rounded-xl p-6 text-center">
                  <p className="text-sm uppercase tracking-wider text-muted-foreground mb-1">{t.verdict}</p>
                  <p className="text-2xl font-bold text-primary">{result.verdict}</p>
                </div>

                {/* Summary metrics */}
                <div>
                  <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-3">{t.summary}</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <MetricCard label="G — gnōsis" value={result.G} delay={0} />
                    <MetricCard label="N — nous" value={result.N} delay={0.05} />
                    <MetricCard label="D — doxa" value={result.D} delay={0.1} />
                    <MetricCard label="V — vérifiabilité" value={result.V} delay={0.15} />
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-3">
                    <MetricCard label={t.qs} value={result.sourceQuality} delay={0.2} />
                    <MetricCard label={t.rc} value={result.avgClaimRisk} delay={0.25} />
                    <MetricCard label={t.vc} value={result.avgClaimVerifiability} delay={0.3} />
                    <MetricCard label={t.f} value={result.redFlags.length} delay={0.35} />
                  </div>
                </div>

                {/* Strengths & Weaknesses */}
                <StrengthsWeaknesses strengths={result.strengths} weaknesses={result.weaknesses} t={t} />

                <Separator />

                {/* Corroboration Module */}
                <CorroborationModule claims={result.claims} hardFactScore={result.hardFactScore} t={t} />

                <Separator />

                {/* LLM Analysis */}
                <LLMAnalysis result={result} t={t} />

                <Separator />

                {/* Claims table */}
                <div>
                  <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-3">
                    {t.hard_fact_checking_by_claim}
                  </h3>
                  <ClaimTable claims={result.claims} t={t} />
                </div>

                <Separator />

                {/* Method */}
                <MethodPanel t={t} />
              </motion.div>
            )}

            {!result && !analyzing && (
              <div className="text-center py-16 text-muted-foreground">
                <Brain className="w-12 h-12 mx-auto mb-4 opacity-20" />
                <p className="text-sm">{t.paste_text_or_load_url}</p>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}
