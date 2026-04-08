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
        "assertive_rigidity": "D : assertive rigidity — unsupported certainties, rhetorical exuberance, doxic inflation.",
        "improved_variant": "Improved Variant",
        "addition_of_v_and_r": "Addition of V for verifiability and R as rhetorical penalty.",
        "hard_fact_checking_module": "Hard Fact-Checking Module",
        "claim_evaluation_criteria": "Each sentence is treated as a potential claim, then evaluated according to:",
        "criteria_list": "- presence of dates, numbers, proper nouns,\n- presence of clear attribution,\n- degree of absolutism,\n- sensational charge,\n- probable quality of mentioned sources,\n- narrative red flags.",
        "practical_hard_fact_formula": "Practical Hard Fact Score Formula",
        "qs": "QS : quality of sources",
        "vc": "VC : average verifiability of claims",
        "rc": "RC : average risk of claims",
        "f": "F : number of red flags",
        "disclaimer": "This app does not replace a real journalist, a real researcher, or a reality clerk. But it already removes some masks from the parading text.",
        "presence_of_source_markers": "Presence of source or data markers",
        "verifiability_clues": "Verifiability clues identified: links, numbers, dates or percentages",
        "text_contains_nuances": "The text contains nuances, limitations or counterpoints",
        "text_evokes_robust_sources": "The text evokes potentially robust or institutional sources",
        "some_claims_verifiable": "Some claims are well-anchored enough to be properly verified",
        "overly_assertive_language": "Overly assertive or absolutist language",
        "notable_emotional_sensational_charge": "Notable emotional or sensational charge",
        "almost_total_absence_of_verifiable_elements": "Almost total absence of verifiable elements",
        "text_too_short": "Text too short to seriously support a strong claim",
        "multiple_claims_very_fragile": "Multiple central claims are very fragile given the present clues",
        "to_verify": "To verify",
        "rather_verifiable": "Rather verifiable",
        "very_fragile": "Very fragile",
    },
    "Español": {
        "title": "🧠 Laboratorio de Mecroyancia — Analizador de credibilidad",
        "analyze": "🔍 Analizar artículo",
        "topic": "Tema a analizar",
        "analyze_topic": "📰 Analizar 10 artículos sobre este tema",
        "url": "Analizar artículo desde URL",
        "load_url": "🌐 Cargar artículo desde URL",
        "paste": "Pegue aquí un artículo o texto",
        "verdict": "Veredicto",
        "summary": "Resumen del análisis",
        "tagline": "Tu fórmula como brújula, un control más estricto como guardia fronterizo.",
        "settings": "Configuración",
        "load_example": "Cargar ejemplo",
        "show_method": "Mostrar método",
        "hard_fact_score_scale": "Escala de Puntuación de Hechos Duros",
        "scale_0_5": "0–5 : muy frágil",
        "scale_6_9": "6–9 : dudoso",
        "scale_10_14": "10–14 : plausible pero necesita verificación cruzada",
        "scale_15_20": "15–20 : estructuralmente robusto",
        "analyze_multiple_articles_by_topic": "Analizar múltiples artículos por tema",
        "searching_analyzing_articles": "Buscando y analizando artículos...",
        "articles_analyzed": "artículos analizados.",
        "analyzed_articles": "Artículos Analizados",
        "avg_hard_fact": "Promedio Hecho Duro",
        "avg_classic_score": "Promedio Puntuación Clásica",
        "topic_doxa_index": "Índice de Doxa del Tema",
        "high": "Alto",
        "medium": "Medio",
        "low": "Bajo",
        "credibility_score_dispersion": "Dispersión de Puntuación de Credibilidad",
        "article_label": "Artículo",
        "analyzed_articles_details": "Detalles de los artículos analizados",
        "no_exploitable_articles_found": "No se encontraron artículos explotables para este tema.",
        "enter_keyword_first": "Ingrese primero una palabra clave o tema.",
        "article_loaded_from_url": "Artículo cargado desde la URL.",
        "unable_to_retrieve_text": "No se pudo recuperar el texto de esta URL.",
        "paste_url_first": "Pegue primero una URL.",
        "classic_score": "Puntuación Clásica",
        "improved_score": "Puntuación Mejorada",
        "hard_fact_score": "Puntuación de Hechos Duros",
        "help_classic_score": "M = (G + N) − D",
        "help_improved_score": "Adición de V y penalización R",
        "help_hard_fact_score": "Control más estricto de afirmaciones y fuentes",
        "credibility_gauge": "Medidor de Credibilidad",
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
        "few_strong_signals": "Pocas señales fuertes identificadas.",
        "weaknesses_detected": "Debilidades detectadas",
        "no_major_weakness": "No se identificaron debilidades importantes por heurística.",
        "hard_fact_checking_by_claim": "Verificación de hechos duros por afirmación",
        "claim": "Afirmación",
        "status": "Estado",
        "verifiability": "Verificabilidad",
        "risk": "Riesgo",
        "number": "Número",
        "date": "Fecha",
        "named_entity": "Entidad Nombrada",
        "attributed_source": "Fuente Atribuida",
        "paste_longer_text": "Pegue un texto un poco más largo para obtener un mapeo fino de las afirmaciones.",
        "paste_text_or_load_url": "Pegue un texto o cargue una URL, luego haga clic en « 🔍 Analizar artículo ».",
        "method": "Método",
        "original_formula": "Fórmula Original",
        "articulated_knowledge_density": "G : densidad de conocimiento articulado — fuentes, cifras, nombres, referencias, rastros verificables.",
        "integration": "N : integración — contexto, matices, reservas, coherencia argumentativa.",
        "assertive_rigidity": "D : rigidez asertiva — certezas no respaldadas, exuberancia retórica, inflación doxástica.",
        "improved_variant": "Variante Mejorada",
        "addition_of_v_and_r": "Adición de V para la verificabilidad y R como penalización retórica.",
        "hard_fact_checking_module": "Módulo de Verificación de Hechos Duros",
        "claim_evaluation_criteria": "Cada oración se trata como una afirmación potencial, luego se evalúa según:",
        "criteria_list": "- presencia de fechas, números, nombres propios,\n- presencia de atribución clara,\n- grado de absolutismo,\n- carga sensacionalista,\n- calidad probable de las fuentes mencionadas,\n- señales de alerta narrativas.",
        "practical_hard_fact_formula": "Fórmula Práctica de Puntuación de Hechos Duros",
        "qs": "QS : calidad de las fuentes",
        "vc": "VC : verificabilidad promedio de las afirmaciones",
        "rc": "RC : riesgo promedio de las afirmaciones",
        "f": "F : número de banderas rojas",
        "disclaimer": "Esta aplicación no reemplaza a un periodista real, un investigador real o un secretario de la realidad. Pero ya quita algunas máscaras al texto que desfila.",
        "presence_of_source_markers": "Presencia de marcadores de fuente o datos",
        "verifiability_clues": "Pistas de verificabilidad identificadas: enlaces, números, fechas o porcentajes",
        "text_contains_nuances": "El texto contiene matices, limitaciones o contrapuntos",
        "text_evokes_robust_sources": "El texto evoca fuentes potencialmente robustas o institucionales",
        "some_claims_verifiable": "Algunas afirmaciones están lo suficientemente bien ancladas para ser verificadas correctamente",
        "overly_assertive_language": "Lenguaje excesivamente asertivo o absolutista",
        "notable_emotional_sensational_charge": "Notable carga emocional o sensacionalista",
        "almost_total_absence_of_verifiable_elements": "Ausencia casi total de elementos verificables",
        "text_too_short": "Texto demasiado corto para respaldar seriamente una afirmación fuerte",
        "multiple_claims_very_fragile": "Múltiples afirmaciones centrales son muy frágiles dadas las pistas presentes",
        "to_verify": "A verificar",
        "rather_verifiable": "Más bien verificable",
        "very_fragile": "Muy frágil",
    },
    "Filipino": {
        "title": "🧠 Mecroyance Lab — Pagsusuri ng Kredibilidad",
        "analyze": "🔍 Suriin ang artikulo",
        "topic": "Paksa na susuriin",
        "analyze_topic": "📰 Suriin ang 10 artikulo tungkol sa paksang ito",
        "url": "Suriin ang artikulo mula sa URL",
        "load_url": "🌐 Kunin ang artikulo mula sa URL",
        "paste": "Ilagay dito ang artikulo o teksto",
        "verdict": "Hatol",
        "summary": "Buod ng pagsusuri",
        "tagline": "Ang iyong pormula bilang kompas, mas mahigpit na kontrol bilang bantay-hangganan.",
        "settings": "Mga Setting",
        "load_example": "I-load ang halimbawa",
        "show_method": "Ipakita ang pamamaraan",
        "hard_fact_score_scale": "Hard Fact Score Scale",
        "scale_0_5": "0–5 : napakahina",
        "scale_6_9": "6–9 : kaduda-duda",
        "scale_10_14": "10–14 : kapani-paniwala ngunit kailangan ng cross-referencing",
        "scale_15_20": "15–20 : matatag sa istruktura",
        "analyze_multiple_articles_by_topic": "Suriin ang maraming artikulo ayon sa paksa",
        "searching_analyzing_articles": "Naghahanap at nagsusuri ng mga artikulo...",
        "articles_analyzed": "mga artikulo na nasuri.",
        "analyzed_articles": "Mga Nasuring Artikulo",
        "avg_hard_fact": "Avg Hard Fact",
        "avg_classic_score": "Avg Classic Score",
        "topic_doxa_index": "Indeks ng Doxa ng Paksa",
        "high": "Mataas",
        "medium": "Katamtaman",
        "low": "Mababa",
        "credibility_score_dispersion": "Pagkalat ng Puntos ng Kredibilidad",
        "article_label": "Artikulo",
        "analyzed_articles_details": "Mga Detalye ng Nasuring Artikulo",
        "no_exploitable_articles_found": "Walang nakitang magagamit na artikulo para sa paksang ito.",
        "enter_keyword_first": "Maglagay muna ng keyword o paksa.",
        "article_loaded_from_url": "Na-load ang artikulo mula sa URL.",
        "unable_to_retrieve_text": "Hindi makuha ang teksto mula sa URL na ito.",
        "paste_url_first": "Mag-paste muna ng URL.",
        "classic_score": "Klasikong Puntos",
        "improved_score": "Pinahusay na Puntos",
        "hard_fact_score": "Hard Fact Score",
        "help_classic_score": "M = (G + N) − D",
        "help_improved_score": "Pagdaragdag ng V at parusa sa R",
        "help_hard_fact_score": "Mas mahigpit na kontrol sa mga pahayag at pinagmulan",
        "credibility_gauge": "Sukat ng Kredibilidad",
        "fragile": "Mahina",
        "fragile_message": "Ang teksto ay nagpapakita ng malakas na istruktural o paktwal na kahinaan.",
        "doubtful": "Kaduda-duda",
        "doubtful_message": "Ang teksto ay naglalaman ng ilang kapani-paniwalang elemento, ngunit nananatiling napaka-hindi tiyak.",
        "plausible": "Kapani-paniwala",
        "plausible_message": "Ang teksto ay lumilitaw na pangkalahatang kapani-paniwala, ngunit nangangailangan pa rin ng pagpapatunay.",
        "robust": "Matatag",
        "robust_message": "Ang teksto ay nagtatanghal ng isang medyo solidong istruktural at paktwal na batayan.",
        "score": "Puntos",
        "strengths_detected": "Mga lakas na natukoy",
        "few_strong_signals": "Ilang malakas na signal ang natukoy.",
        "weaknesses_detected": "Mga kahinaan na natukoy",
        "no_major_weakness": "Walang pangunahing kahinaan na natukoy ng heuristika.",
        "hard_fact_checking_by_claim": "Hard fact-checking sa bawat pahayag",
        "claim": "Pahayag",
        "status": "Katayuan",
        "verifiability": "Pagpapatunay",
        "risk": "Panganib",
        "number": "Numero",
        "date": "Petsa",
        "named_entity": "Pinangalanang Entidad",
        "attributed_source": "Iniugnay na Pinagmulan",
        "paste_longer_text": "Mag-paste ng bahagyang mas mahabang teksto upang makakuha ng detalyadong pagmamapa ng mga pahayag.",
        "paste_text_or_load_url": "Mag-paste ng teksto o mag-load ng URL, pagkatapos ay i-click ang « 🔍 Suriin ang artikulo ».",
        "method": "Paraan",
        "original_formula": "Orihinal na Pormula",
        "articulated_knowledge_density": "G : density ng articulated knowledge — mga pinagmulan, numero, pangalan, sanggunian, nabe-verify na bakas.",
        "integration": "N : integrasyon — konteksto, nuances, reserbasyon, lohikal na pagkakaugnay.",
        "assertive_rigidity": "D : assertive rigidity — hindi suportadong katiyakan, retorikal na pagmamalabis, doxic inflation.",
        "improved_variant": "Pinahusay na Variant",
        "addition_of_v_and_r": "Pagdaragdag ng V para sa pagpapatunay at R bilang retorikal na parusa.",
        "hard_fact_checking_module": "Hard Fact-Checking Module",
        "claim_evaluation_criteria": "Ang bawat pangungusap ay itinuturing na isang potensyal na pahayag, pagkatapos ay sinusuri ayon sa:",
        "criteria_list": "- pagkakaroon ng mga petsa, numero, wastong pangalan,\n- pagkakaroon ng malinaw na atribusyon,\n- antas ng absolutismo,\n- sensational na singil,\n- posibleng kalidad ng mga nabanggit na pinagmulan,\n- narrative red flags.",
        "practical_hard_fact_formula": "Praktikal na Pormula ng Hard Fact Score",
        "qs": "QS : kalidad ng mga pinagmulan",
        "vc": "VC : average na pagpapatunay ng mga pahayag",
        "rc": "RC : average na panganib ng mga pahayag",
        "f": "F : bilang ng mga red flag",
        "disclaimer": "Ang app na ito ay hindi pumapalit sa isang tunay na mamamahayag, isang tunay na mananaliksik, o isang klerk ng katotohanan. Ngunit tinatanggal na nito ang ilang maskara mula sa nagpaparadang teksto.",
        "presence_of_source_markers": "Pagkakaroon ng mga marker ng pinagmulan o data",
        "verifiability_clues": "Mga pahiwatig ng pagpapatunay na natukoy: mga link, numero, petsa o porsyento",
        "text_contains_nuances": "Ang teksto ay naglalaman ng mga nuances, limitasyon o kontrapunto",
        "text_evokes_robust_sources": "Ang teksto ay nagpapahiwatig ng posibleng matatag o institusyonal na pinagmulan",
        "some_claims_verifiable": "Ang ilang mga pahayag ay sapat na nakabaon upang maayos na mapatunayan",
        "overly_assertive_language": "Labis na mapilit o absolutistang wika",
        "notable_emotional_sensational_charge": "Kapansin-pansing emosyonal o sensational na singil",
        "almost_total_absence_of_verifiable_elements": "Halos kumpletong kawalan ng nabe-verify na elemento",
        "text_too_short": "Masyadong maikli ang teksto upang seryosong suportahan ang isang malakas na pahayag",
        "multiple_claims_very_fragile": "Maraming sentral na pahayag ang napakahina dahil sa kasalukuyang mga pahiwatig",
        "to_verify": "Upang i-verify",
        "rather_verifiable": "Sa halip nabe-verify",
        "very_fragile": "Napakabihira",
    },
}

lang = st.sidebar.selectbox(
    "Language / Langue / Idioma",
    ["Français", "English", "Español", "Filipino"]
)

# bannière de l'application
st.image("banner.png", use_container_width=True)

SAMPLE_ARTICLE = """Titre : Une découverte historique va bouleverser la science pour toujours

Des chercheurs affirment avoir trouvé une substance naturelle capable de guérir presque toutes les maladies. Selon plusieurs experts, cette avancée serait cachée depuis des années par certaines industries. Tout le monde devrait s'inquiéter. Aucune source officielle n'a encore publié de données complètes, mais les témoignages sont troublants et les résultats sembleraient indiscutables.
"""

# -----------------------------
# Utilitaires
# -----------------------------
def clamp(value: float, min_value: float = 0.0, max_value: float = 20.0) -> float:
    return max(min_value, min(max_value, value))


def normalize(
    value: float,
    in_min: float,
    in_max: float,
    out_min: float = 0.0,
    out_max: float = 20.0,
) -> float:
    if in_max == in_min:
        return out_min
    ratio = (value - in_min) / (in_max - in_min)
    return out_min + ratio * (out_max - out_min)


def count_matches(text: str, pattern: str, flags: int = 0) -> int:
    return len(re.findall(pattern, text, flags))


def split_into_claims(text: str) -> List[str]:
    if not text.strip():
        return []
    rough = re.split(r"(?<=[.!?])\s+", text.strip())
    claims = []
    for sentence in rough:
        sentence = sentence.strip()
        if len(sentence.split()) >= 8:
            claims.append(sentence)
    return claims[:20]


def extract_article_from_url(url: str) -> str:
    try:
        article = Article(url)
        article.download()
        article.parse()

        text = article.text.strip()

        if article.title:
            return "Titre : " + article.title + "\n\n" + text
        return text

    except Exception:
        return ""


def search_articles_by_keyword(keyword: str, max_results: int = 10):
    """
    Moteur de recherche amélioré :
    - Liste de domaines de confiance élargie (25+ sources)
    - Requête plus flexible sans guillemets stricts autour du mot-clé
    - Volume de résultats bruts multiplié par 5 pour augmenter les chances de trouver des domaines de confiance
    - Utilise le nouveau package ddgs (anciennement duckduckgo_search)
    """
    results = []

    # Liste élargie de domaines de confiance (médias, institutions, presse internationale)
    trusted_domains = [
        # Agences de presse internationales
        "reuters.com",
        "apnews.com",
        "afp.com",
        # Médias anglophones
        "bbc.com",
        "theguardian.com",
        "nytimes.com",
        "washingtonpost.com",
        "wsj.com",
        "bloomberg.com",
        "ft.com",
        "cnn.com",
        "npr.org",
        "politico.com",
        "politico.eu",
        # Médias francophones
        "lemonde.fr",
        "france24.com",
        "francetvinfo.fr",
        "liberation.fr",
        "lefigaro.fr",
        "lesechos.fr",
        "mediapart.fr",
        "lepoint.fr",
        "lexpress.fr",
        "rfi.fr",
        # Médias hispanophones
        "elpais.com",
        # Médias germanophones et internationaux
        "spiegel.de",
        "dw.com",
        "aljazeera.com",
        # Sources scientifiques et institutionnelles
        "nature.com",
        "science.org",
        "thelancet.com",
        "nejm.org",
        "who.int",
        "un.org",
        "europa.eu",
    ]

    try:
        # Requête plus flexible : sans guillemets stricts, avec des termes booléens
        # pour cibler des publications journalistiques ou scientifiques
        query = f"{keyword} (actualités OR news OR article OR analyse OR reportage OR étude)"

        with DDGS() as ddgs:
            # On demande 5x plus de résultats bruts pour maximiser les chances
            # de trouver des articles provenant des domaines de confiance
            search_results = ddgs.text(query, max_results=max_results * 5)

            for r in search_results:
                url = r.get("href", "")
                if not url:
                    continue

                # Vérification souple : le domaine est-il dans notre liste ?
                if not any(domain in url.lower() for domain in trusted_domains):
                    continue

                results.append(
                    {
                        "title": r.get("title", ""),
                        "url": url,
                        "source": r.get("body", ""),
                    }
                )

                if len(results) >= max_results:
                    break

    except Exception as e:
        st.warning(f"Erreur lors de la recherche : {e}")
        return []

    return results


def analyze_multiple_articles(keyword: str, max_results: int = 10):
    found_articles = search_articles_by_keyword(keyword, max_results=max_results)
    analyzed = []

    for item in found_articles:
        url = item.get("url", "").strip()
        if not url:
            continue

        text = extract_article_from_url(url)
        if not text:
            continue

        result = analyze_article(text)

        analyzed.append(
            {
                "Titre": item.get("title", "Sans titre"),
                "URL": url,
                "Score classique": result["M"],
                "Score amélioré": result["improved"],
                "Hard Fact Score": result["hard_fact_score"],
                "Verdict": result["verdict"],
            }
        )

    return analyzed


# -----------------------------
# Moteur d'analyse
# -----------------------------
def score_source_quality(lower: str) -> float:
    score = 10.0

    strong_sources = [
        r"reuters", r"associated press", r"ap news", r"afp", r"bbc", r"le monde",
        r"nature", r"science", r"the lancet", r"nejm", r"who", r"oms", r"unicef",
        r"eurostat", r"insee", r"onu", r"united nations", r"gouvernement", r"minist[eè]re",
        r"universit[eé]", r"institut", r"cour des comptes", r"european commission",
    ]
    weak_sources = [
        r"blog", r"rumeur", r"anonyme", r"telegram", r"whatsapp", r"forum",
        r"tiktok", r"youtube", r"influenceur", r"source inconnue",
    ]
    vague_authority = [
        r"selon des experts", r"plusieurs experts", r"des experts affirment",
        r"certains disent", r"on raconte", r"beaucoup pensent",
    ]

    if any(re.search(p, lower) for p in strong_sources):
        score += 6
    if any(re.search(p, lower) for p in weak_sources):
        score -= 6
    if any(re.search(p, lower) for p in vague_authority):
        score -= 4

    return round(clamp(score), 1)


def extract_red_flags(lower: str) -> List[str]:
    flags = []
    patterns = {
        "Narration de dissimulation ou de complot": r"secret|cach[ée] depuis des ann[ée]es|on vous ment|v[ée]rit[ée] cach[ée]e|complot",
        "Promesse extraordinaire ou disproportionnée": r"gu[ée]rir presque toutes les maladies|miracle|r[ée]volutionnaire|d[ée]finitif",
        "Pression injonctive ou émotionnelle": r"tout le monde devrait|personne ne vous dit|il faut absolument",
        "Affirmation forte sans base documentaire robuste": r"aucune source officielle|sans preuve|sans donn[ée]es compl[èe]tes",
        "Attribution floue des autorités citées": r"selon plusieurs experts|des chercheurs affirment",
    }
    for label, pattern in patterns.items():
        if re.search(pattern, lower):
            flags.append(label)
    return flags


@dataclass
class ClaimAssessment:
    text: str
    verifiability: float
    risk: float
    status: str
    has_number: bool
    has_date: bool
    has_named_entity: bool
    has_source_cue: bool


def assess_claim(sentence: str) -> ClaimAssessment:
    has_number = bool(re.search(r"\b\d+(?:[.,]\d+)?\b", sentence))
    has_date = bool(re.search(r"\b(?:19|20)\d{2}\b", sentence))
    has_named_entity = bool(
        re.search(r"\b[A-ZÉÈÀÂÊÎÔÛÄËÏÖÜ][a-zàâçéèêëîïôûùüÿñæœ'\-]{2,}\b", sentence)
    )
    has_source_cue = bool(
        re.search(r"selon|d'après|rapport|étude|données|publication|université|institut|journal|revue", sentence, re.I)
    )
    hedged = bool(re.search(r"semble|pourrait|suggère|à confirmer|probable", sentence, re.I))
    absolute = bool(re.search(r"toujours|jamais|indiscutable|certain|absolument|sans aucun doute|prouve", sentence, re.I))
    sensational = bool(re.search(r"choc|explosif|scandale|révélations|bouleverser", sentence, re.I))

    verifiability = 4.0
    if has_number:
        verifiability += 4
    if has_date:
        verifiability += 3
    if has_named_entity:
        verifiability += 3
    if has_source_cue:
        verifiability += 4
    verifiability = round(clamp(verifiability), 1)

    risk = 3.0
    if absolute:
        risk += 6
    if sensational:
        risk += 4
    if not has_source_cue:
        risk += 3
    if not has_named_entity and not has_number:
        risk += 2
    if hedged:
        risk -= 1.5
    risk = round(clamp(risk), 1)

    status = translations[lang]["to_verify"]
    if verifiability >= 12 and risk <= 7:
        status = translations[lang]["rather_verifiable"]
    elif risk >= 12:
        status = translations[lang]["very_fragile"]

    return ClaimAssessment(
        text=sentence,
        verifiability=verifiability,
        risk=risk,
        status=status,
        has_number=has_number,
        has_date=has_date,
        has_named_entity=has_named_entity,
        has_source_cue=has_source_cue,
    )


def analyze_article(text: str) -> Dict:
    clean = text.strip()
    words = re.findall(r"\S+", clean)
    sentences = [s.strip() for s in re.split(r"[.!?]+", clean) if s.strip()]
    lower = clean.lower()

    source_markers = count_matches(
        lower,
        r"selon|d'après|source|sources|étude|rapport|données|statistiques|recherche|journal|revue|université|institut|publication|enquête|archive|preuve|preuves",
    )
    citation_like = count_matches(
        clean,
        r"https?://|www\.|\[[0-9]+\]|\([0-9]{4}\)|%|\d+\s?(millions|milliards|%|ans|jours|mois)",
        re.I,
    )
    named_entities = count_matches(
        clean,
        r"\b[A-ZÉÈÀÂÊÎÔÛÄËÏÖÜ][a-zàâçéèêëîïôûùüÿñæœ'\-]{2,}\b",
    )
    hedges = count_matches(
        lower,
        r"semble|semblerait|probable|probablement|possible|possiblement|suggère|suggèrent|pourrait|pourraient|hypothèse|incertain|selon les premiers éléments|à confirmer",
    )
    certainty = count_matches(
        lower,
        r"toujours|jamais|indiscutable|indiscutables|prouve|preuve définitive|certain|certainement|absolument|sans aucun doute|tout le monde|personne ne|forcément|à coup sûr|vérité cachée|on vous ment|bouleverser|explosif|choc|scandale|incroyable",
    )
    emotional = count_matches(
        lower,
        r"scandale|honte|peur|catastrophe|mensonge|censure|complot|terrifiant|choquant|alarmant|panique|bouleverser|explosif|révélations",
    )
    nuance_markers = count_matches(
        lower,
        r"cependant|toutefois|néanmoins|en revanche|mais|d'un côté|de l'autre|limite|limites|réserve|réserves|biais|méthodologie|contexte|contre-argument|incertitude",
    )
    article_length = len(words)
    avg_sentence_length = (len(words) / len(sentences)) if sentences else 0

    G = 3.0
    G += normalize(source_markers, 0, 12, 0, 7)
    G += normalize(citation_like, 0, 10, 0, 5)
    G += normalize(named_entities, 0, 18, 0, 3)
    G += 1.5 if article_length > 180 else 0.75 if article_length > 90 else 0
    G = round(clamp(G), 1)

    N = 4.0
    N += normalize(nuance_markers, 0, 10, 0, 7)
    N += min(3, hedges * 0.5) if hedges > 0 else 0
    N += 1.5 if 10 <= avg_sentence_length <= 28 else 0.5
    N += 1 if len(sentences) >= 3 else 0
    N = round(clamp(N), 1)

    D = 2.0
    D += normalize(certainty, 0, 10, 0, 9)
    D += normalize(emotional, 0, 8, 0, 5)
    D += 2 if article_length < 80 else 0
    if source_markers == 0 and citation_like == 0:
        D += 2.5
    D = round(clamp(D), 1)

    M = round((G + N) - D, 1)

    V = round(clamp(normalize(source_markers + citation_like, 0, 18, 0, 20)), 1)
    R = round(clamp(normalize(certainty + emotional, 0, 16, 0, 20)), 1)
    improved_raw = ((G + N + V) / 3) - (D * 0.55) - (R * 0.25)
    improved = round(clamp(improved_raw, -10, 20), 1)

    claims = [assess_claim(c) for c in split_into_claims(clean)]
    source_quality = score_source_quality(lower)
    red_flags = extract_red_flags(lower)

    avg_claim_risk = round(sum(c.risk for c in claims) / len(claims), 1) if claims else 0.0
    avg_claim_verifiability = round(sum(c.verifiability for c in claims) / len(claims), 1) if claims else 0.0

    hard_fact_score_raw = (
        (G * 0.18)
        + (N * 0.12)
        + (V * 0.20)
        + (source_quality * 0.22)
        + (avg_claim_verifiability * 0.18)
        - (D * 0.16)
        - (R * 0.12)
        - (avg_claim_risk * 0.18)
        - (len(red_flags) * 0.9)
    )
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

            # tri du plus crédible au moins crédible
            df_multi = df_multi.sort_values("Hard Fact Score", ascending=False)

            st.success(f"{len(df_multi)} {translations[lang]['articles_analyzed']}")

            moyenne_hf = round(df_multi["Hard Fact Score"].mean(), 1)
            moyenne_classique = round(df_multi["Score classique"].mean(), 1)

            c1, c2, c3 = st.columns(3)
            c1.metric(translations[lang]["analyzed_articles"], len(df_multi))
            c2.metric(translations[lang]["avg_hard_fact"], moyenne_hf)
            c3.metric(translations[lang]["avg_classic_score"], moyenne_classique)

            ecart_type_hf = round(df_multi["Hard Fact Score"].std(), 2)

            if ecart_type_hf < 1.5:
                indice_doxa = "Élevé"
            elif ecart_type_hf < 3:
                indice_doxa = "Moyen"
            else:
                indice_doxa = "Faible"

            st.metric(translations[lang]["topic_doxa_index"], indice_doxa)

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
    col3.metric(
        translations[lang]["hard_fact_score"],
        result["hard_fact_score"],
        help=translations[lang]["help_hard_fact_score"],
    )

    score = result["hard_fact_score"]

    if score <= 6:
        couleur = "🔴"
        etiquette = translations[lang]["fragile"]
        message = translations[lang]["fragile_message"]
    elif score <= 11:
        couleur = "🟠"
        etiquette = translations[lang]["doubtful"]
        message = translations[lang]["doubtful_message"]
    elif score <= 15:
        couleur = "🟡"
        etiquette = translations[lang]["plausible"]
        message = translations[lang]["plausible_message"]
    else:
        couleur = "🟢"
        etiquette = translations[lang]["robust"]
        message = translations[lang]["robust_message"]

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
            for item in result["strengths"]:
                st.success(item)
        else:
            st.info(translations[lang]["few_strong_signals"])

    with st.expander(translations[lang]["weaknesses_detected"], expanded=True):
        if result["weaknesses"]:
            for item in result["weaknesses"]:
                st.error(item)
        else:
            st.success(translations[lang]["no_major_weakness"])

    st.subheader(translations[lang]["hard_fact_checking_by_claim"])
    claims_df = pd.DataFrame(
        [
            {
                translations[lang]["claim"]: c.text,
                translations[lang]["status"]: c.status,
                f"{translations[lang]['verifiability']} /20": c.verifiability,
                f"{translations[lang]['risk']} /20": c.risk,
                translations[lang]["number"]: translations[lang]["yes"] if c.has_number else translations[lang]["no"],
                translations[lang]["date"]: translations[lang]["yes"] if c.has_date else translations[lang]["no"],
                translations[lang]["named_entity"]: translations[lang]["yes"] if c.has_named_entity else translations[lang]["no"],
                translations[lang]["attributed_source"]: translations[lang]["yes"] if c.has_source_cue else translations[lang]["no"],
            }
            for c in result["claims"]
        ]
    )

    if not claims_df.empty:
        st.dataframe(claims_df, use_container_width=True, hide_index=True)
    else:
        st.info(translations[lang]["paste_longer_text"])
else:
    st.info(translations[lang]["paste_text_or_load_url"])

if show_method:
    st.subheader(translations[lang]["method"])
    st.markdown(
        f"""
### {translations[lang]["original_formula"]}
`M = (G + N) − D`

- {translations[lang]["articulated_knowledge_density"]}
- {translations[lang]["integration"]}
- {translations[lang]["assertive_rigidity"]}

### {translations[lang]["improved_variant"]}
{translations[lang]["addition_of_v_and_r"]}

### {translations[lang]["hard_fact_checking_module"]}
{translations[lang]["claim_evaluation_criteria"]}
{translations[lang]["criteria_list"]}

### {translations[lang]["practical_hard_fact_formula"]}
`HF = 0.18G + 0.12N + 0.20V + 0.22QS + 0.18VC − 0.16D − 0.12R − 0.18RC − 0.9F + 8`

- **QS** : {translations[lang]["qs"]}
- **VC** : {translations[lang]["vc"]}
- **RC** : {translations[lang]["rc"]}
- **F** : {translations[lang]["f"]}

{translations[lang]["disclaimer"]}
        """
    )
