from ddgs import DDGS  # Renommé depuis duckduckgo_search
from newspaper import Article
import re
from dataclasses import dataclass
from typing import List, Dict

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Mécroyance Lab — Fact-checking",
    page_icon="🧠",
    layout="wide",
)

# -----------------------------
# Dictionnaire de traduction
# -----------------------------
translations = {
    "Français": {
        "title": "🧠 Mécroyance Lab — Analyse de crédibilité",
        "analyze": "🔍 Analyser l'article",
        "topic": "Sujet à analyser",
        "analyze_topic": "📰 Analyser 10 articles sur ce sujet",
        "url": "Analyser un article par URL",
        "load_url": "🌐 Charger l'article depuis l'URL",
        "paste": "Collez ici un article ou un texte",
        "verdict": "Verdict",
        "summary": "Résumé de l'analyse",
        "tagline": "Votre formule comme boussole, un contrôle plus sévère comme garde-frontière.",
        "settings": "Réglages",
        "load_example": "Charger l'exemple",
        "show_method": "Afficher la méthode",
        "hard_fact_score_scale": "Échelle du hard fact score",
        "scale_0_5": "0–5 : très fragile",
        "scale_6_9": "6–9 : douteux",
        "scale_10_14": "10–14 : plausible mais à recouper",
        "scale_15_20": "15–20 : structurellement robuste",
        "analyze_multiple_articles_by_topic": "Analyse de plusieurs articles par sujet",
        "searching_analyzing_articles": "Recherche et analyse des articles en cours...",
        "articles_analyzed": "articles analysés.",
        "analyzed_articles": "Articles analysés",
        "avg_hard_fact": "Moyenne Hard Fact",
        "avg_classic_score": "Moyenne score classique",
        "topic_doxa_index": "Indice de doxa du sujet",
        "high": "Élevé",
        "medium": "Moyen",
        "low": "Faible",
        "credibility_score_dispersion": "Dispersion des scores de crédibilité",
        "article_label": "Article",
        "analyzed_articles_details": "Détail des articles analysés",
        "no_exploitable_articles_found": "Aucun article exploitable trouvé pour ce sujet.",
        "enter_keyword_first": "Entrez d'abord un mot-clé ou un sujet.",
        "article_loaded_from_url": "Article chargé depuis l'URL.",
        "unable_to_retrieve_text": "Impossible de récupérer le texte de cette URL.",
        "paste_url_first": "Collez d'abord une URL.",
        "classic_score": "Score classique",
        "improved_score": "Score amélioré",
        "hard_fact_score": "Hard Fact Score",
        "help_classic_score": "M = (G + N) − D",
        "help_improved_score": "Ajout de V et pénalité R",
        "help_hard_fact_score": "Contrôle plus dur des affirmations et des sources",
        "credibility_gauge": "Jauge de crédibilité",
        "fragile": "Fragile",
        "fragile_message": "Le texte présente de fortes fragilités structurelles ou factuelles.",
        "doubtful": "Douteux",
        "doubtful_message": "Le texte contient quelques éléments crédibles, mais reste très incertain.",
        "plausible": "Plausible",
        "plausible_message": "Le texte paraît globalement plausible, mais demande encore vérification.",
        "robust": "Robuste",
        "robust_message": "Le texte présente une base structurelle et factuelle plutôt solide.",
        "score": "Score",
        "strengths_detected": "Forces détectées",
        "few_strong_signals": "Peu de signaux forts repérés.",
        "weaknesses_detected": "Fragilités détectées",
        "no_major_weakness": "Aucune fragilité majeure repérée par l'heuristique.",
        "hard_fact_checking_by_claim": "Fact-checking dur par affirmation",
        "claim": "Affirmation",
        "status": "Statut",
        "verifiability": "Vérifiabilité",
        "risk": "Risque",
        "number": "Nombre",
        "date": "Date",
        "named_entity": "Nom propre",
        "attributed_source": "Source attribuée",
        "paste_longer_text": "Collez un texte un peu plus long pour obtenir une cartographie fine des affirmations.",
        "paste_text_or_load_url": "Collez un texte ou chargez une URL, puis cliquez sur « 🔍 Analyser l'article ».",
        "method": "Méthode",
        "original_formula": "Formule originelle",
        "articulated_knowledge_density": "G : densité de savoir articulé — sources, chiffres, noms, références, traces vérifiables.",
        "integration": "N : intégration — contexte, nuances, réserves, cohérence argumentative.",
        "assertive_rigidity": "D : rigidité assertive — certitudes non soutenues, emballement rhétorique, gonflement doxique.",
        "improved_variant": "Variante améliorée",
        "addition_of_v_and_r": "Ajout de V pour la vérifiabilité et de R comme pénalité rhétorique.",
        "hard_fact_checking_module": "Module de fact-checking dur",
        "claim_evaluation_criteria": "Chaque phrase est traitée comme une affirmation potentielle, puis évaluée selon:",
        "criteria_list": "- présence de dates, nombres, noms propres,\n- présence d'une attribution claire,\n- degré d'absolutisme,\n- charge sensationnaliste,\n- qualité probable des sources mentionnées,\n- signaux rouges narratifs.",
        "practical_hard_fact_formula": "Formule pratique du hard fact score",
        "qs": "QS : qualité des sources",
        "vc": "VC : vérifiabilité moyenne des affirmations",
        "rc": "RC : risque moyen des affirmations",
        "f": "F : nombre de red flags",
        "disclaimer": "Cette app ne remplace pas un vrai journaliste, un vrai chercheur, ni un greffier de la réalité. Mais elle retire déjà quelques masques au texte qui parade.",
        "presence_of_source_markers": "Présence de marqueurs de sources ou de données",
        "verifiability_clues": "Indices de vérifiabilité repérés : liens, chiffres, dates ou pourcentages",
        "text_contains_nuances": "Le texte contient des nuances, limites ou contrepoints",
        "text_evokes_robust_sources": "Le texte évoque des sources potentiellement robustes ou institutionnelles",
        "some_claims_verifiable": "Certaines affirmations sont assez bien ancrées pour être vérifiées proprement",
        "overly_assertive_language": "Langage trop assuré ou absolutiste",
        "notable_emotional_sensational_charge": "Charge émotionnelle ou sensationnaliste notable",
        "almost_total_absence_of_verifiable_elements": "Absence quasi totale d'éléments vérifiables",
        "text_too_short": "Texte trop court pour soutenir sérieusement une affirmation forte",
        "multiple_claims_very_fragile": "Plusieurs affirmations centrales sont très fragiles au regard des indices présents",
        "to_verify": "À vérifier",
        "rather_verifiable": "Plutôt vérifiable",
        "very_fragile": "Très fragile",
        "low_credibility": "Crédibilité basse",
        "prudent_credibility": "Crédibilité prudente",
        "rather_credible": "Plutôt crédible",
        "strong_credibility": "Crédibilité forte",
        "yes": "Oui",
        "no": "Non",
        "llm_analysis": "Analyse de Mécroyance pour LLM",
        "llm_intro": "Cette section applique les modèles dérivés du traité pour évaluer la posture cognitive d'un système (IA ou humain).",
        "overconfidence": "Surconfiance (Asymétrie)",
        "calibration": "Calibration relative (Ratio)",
        "revisability": "Révisabilité (R)",
        "cognitive_closure": "Clôture cognitive",
        "cognitive_potential": "Potentiel cognitif",
        "cognitive_field": "Champ cognitif (Attracteur)",
        "cognitive_curvature": "Courbure cognitive (κ)",
        "interpretation": "Interprétation",
        "llm_metrics": "Métriques LLM",
        "zone_closure": "Zone de clôture cognitive : la certitude excède l’ancrage cognitif.",
        "zone_stability": "Zone de stabilité révisable : la mécroyance accompagne sans dominer.",
        "zone_lucidity": "Zone de lucidité croissante : le doute structure la cognition.",
        "zone_rare": "Zone rare : cognition hautement intégrée et réflexive.",
        "zone_pansapience": "Pan-sapience hypothétique : horizon limite d’une cognition presque totalement révisable.",
        "zone_asymptote": "Asymptote idéale : totalité du savoir et de l’intégration, sans rigidification.",
        "out_of_spectrum": "Valeur hors spectre théorique.",
    },
    "English": {
        "title": "🧠 Mecroyance Lab — Credibility Analyzer",
        "analyze": "🔍 Analyze article",
        "topic": "Topic to analyze",
        "analyze_topic": "📰 Analyze 10 articles on this topic",
        "url": "Analyze article from URL",
        "load_url": "🌐 Load article from URL",
        "paste": "Paste an article or text here",
        "verdict": "Verdict",
        "summary": "Analysis summary",
        "tagline": "Your formula as a compass, stricter control as a border guard.",
        "settings": "Settings",
        "load_example": "Load example",
        "show_method": "Show method",
        "hard_fact_score_scale": "Hard Fact Score Scale",
        "scale_0_5": "0–5 : very fragile",
        "scale_6_9": "6–9 : doubtful",
        "scale_10_14": "10–14 : plausible but needs cross-referencing",
        "scale_15_20": "15–20 : structurally robust",
        "analyze_multiple_articles_by_topic": "Analyze multiple articles by topic",
        "searching_analyzing_articles": "Searching and analyzing articles...",
        "articles_analyzed": "articles analyzed.",
        "analyzed_articles": "Analyzed Articles",
        "avg_hard_fact": "Avg Hard Fact",
        "avg_classic_score": "Avg Classic Score",
        "topic_doxa_index": "Topic Doxa Index",
        "high": "High",
        "medium": "Medium",
        "low": "Low",
        "credibility_score_dispersion": "Credibility Score Dispersion",
        "article_label": "Article",
        "analyzed_articles_details": "Details of analyzed articles",
        "no_exploitable_articles_found": "No exploitable articles found for this topic.",
        "enter_keyword_first": "Enter a keyword or topic first.",
        "article_loaded_from_url": "Article loaded from URL.",
        "unable_to_retrieve_text": "Unable to retrieve text from this URL.",
        "paste_url_first": "Paste a URL first.",
        "classic_score": "Classic Score",
        "improved_score": "Improved Score",
        "hard_fact_score": "Hard Fact Score",
        "help_classic_score": "M = (G + N) − D",
        "help_improved_score": "Addition of V and R penalty",
        "help_hard_fact_score": "Stricter control of claims and sources",
        "credibility_gauge": "Credibility Gauge",
        "fragile": "Fragile",
        "fragile_message": "The text shows strong structural or factual weaknesses.",
        "doubtful": "Doubtful",
        "doubtful_message": "The text contains some credible elements, but remains very uncertain.",
        "plausible": "Plausible",
        "plausible_message": "The text appears generally plausible, but still requires verification.",
        "robust": "Robust",
        "robust_message": "The text presents a rather solid structural and factual basis.",
        "score": "Score",
        "strengths_detected": "Strengths detected",
        "few_strong_signals": "Few strong signals identified.",
        "weaknesses_detected": "Weaknesses detected",
        "no_major_weakness": "No major weakness identified by heuristics.",
        "hard_fact_checking_by_claim": "Hard fact-checking by claim",
        "claim": "Claim",
        "status": "Status",
        "verifiability": "Verifiability",
        "risk": "Risk",
        "number": "Number",
        "date": "Date",
        "named_entity": "Named Entity",
        "attributed_source": "Attributed Source",
        "paste_longer_text": "Paste a slightly longer text to get a fine mapping of claims.",
        "paste_text_or_load_url": "Paste a text or load a URL, then click on « 🔍 Analyze article ».",
        "method": "Method",
        "original_formula": "Original Formula",
        "articulated_knowledge_density": "G : articulated knowledge density — sources, figures, names, references, verifiable traces.",
        "integration": "N : integration — context, nuances, reservations, argumentative coherence.",
        "assertive_rigidity": "D : assertive rigidity — unsupported certainties, emotional charge.",
        "improved_variant": "Improved Variant",
        "addition_of_v_and_r": "Addition of V for verifiability and R as a rhetorical penalty.",
        "hard_fact_checking_module": "Hard Fact-Checking Module",
        "claim_evaluation_criteria": "Each sentence is treated as a potential claim, then evaluated according to:",
        "criteria_list": "- presence of dates, numbers, proper names,\n- presence of clear attribution,\n- degree of absolutism,\n- sensationalist charge,\n- probable quality of mentioned sources,\n- narrative red flags.",
        "practical_hard_fact_formula": "Practical Hard Fact Score Formula",
        "qs": "QS: quality of sources",
        "vc": "VC: average verifiability of claims",
        "rc": "RC: average risk of claims",
        "f": "F: number of red flags",
        "disclaimer": "This app does not replace a real journalist, a real researcher, or a clerk of reality. But it already removes some masks from the parading text.",
        "presence_of_source_markers": "Presence of source or data markers",
        "verifiability_clues": "Verifiability clues found: links, figures, dates or percentages",
        "text_contains_nuances": "The text contains nuances, limits or counterpoints",
        "text_evokes_robust_sources": "The text evokes potentially robust or institutional sources",
        "some_claims_verifiable": "Some claims are well-anchored enough to be properly verified",
        "overly_assertive_language": "Overly assertive or absolutist language",
        "notable_emotional_sensational_charge": "Notable emotional or sensational charge",
        "almost_total_absence_of_verifiable_elements": "Almost total absence of verifiable elements",
        "text_too_short": "Text too short to seriously support a strong claim",
        "multiple_claims_very_fragile": "Several central claims are very fragile given the present clues",
        "to_verify": "To verify",
        "rather_verifiable": "Rather verifiable",
        "very_fragile": "Very fragile",
        "low_credibility": "Low credibility",
        "prudent_credibility": "Prudent credibility",
        "rather_credible": "Rather credible",
        "strong_credibility": "Strong credibility",
        "yes": "Yes",
        "no": "No",
        "llm_analysis": "Mecroyance Analysis for LLM",
        "llm_intro": "This section applies derived models from the treatise to evaluate the cognitive posture of a system (AI or human).",
        "overconfidence": "Overconfidence (Asymmetry)",
        "calibration": "Relative Calibration (Ratio)",
        "revisability": "Revisability (R)",
        "cognitive_closure": "Cognitive Closure",
        "cognitive_potential": "Cognitive Potential",
        "cognitive_field": "Cognitive Field (Attractor)",
        "cognitive_curvature": "Cognitive Curvature (κ)",
        "interpretation": "Interpretation",
        "llm_metrics": "LLM Metrics",
        "zone_closure": "Cognitive closure zone: certainty exceeds cognitive anchoring.",
        "zone_stability": "Revisable stability zone: mecroyance accompanies without dominating.",
        "zone_lucidity": "Increasing lucidity zone: doubt structures cognition.",
        "zone_rare": "Rare zone: highly integrated and reflexive cognition.",
        "zone_pansapience": "Hypothetical pan-sapience: limit horizon of an almost totally revisable cognition.",
        "zone_asymptote": "Ideal asymptote: totality of knowledge and integration, without rigidification.",
        "out_of_spectrum": "Value out of theoretical spectrum.",
    },
    "Español": {
        "title": "🧠 Mecroyance Lab — Analizador de Credibilidad",
        "analyze": "🔍 Analizar artículo",
        "topic": "Tema a analizar",
        "analyze_topic": "📰 Analizar 10 artículos sobre este tema",
        "url": "Analizar artículo por URL",
        "load_url": "🌐 Cargar artículo desde URL",
        "paste": "Pegue aquí un artículo o texto",
        "verdict": "Veredicto",
        "summary": "Resumen del análisis",
        "tagline": "Su fórmula como brújula, un control más estricto como guardia fronterizo.",
        "settings": "Ajustes",
        "load_example": "Cargar ejemplo",
        "show_method": "Mostrar método",
        "hard_fact_score_scale": "Escala del Hard Fact Score",
        "scale_0_5": "0–5 : muy frágil",
        "scale_6_9": "6–9 : dudoso",
        "scale_10_14": "10–14 : plausible pero requiere contrastación",
        "scale_15_20": "15–20 : estructuralmente robusto",
        "analyze_multiple_articles_by_topic": "Análisis de múltiples artículos por tema",
        "searching_analyzing_articles": "Buscando y analizando artículos...",
        "articles_analyzed": "artículos analizados.",
        "analyzed_articles": "Artículos Analizados",
        "avg_hard_fact": "Promedio Hard Fact",
        "avg_classic_score": "Promedio Score Clásico",
        "topic_doxa_index": "Índice de doxa del tema",
        "high": "Alto",
        "medium": "Medio",
        "low": "Bajo",
        "credibility_score_dispersion": "Dispersión de puntuaciones de credibilidad",
        "article_label": "Artículo",
        "analyzed_articles_details": "Detalle de artículos analizados",
        "no_exploitable_articles_found": "No se encontraron artículos explotables para este tema.",
        "enter_keyword_first": "Ingrese primero una palabra clave o tema.",
        "article_loaded_from_url": "Artículo cargado desde URL.",
        "unable_to_retrieve_text": "No se pudo recuperar el texto de esta URL.",
        "paste_url_first": "Pegue primero una URL.",
        "classic_score": "Score Clásico",
        "improved_score": "Score Mejorado",
        "hard_fact_score": "Hard Fact Score",
        "help_classic_score": "M = (G + N) − D",
        "help_improved_score": "Adición de V y penalización R",
        "help_hard_fact_score": "Control más estricto de afirmaciones y fuentes",
        "credibility_gauge": "Indicador de credibilidad",
        "fragile": "Frágil",
        "fragile_message": "El texto presenta fuertes debilidades estructurales o fácticas.",
        "doubtful": "Dudoso",
        "doubtful_message": "El texto contiene algunos elementos creíbles, pero sigue siendo muy incierto.",
        "plausible": "Plausible",
        "plausible_message": "El texto parece generalmente plausible, pero aún requiere verificación.",
        "robust": "Robusto",
        "robust_message": "El texto presenta una base estructural y fáctica bastante sólida.",
        "score": "Puntuación",
        "strengths_detected": "Fortalezas detectadas",
        "few_strong_signals": "Pocos señales fuertes identificadas.",
        "weaknesses_detected": "Debilidades detectadas",
        "no_major_weakness": "No se identificaron debilidades mayores por heurística.",
        "hard_fact_checking_by_claim": "Fact-checking duro por afirmación",
        "claim": "Afirmación",
        "status": "Estado",
        "verifiability": "Verificabilidad",
        "risk": "Riesgo",
        "number": "Número",
        "date": "Fecha",
        "named_entity": "Entidad nombrada",
        "attributed_source": "Fuente atribuida",
        "paste_longer_text": "Pegue un texto un poco más largo para obtener un mapeo fino de las afirmaciones.",
        "paste_text_or_load_url": "Pegue un texto o cargue una URL, luego haga clic en « 🔍 Analizar artículo ».",
        "method": "Método",
        "original_formula": "Fórmula Original",
        "articulated_knowledge_density": "G : densidad de conocimiento articulado — fuentes, cifras, nombres, referencias, rastros verificables.",
        "integration": "N : integración — contexto, matices, reservas, coherencia argumentativa.",
        "assertive_rigidity": "D : rigidez asertiva — certezas no sustentadas, carga emocional.",
        "improved_variant": "Variante Mejorada",
        "addition_of_v_and_r": "Adición de V para verificabilidad y R como penalización retórica.",
        "hard_fact_checking_module": "Módulo de Fact-Checking Duro",
        "claim_evaluation_criteria": "Cada oración se trata como una afirmación potencial, luego se evalúa según:",
        "criteria_list": "- presencia de fechas, números, nombres propios,\n- presencia de atribución clara,\n- grado de absolutismo,\n- carga sensacionalista,\n- calidad probable de las fuentes mencionadas,\n- señales rojas narrativas.",
        "practical_hard_fact_formula": "Fórmula Práctica del Hard Fact Score",
        "qs": "QS: calidad de las fuentes",
        "vc": "VC: verificabilidad promedio de las afirmaciones",
        "rc": "RC: riesgo promedio de las afirmaciones",
        "f": "F: número de banderas rojas",
        "disclaimer": "Esta aplicación no reemplaza a un periodista real, un investigador real ni a un escribano de la realidad. Pero ya quita algunas máscaras al texto que desfila.",
        "presence_of_source_markers": "Presencia de marcadores de fuentes o datos",
        "verifiability_clues": "Pistas de verificabilidad encontradas: enlaces, cifras, fechas o porcentages",
        "text_contains_nuances": "El texto contiene matices, límites o contrapuntos",
        "text_evokes_robust_sources": "El texto evoca fuentes potencialmente robustas o institucionales",
        "some_claims_verifiable": "Algunas afirmaciones están lo suficientemente ancladas como para ser verificadas adecuadamente",
        "overly_assertive_language": "Lenguaje demasiado asertivo o absolutista",
        "notable_emotional_sensational_charge": "Carga emocional o sensacionalista notable",
        "almost_total_absence_of_verifiable_elements": "Ausencia casi total de elementos verificables",
        "text_too_short": "Texto demasiado corto para sustentar seriamente una afirmación fuerte",
        "multiple_claims_very_fragile": "Varias afirmaciones centrales son muy frágiles dados los indicios presentes",
        "to_verify": "Por verificar",
        "rather_verifiable": "Bastante verificable",
        "very_fragile": "Muy frágil",
        "low_credibility": "Credibilidad baja",
        "prudent_credibility": "Credibilidad prudente",
        "rather_credible": "Bastante creíble",
        "strong_credibility": "Credibilidad fuerte",
        "yes": "Sí",
        "no": "No",
        "llm_analysis": "Análisis de Mecroyance para LLM",
        "llm_intro": "Esta sección aplica modelos derivados del tratado para evaluar la postura cognitiva de un sistema (IA o humano).",
        "overconfidence": "Sobreconfianza (Asimetría)",
        "calibration": "Calibración relativa (Ratio)",
        "revisability": "Revisabilidad (R)",
        "cognitive_closure": "Cierre cognitivo",
        "cognitive_potential": "Potencial cognitivo",
        "cognitive_field": "Campo cognitivo (Atractor)",
        "cognitive_curvature": "Curvatura cognitiva (κ)",
        "interpretation": "Interpretación",
        "llm_metrics": "Métricas LLM",
        "zone_closure": "Zona de cierre cognitivo: la certeza excede el anclaje cognitivo.",
        "zone_stability": "Zona de estabilidad revisable: la mecroyance acompaña sin dominar.",
        "zone_lucidity": "Zona de lucidez creciente: la duda estructura la cognición.",
        "zone_rare": "Zona rara: cognición altamente integrada y reflexiva.",
        "zone_pansapience": "Pan-sapiencia hipotética: horizonte límite de una cognición casi totalmente revisable.",
        "zone_asymptote": "Asíntota ideal: totalidad del conocimiento y la integración, sin rigidización.",
        "out_of_spectrum": "Valor fuera del espectro teórico.",
    },
    "Philippine": {
        "title": "🧠 Mecroyance Lab — Credibility Analyzer",
        "analyze": "🔍 Suriin ang artikulo",
        "topic": "Paksa na susuriin",
        "analyze_topic": "📰 Suriin ang 10 artikulo sa paksang ito",
        "url": "Suriin ang artikulo mula sa URL",
        "load_url": "🌐 I-load ang artikulo mula sa URL",
        "paste": "I-paste ang artikulo o teksto rito",
        "verdict": "Hatol",
        "summary": "Buod ng pagsusuri",
        "tagline": "Ang iyong formula bilang kumpas, mas mahigpit na kontrol bilang bantay-dagat.",
        "settings": "Mga Setting",
        "load_example": "I-load ang halimbawa",
        "show_method": "Ipakita ang pamamaraan",
        "hard_fact_score_scale": "Scale ng Hard Fact Score",
        "scale_0_5": "0–5 : napakarupok",
        "scale_6_9": "6–9 : kahina-hinala",
        "scale_10_14": "10–14 : kapani-paniwala ngunit kailangan ng cross-referencing",
        "scale_15_20": "15–20 : matibay ang istruktura",
        "analyze_multiple_articles_by_topic": "Suriin ang maraming artikulo ayon sa paksa",
        "searching_analyzing_articles": "Hinahanap at sinusuri ang mga artikulo...",
        "articles_analyzed": "mga artikulong nasuri.",
        "analyzed_articles": "Mga Nasuring Artikulo",
        "avg_hard_fact": "Avg Hard Fact",
        "avg_classic_score": "Avg Classic Score",
        "topic_doxa_index": "Topic Doxa Index",
        "high": "Mataas",
        "medium": "Katamtaman",
        "low": "Mababa",
        "credibility_score_dispersion": "Dispersion ng Credibility Score",
        "article_label": "Artikulo",
        "analyzed_articles_details": "Mga detalye ng nasuring artikulo",
        "no_exploitable_articles_found": "Walang nahanap na magagamit na artikulo para sa paksang ito.",
        "enter_keyword_first": "Maglagay muna ng keyword o paksa.",
        "article_loaded_from_url": "Na-load na ang artikulo mula sa URL.",
        "unable_to_retrieve_text": "Hindi makuha ang teksto mula sa URL na ito.",
        "paste_url_first": "I-paste muna ang URL.",
        "classic_score": "Classic Score",
        "improved_score": "Improved Score",
        "hard_fact_score": "Hard Fact Score",
        "help_classic_score": "M = (G + N) − D",
        "help_improved_score": "Pagdaragdag ng V at parusa sa R",
        "help_hard_fact_score": "Mas mahigpit na kontrol sa mga claim at source",
        "credibility_gauge": "Credibility Gauge",
        "fragile": "Marupok",
        "fragile_message": "Ang teksto ay nagpapakita ng malakas na kahinaan sa istruktura o katotohanan.",
        "doubtful": "Kahina-hinala",
        "doubtful_message": "Ang teksto ay naglalaman ng ilang kapani-paniwalang elemento, ngunit nananatiling napaka-hindi sigurado.",
        "plausible": "Kapani-paniwala",
        "plausible_message": "Ang teksto ay tila kapani-paniwala sa pangkalahatan, ngunit nangangailangan pa rin ng beripikasyon.",
        "robust": "Matibay",
        "robust_message": "Ang teksto ay nagpapakita ng medyo matibay na istruktura at batayan sa katotohanan.",
        "score": "Iskor",
        "strengths_detected": "Mga nakitang kalakasan",
        "few_strong_signals": "Kakaunting malakas na signal ang natukoy.",
        "weaknesses_detected": "Mga nakitang kahinaan",
        "no_major_weakness": "Walang natukoy na malaking kahinaan sa pamamagitan ng heuristics.",
        "hard_fact_checking_by_claim": "Hard fact-checking ayon sa claim",
        "claim": "Claim",
        "status": "Katayuan",
        "verifiability": "Verifiability",
        "risk": "Panganib",
        "number": "Numero",
        "date": "Petsa",
        "named_entity": "Named Entity",
        "attributed_source": "Attributed Source",
        "paste_longer_text": "I-paste ang mas mahabang teksto upang makakuha ng masusing mapping ng mga claim.",
        "paste_text_or_load_url": "I-paste ang teksto o i-load ang URL, pagkatapos ay i-click ang « 🔍 Suriin ang artikulo ».",
        "method": "Pamamaraan",
        "original_formula": "Orihinal na Formula",
        "articulated_knowledge_density": "G : articulated knowledge density — mga source, pigura, pangalan, sanggunian, mga bakas na maaaring ma-verify.",
        "integration": "N : integration — konteksto, mga nuance, reserbasyon, argumentative coherence.",
        "assertive_rigidity": "D : assertive rigidity — mga katiyakang walang basehan, emosyonal na karga.",
        "improved_variant": "Improved Variant",
        "addition_of_v_and_r": "Pagdaragdag ng V para sa verifiability at R bilang parusang retorika.",
        "hard_fact_checking_module": "Hard Fact-Checking Module",
        "claim_evaluation_criteria": "Ang bawat pangungusap ay itinuturing na potensyal na claim, pagkatapos ay sinusuri ayon sa:",
        "criteria_list": "- pagkakaroon ng mga petsa, numero, tamang pangalan,\n- pagkakaroon ng malinaw na attribution,\n- antas ng absolutismo,\n- sensationalist na karga,\n- malamang na kalidad ng mga nabanggit na source,\n- mga narrative red flag.",
        "practical_hard_fact_formula": "Praktikal na Formula ng Hard Fact Score",
        "qs": "QS: kalidad ng mga source",
        "vc": "VC: average verifiability ng mga claim",
        "rc": "RC: average na panganib ng mga claim",
        "f": "F: bilang ng mga red flag",
        "disclaimer": "Ang app na ito ay hindi pumapalit sa isang tunay na mamamahayag, isang tunay na mananaliksik, o isang klerk ng katotohanan. Ngunit tinatanggal na nito ang ilang maskara sa tekstong nagpaparada.",
        "presence_of_source_markers": "Pagkakaroon ng mga source o data marker",
        "verifiability_clues": "Nahanap na mga pahiwatig ng verifiability: mga link, pigura, petsa o porsyento",
        "text_contains_nuances": "Ang teksto ay naglalaman ng mga nuance, limitasyon o counterpoint",
        "text_evokes_robust_sources": "Ang teksto ay tumutukoy sa mga potensyal na matibay o institusyonal na source",
        "some_claims_verifiable": "Ang ilang mga claim ay sapat na naka-angkla upang ma-verify nang maayos",
        "overly_assertive_language": "Masyadong mapilit o absolutistang pananalita",
        "notable_emotional_sensational_charge": "Kapansin-pansing emosyonal o sensationalist na karga",
        "almost_total_absence_of_verifiable_elements": "Halos kabuuang kawalan ng mga elementong maaaring ma-verify",
        "text_too_short": "Masyadong maikli ang teksto upang seryosong suportahan ang isang malakas na claim",
        "multiple_claims_very_fragile": "Maraming sentral na claim ang napakarupok base sa mga kasalukuyang pahiwatig",
        "to_verify": "Susuriin",
        "rather_verifiable": "Medyo mabe-verify",
        "very_fragile": "Napakarupok",
        "low_credibility": "Mababang kredibilidad",
        "prudent_credibility": "Maingat na kredibilidad",
        "rather_credible": "Medyo kapani-paniwala",
        "strong_credibility": "Malakas na kredibilidad",
        "yes": "Oo",
        "no": "Hindi",
        "llm_analysis": "Mecroyance Analysis para sa LLM",
        "llm_intro": "Inilalapat ng seksyong ito ang mga modelong hango sa treatise upang suriin ang cognitive posture ng isang sistema (AI o tao).",
        "overconfidence": "Overconfidence (Asymmetry)",
        "calibration": "Relative Calibration (Ratio)",
        "revisability": "Revisability (R)",
        "cognitive_closure": "Cognitive Closure",
        "cognitive_potential": "Cognitive Potential",
        "cognitive_field": "Cognitive Field (Attractor)",
        "cognitive_curvature": "Cognitive Curvature (κ)",
        "interpretation": "Interpretasyon",
        "llm_metrics": "Mga Metriko ng LLM",
        "zone_closure": "Zone ng cognitive closure: ang katiyakan ay lumalampas sa cognitive anchoring.",
        "zone_stability": "Zone ng revisable stability: ang mecroyance ay sumasama nang hindi nangingibabaw.",
        "zone_lucidity": "Zone ng tumataas na lucidity: ang duda ang nagpapatakbo sa cognition.",
        "zone_rare": "Rare zone: mataas na integrated at reflexive na cognition.",
        "zone_pansapience": "Hypothetical pan-sapience: limitadong horizon ng isang halos ganap na revisable na cognition.",
        "zone_asymptote": "Ideal asymptote: kabuuan ng kaalaman at integrasyon, nang walang rigidification.",
        "out_of_spectrum": "Halaga sa labas ng theoretical spectrum.",
    },
}

# -----------------------------
# Langue par défaut
# -----------------------------
lang = st.sidebar.selectbox("Langue / Language", list(translations.keys()))

# -----------------------------
# Classes de Cognition (Nouveau)
# -----------------------------
class Cognition:
    def __init__(self, gnosis: float, nous: float, doxa: float):
        self.G = self.clamp(gnosis)
        self.N = self.clamp(nous)
        self.D = self.clamp(doxa)
        self.M = self.compute_mecroyance()

    @staticmethod
    def clamp(value: float, min_val: float = 0.0, max_val: float = 10.0) -> float:
        return max(min_val, min(max_val, value))

    def compute_mecroyance(self) -> float:
        return (self.G + self.N) - self.D

    def interpret(self) -> str:
        m = self.M
        if m < 0:
            return translations[lang]["zone_closure"]
        elif 0 <= m <= 10:
            return translations[lang]["zone_stability"]
        elif 10 < m <= 17:
            return translations[lang]["zone_lucidity"]
        elif 17 < m < 19:
            return translations[lang]["zone_rare"]
        elif 19 <= m < 20:
            return translations[lang]["zone_pansapience"]
        elif m == 20:
            return translations[lang]["zone_asymptote"]
        else:
            return translations[lang]["out_of_spectrum"]

# -----------------------------
# Données d'exemple
# -----------------------------
SAMPLE_ARTICLE = """L'intelligence artificielle va remplacer 80% des emplois d'ici 2030, selon une étude choc publiée hier par le cabinet GlobalTech. Le rapport de 45 pages affirme que les secteurs de la finance et de la santé seront les plus touchés. "C'est une révolution sans précédent", déclare Jean Dupont, expert en robotique. Cependant, certains économistes comme Marie Curie restent prudents : "Il faut nuancer ces chiffres, car de nouveaux métiers vont apparaître." L'étude précise que 12 millions de postes pourraient être créés en Europe. Malgré cela, l'inquiétude grandit chez les salariés qui craignent pour leur avenir. Il est absolument certain que nous allons vers une crise sociale majeure si rien n'est fait immédiatement."""

# -----------------------------
# Fonctions utilitaires
# -----------------------------
def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def extract_article_from_url(url: str) -> str:
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except:
        return ""

def search_articles_by_keyword(keyword: str, max_results: int = 10) -> List[Dict]:
    """Recherche des articles sur DuckDuckGo filtrés par domaines de confiance."""
    trusted_domains = [
        "lemonde.fr", "lefigaro.fr", "liberation.fr", "francetvinfo.fr", 
        "lexpress.fr", "lepoint.fr", "nouvelobs.com", "la-croix.com",
        "lesechos.fr", "latribune.fr", "mediapart.fr", "arte.tv",
        "bbc.com", "reuters.com", "apnews.com", "nytimes.com", 
        "theguardian.com", "bloomberg.com", "dw.com", "aljazeera.com",
        "nature.com", "science.org", "who.int", "un.org", "worldbank.org",
        "elpais.com", "elmundo.es", "corriere.it", "spiegel.de", "zeit.de"
    ]
    
    results = []
    try:
        with DDGS() as ddgs:
            # Requête assouplie pour plus de résultats
            query = f"{keyword} (actualités OR news OR article OR analyse OR reportage OR étude)"
            ddg_results = list(ddgs.text(query, max_results=max_results * 5))
            
            for r in ddg_results:
                url = r.get('href', '')
                if any(domain in url for domain in trusted_domains):
                    results.append({
                        "title": r.get('title', 'Sans titre'),
                        "url": url,
                        "source": url.split('/')[2]
                    })
                    if len(results) >= max_results:
                        break
    except Exception as e:
        st.warning(f"Erreur lors de la recherche : {e}")
    return results

@dataclass
class Claim:
    text: str
    has_number: bool
    has_date: bool
    has_named_entity: bool
    has_source_cue: bool
    absolutism: int
    emotional_charge: int
    verifiability: float
    risk: float
    status: str

def analyze_claim(sentence: str) -> Claim:
    has_number = bool(re.search(r'\d+', sentence))
    has_date = bool(re.search(r'\d{4}|janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre|lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche', sentence, re.I))
    has_named_entity = bool(re.search(r'[A-Z][a-z]+ [A-Z][a-z]+|[A-Z]{2,}', sentence))
    
    source_cues = ['selon', 'affirme', 'déclare', 'rapport', 'étude', 'expert', 'source', 'dit', 'écrit', 'publié', 'according to', 'claims', 'states', 'report', 'study', 'expert', 'source', 'says', 'writes', 'published']
    has_source_cue = any(cue in sentence.lower() for cue in source_cues)
    
    absolutist_words = ['toujours', 'jamais', 'absolument', 'certain', 'prouvé', 'incontestable', 'tous', 'aucun', 'always', 'never', 'absolutely', 'certain', 'proven', 'unquestionable', 'all', 'none']
    absolutism = sum(1 for word in absolutist_words if word in sentence.lower())
    
    emotional_words = ['choc', 'incroyable', 'terrible', 'peur', 'menace', 'scandale', 'révolution', 'urgent', 'shock', 'incredible', 'terrible', 'fear', 'threat', 'scandal', 'revolution', 'urgent']
    emotional_charge = sum(1 for word in emotional_words if word in sentence.lower())
    
    v_score = (has_number * 5) + (has_date * 5) + (has_named_entity * 5) + (has_source_cue * 5)
    r_score = (absolutism * 7) + (emotional_charge * 7)
    
    v_score = clamp(v_score, 0, 20)
    r_score = clamp(r_score, 0, 20)
    
    if v_score < 5:
        status = translations[lang]["very_fragile"]
    elif v_score < 12:
        status = translations[lang]["to_verify"]
    else:
        status = translations[lang]["rather_verifiable"]
        
    return Claim(sentence, has_number, has_date, has_named_entity, has_source_cue, absolutism, emotional_charge, v_score, r_score, status)

def analyze_article(text: str):
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    article_length = len(words)
    
    source_markers = len(re.findall(r'selon|affirme|déclare|rapport|étude|expert|source|according to|claims|states|report|study|expert|source', text.lower()))
    citation_like = len(re.findall(r'"|\'|«|»', text))
    nuance_markers = len(re.findall(r'cependant|pourtant|néanmoins|toutefois|mais|nuancer|prudence|possible|peut-être|however|yet|nevertheless|nonetheless|but|nuance|caution|possible|maybe', text.lower()))
    
    G = clamp(source_markers * 1.5 + citation_like * 0.5, 0, 10)
    N = clamp(nuance_markers * 2 + (article_length / 100), 0, 10)
    
    certainty = len(re.findall(r'certain|absolument|prouvé|évident|incontestable|certainly|absolutely|proven|obvious|unquestionable', text.lower()))
    emotional = len(re.findall(r'choc|incroyable|terrible|peur|menace|scandale|révolution|urgent|shock|incredible|terrible|fear|threat|scandal|revolution|urgent', text.lower()))
    D = clamp(certainty * 2 + emotional * 1.5, 0, 10)
    
    M = round((G + N) - D, 1)
    
    V = clamp(G * 0.8 + N * 0.2, 0, 10)
    R = clamp(D * 0.7 + (emotional * 1.2), 0, 10)
    improved = round((G + N + V) - (D + R), 1)
    
    claims = [analyze_claim(s) for s in sentences[:15]]
    
    avg_claim_verifiability = sum(c.verifiability for c in claims) / len(claims) if claims else 0
    avg_claim_risk = sum(c.risk for c in claims) / len(claims) if claims else 0
    
    source_quality = clamp(source_markers * 3 - (emotional * 2), 0, 20)
    
    red_flags = []
    if D > 8: red_flags.append("Doxa saturée")
    if emotional > 5: red_flags.append("Pathos excessif")
    if G < 2: red_flags.append("Désert documentaire")
    if article_length < 50: red_flags.append("Format indigent")
    
    hard_fact_score_raw = (0.18 * G + 0.12 * N + 0.20 * V + 0.22 * source_quality + 0.18 * avg_claim_verifiability) - (0.16 * D + 0.12 * R + 0.18 * avg_claim_risk + 0.9 * len(red_flags))
    hard_fact_score = round(clamp(hard_fact_score_raw + 8, 0, 20), 1)

    if hard_fact_score < 6:
        verdict = translations[lang]["low_credibility"]
    elif hard_fact_score < 10:
        verdict = translations[lang]["prudent_credibility"]
    elif hard_fact_score < 15:
        verdict = translations[lang]["rather_credible"]
    else:
        verdict = translations[lang]["strong_credibility"]

    strengths = []
    weaknesses = []

    if source_markers >= 2:
        strengths.append(translations[lang]["presence_of_source_markers"])
    if citation_like >= 2:
        strengths.append(translations[lang]["verifiability_clues"])
    if nuance_markers >= 2:
        strengths.append(translations[lang]["text_contains_nuances"])
    if source_quality >= 12:
        strengths.append(translations[lang]["text_evokes_robust_sources"])
    if any(c.status == translations[lang]["rather_verifiable"] for c in claims):
        strengths.append(translations[lang]["some_claims_verifiable"])

    if certainty >= 3:
        weaknesses.append(translations[lang]["overly_assertive_language"])
    if emotional >= 2:
        weaknesses.append(translations[lang]["notable_emotional_sensational_charge"])
    if source_markers == 0 and citation_like == 0:
        weaknesses.append(translations[lang]["almost_total_absence_of_verifiable_elements"])
    if article_length < 80:
        weaknesses.append(translations[lang]["text_too_short"])
    weaknesses.extend(red_flags)
    if sum(1 for c in claims if c.status == translations[lang]["very_fragile"]) >= 2:
        weaknesses.append(translations[lang]["multiple_claims_very_fragile"])

    return {
        "words": len(words),
        "sentences": len(sentences),
        "G": G,
        "N": N,
        "D": D,
        "M": M,
        "V": V,
        "R": R,
        "improved": improved,
        "source_quality": source_quality,
        "avg_claim_risk": avg_claim_risk,
        "avg_claim_verifiability": avg_claim_verifiability,
        "hard_fact_score": hard_fact_score,
        "verdict": verdict,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "claims": claims,
        "red_flags": red_flags,
    }

def analyze_multiple_articles(keyword: str, max_results: int = 10):
    articles = search_articles_by_keyword(keyword, max_results)
    results = []
    for art in articles:
        try:
            full_text = extract_article_from_url(art['url'])
            if len(full_text) > 200:
                analysis = analyze_article(full_text)
                results.append({
                    "Source": art['source'],
                    "Titre": art['title'],
                    "Score classique": analysis['M'],
                    "Hard Fact Score": analysis['hard_fact_score'],
                    "Verdict": analysis['verdict'],
                    "URL": art['url']
                })
        except:
            continue
    return results

# -----------------------------
# Interface
# -----------------------------
st.title(translations[lang]["title"])
st.caption(translations[lang]["tagline"])

with st.sidebar:
    st.header(translations[lang]["settings"])
    use_sample = st.button(translations[lang]["load_example"])
    show_method = st.toggle(translations[lang]["show_method"], value=True)
    st.divider()
    st.subheader(translations[lang]["hard_fact_score_scale"])
    st.markdown(
        f"""
- **0–5** : {translations[lang]["scale_0_5"]}  
- **6–9** : {translations[lang]["scale_6_9"]}  
- **10–14** : {translations[lang]["scale_10_14"]}  
- **15–20** : {translations[lang]["scale_15_20"]}
        """
    )

if "article" not in st.session_state:
    st.session_state.article = SAMPLE_ARTICLE

if use_sample:
    st.session_state.article = SAMPLE_ARTICLE

st.subheader(translations[lang]["analyze_multiple_articles_by_topic"])

keyword = st.text_input(translations[lang]["topic"], placeholder="ex : intelligence artificielle")

if st.button(translations[lang]["analyze_topic"], key="analyze_topic"):
    if keyword.strip():
        st.info(translations[lang]["searching_analyzing_articles"])
        multiple_results = analyze_multiple_articles(keyword.strip(), max_results=10)

        if multiple_results:
            df_multi = pd.DataFrame(multiple_results)
            df_multi = df_multi.sort_values("Hard Fact Score", ascending=False)
            st.success(f"{len(df_multi)} {translations[lang]['articles_analyzed']}")
            moyenne_hf = round(df_multi["Hard Fact Score"].mean(), 1)
            moyenne_classique = round(df_multi["Score classique"].mean(), 1)
            c1, c2, c3 = st.columns(3)
            c1.metric(translations[lang]["analyzed_articles"], len(df_multi))
            c2.metric(translations[lang]["avg_hard_fact"], moyenne_hf)
            c3.metric(translations[lang]["avg_classic_score"], moyenne_classique)
            ecart_type_hf = round(df_multi["Hard Fact Score"].std(), 2)
            indice_doxa = "Élevé" if ecart_type_hf < 1.5 else ("Moyen" if ecart_type_hf < 3 else "Faible")
            st.metric(translations[lang]["topic_doxa_index"], translations[lang][indice_doxa.lower()])
            st.subheader(translations[lang]["credibility_score_dispersion"])
            df_plot = df_multi.copy()
            df_plot["Article"] = [f"{translations[lang]['article_label']} {i+1}" for i in range(len(df_plot))]
            st.bar_chart(df_plot.set_index("Article")["Hard Fact Score"])
            st.subheader(translations[lang]["analyzed_articles_details"])
            st.dataframe(df_multi, use_container_width=True, hide_index=True)
        else:
            st.warning(translations[lang]["no_exploitable_articles_found"])
    else:
        st.warning(translations[lang]["enter_keyword_first"])

url = st.text_input(translations[lang]["url"])

if st.button(translations[lang]["load_url"], key="load_url"):
    if url:
        texte = extract_article_from_url(url)
        if texte:
            st.session_state.article = texte
            st.success(translations[lang]["article_loaded_from_url"])
        else:
            st.error(translations[lang]["unable_to_retrieve_text"])
    else:
        st.warning(translations[lang]["paste_url_first"])

article = st.text_area(
    translations[lang]["paste"],
    value=st.session_state.article,
    height=320,
)

st.session_state.article = article

analyser = st.button(
    translations[lang]["analyze"],
    use_container_width=True,
    type="primary",
    key="analyze_single",
)

if analyser:
    result = analyze_article(article)
    col1, col2, col3 = st.columns(3)
    col1.metric(translations[lang]["classic_score"], result["M"], help=translations[lang]["help_classic_score"])
    col2.metric(translations[lang]["improved_score"], result["improved"], help=translations[lang]["help_improved_score"])
    col3.metric(translations[lang]["hard_fact_score"], result["hard_fact_score"], help=translations[lang]["help_hard_fact_score"])

    score = result["hard_fact_score"]
    if score <= 6:
        couleur, etiquette, message = "🔴", translations[lang]["fragile"], translations[lang]["fragile_message"]
    elif score <= 11:
        couleur, etiquette, message = "🟠", translations[lang]["doubtful"], translations[lang]["doubtful_message"]
    elif score <= 15:
        couleur, etiquette, message = "🟡", translations[lang]["plausible"], translations[lang]["plausible_message"]
    else:
        couleur, etiquette, message = "🟢", translations[lang]["robust"], translations[lang]["robust_message"]

    st.subheader(f"{couleur} {translations[lang]['credibility_gauge']} : {etiquette}")
    st.progress(score / 20)
    st.caption(f"{translations[lang]['score']} : {score}/20 — {message}")

    st.subheader(f"{translations[lang]['verdict']} : {result['verdict']}")
    st.subheader(translations[lang]["summary"])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("G — gnōsis", result["G"])
    m2.metric("N — nous", result["N"])
    m3.metric("D — doxa", result["D"])
    m4.metric("V — vérifiabilité", result["V"])

    m5, m6, m7, m8 = st.columns(4)
    m5.metric(translations[lang]["qs"], result["source_quality"])
    m6.metric(translations[lang]["rc"], result["avg_claim_risk"])
    m7.metric(translations[lang]["vc"], result["avg_claim_verifiability"])
    m8.metric(translations[lang]["f"], len(result["red_flags"]))

    with st.expander(translations[lang]["strengths_detected"], expanded=True):
        if result["strengths"]:
            for item in result["strengths"]: st.success(item)
        else: st.info(translations[lang]["few_strong_signals"])

    with st.expander(translations[lang]["weaknesses_detected"], expanded=True):
        if result["weaknesses"]:
            for item in result["weaknesses"]: st.error(item)
        else: st.success(translations[lang]["no_major_weakness"])

    # --- Section Analyse LLM (Nouveau) ---
    st.divider()
    st.subheader(translations[lang]["llm_analysis"])
    st.info(translations[lang]["llm_intro"])
    
    cog = Cognition(result["G"], result["N"], result["D"])
    
    # Modèles dérivés
    overconfidence = result["D"] - (result["G"] + result["N"])
    calibration = result["D"] / (result["G"] + result["N"]) if (result["G"] + result["N"]) > 0 else 10
    revisability = (result["G"] + result["N"] + result["V"]) - result["D"]
    closure = (result["D"] * (1 + len(result["red_flags"])/5)) / (result["G"] + result["N"]) if (result["G"] + result["N"]) > 0 else 10
    potential = result["D"] - (result["G"] + result["N"])
    field = result["D"] / (result["G"] + result["N"]) if (result["G"] + result["N"]) > 0 else 10
    curvature = result["D"] / (result["G"] + result["N"]) if (result["G"] + result["N"]) > 0 else 10

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(translations[lang]["overconfidence"], round(overconfidence, 2))
    c2.metric(translations[lang]["calibration"], round(calibration, 2))
    c3.metric(translations[lang]["revisability"], round(revisability, 2))
    c4.metric(translations[lang]["cognitive_closure"], round(closure, 2))
    
    c5, c6, c7 = st.columns(3)
    c5.metric(translations[lang]["cognitive_potential"], round(potential, 2))
    c6.metric(translations[lang]["cognitive_field"], round(field, 2))
    c7.metric(translations[lang]["cognitive_curvature"], round(curvature, 2))
    
    st.markdown(f"**{translations[lang]['interpretation']} :** {cog.interpret()}")

    st.subheader(translations[lang]["hard_fact_checking_by_claim"])
    claims_df = pd.DataFrame([
        {
            translations[lang]["claim"]: c.text,
            translations[lang]["status"]: c.status,
            f"{translations[lang]['verifiability']} /20": c.verifiability,
            f"{translations[lang]['risk']} /20": c.risk,
            translations[lang]["number"]: translations[lang]["yes"] if c.has_number else translations[lang]["no"],
            translations[lang]["date"]: translations[lang]["yes"] if c.has_date else translations[lang]["no"],
            translations[lang]["named_entity"]: translations[lang]["yes"] if c.has_named_entity else translations[lang]["no"],
            translations[lang]["attributed_source"]: translations[lang]["yes"] if c.has_source_cue else translations[lang]["no"],
        } for c in result["claims"]
    ])
    if not claims_df.empty: st.dataframe(claims_df, use_container_width=True, hide_index=True)
    else: st.info(translations[lang]["paste_longer_text"])
else:
    st.info(translations[lang]["paste_text_or_load_url"])

if show_method:
    st.subheader(translations[lang]["method"])
    st.markdown(f"""
### {translations[lang]["original_formula"]}
`M = (G + N) − D`
- {translations[lang]["articulated_knowledge_density"]}
- {translations[lang]["integration"]}
- {translations[lang]["assertive_rigidity"]}

### {translations[lang]["llm_metrics"]}
- **{translations[lang]["overconfidence"]}** : `D - (G + N)`
- **{translations[lang]["calibration"]}** : `D / (G + N)`
- **{translations[lang]["revisability"]}** : `(G + N + V) - D`
- **{translations[lang]["cognitive_closure"]}** : `(D * S) / (G + N)`

{translations[lang]["disclaimer"]}
""")
