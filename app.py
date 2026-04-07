from duckduckgo_search import DDGS
from newspaper import Article
import re
from dataclasses import dataclass
from typing import List, Dict

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Mécroyance Lab — Fact-checking dur",
    page_icon="🧠",
    layout="wide",
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
    results = []
    try:
        with DDGS() as ddgs:
            search_results = ddgs.text(keyword, max_results=max_results)
            for r in search_results:
                results.append(
                    {
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "source": r.get("body", ""),
                    }
                )
    except Exception:
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

    status = "À vérifier"
    if verifiability >= 12 and risk <= 7:
        status = "Plutôt vérifiable"
    elif risk >= 12:
        status = "Très fragile"

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
        verdict = "Crédibilité basse"
    elif hard_fact_score < 10:
        verdict = "Crédibilité prudente"
    elif hard_fact_score < 15:
        verdict = "Plutôt crédible"
    else:
        verdict = "Crédibilité forte"

    strengths = []
    weaknesses = []

    if source_markers >= 2:
        strengths.append("Présence de marqueurs de sources ou de données")
    if citation_like >= 2:
        strengths.append("Indices de vérifiabilité repérés : liens, chiffres, dates ou pourcentages")
    if nuance_markers >= 2:
        strengths.append("Le texte contient des nuances, limites ou contrepoints")
    if source_quality >= 12:
        strengths.append("Le texte évoque des sources potentiellement robustes ou institutionnelles")
    if any(c.status == "Plutôt vérifiable" for c in claims):
        strengths.append("Certaines affirmations sont assez bien ancrées pour être vérifiées proprement")

    if certainty >= 3:
        weaknesses.append("Langage trop assuré ou absolutiste")
    if emotional >= 2:
        weaknesses.append("Charge émotionnelle ou sensationnaliste notable")
    if source_markers == 0 and citation_like == 0:
        weaknesses.append("Absence quasi totale d'éléments vérifiables")
    if article_length < 80:
        weaknesses.append("Texte trop court pour soutenir sérieusement une affirmation forte")
    weaknesses.extend(red_flags)
    if sum(1 for c in claims if c.status == "Très fragile") >= 2:
        weaknesses.append("Plusieurs affirmations centrales sont très fragiles au regard des indices présents")

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
st.title("🧠 Mécroyance Lab — Crédibilité d'article & fact-checking dur")
st.caption("Votre formule comme boussole, un contrôle plus sévère comme garde-frontière.")

with st.sidebar:
    st.header("Réglages")
    use_sample = st.button("Charger l'exemple")
    show_method = st.toggle("Afficher la méthode", value=True)
    st.divider()
    st.subheader("Échelle du hard fact score")
    st.markdown(
        """
- **0–5** : très fragile  
- **6–9** : douteux  
- **10–14** : plausible mais à recouper  
- **15–20** : structurellement robuste
        """
    )

if "article" not in st.session_state:
    st.session_state.article = SAMPLE_ARTICLE

if use_sample:
    st.session_state.article = SAMPLE_ARTICLE

url = st.text_input("Analyser un article par URL")

if st.button("🌐 Charger l'article depuis l'URL"):
    if url:
        texte = extract_article_from_url(url)
        if texte:
            st.session_state.article = texte
            st.success("Article chargé depuis l'URL.")
        else:
            st.error("Impossible de récupérer le texte de cette URL.")
    else:
        st.warning("Collez d'abord une URL.")

article = st.text_area(
    "Collez ici un article, un post, un communiqué ou un texte journalistique",
    value=st.session_state.article,
    height=320,
)

st.session_state.article = article

analyser = st.button("🔍 Analyser l'article", use_container_width=True, type="primary")

if analyser:
    result = analyze_article(article)

    col1, col2, col3 = st.columns(3)
    col1.metric("Score classique", result["M"], help="M = (G + N) − D")
    col2.metric("Score amélioré", result["improved"], help="Ajout de V et pénalité R")
    col3.metric(
        "Hard Fact Score",
        result["hard_fact_score"],
        help="Contrôle plus dur des affirmations et des sources",
    )

    score = result["hard_fact_score"]

    if score <= 6:
        couleur = "🔴"
        etiquette = "Fragile"
        message = "Le texte présente de fortes fragilités structurelles ou factuelles."
    elif score <= 11:
        couleur = "🟠"
        etiquette = "Douteux"
        message = "Le texte contient quelques éléments crédibles, mais reste très incertain."
    elif score <= 15:
        couleur = "🟡"
        etiquette = "Plausible"
        message = "Le texte paraît globalement plausible, mais demande encore vérification."
    else:
        couleur = "🟢"
        etiquette = "Robuste"
        message = "Le texte présente une base structurelle et factuelle plutôt solide."

    st.subheader(f"{couleur} Jauge de crédibilité : {etiquette}")
    st.progress(score / 20)
    st.caption(f"Score : {score}/20 — {message}")

    st.subheader(f"Verdict : {result['verdict']}")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("G — gnōsis", result["G"])
    m2.metric("N — nous", result["N"])
    m3.metric("D — doxa", result["D"])
    m4.metric("V — vérifiabilité", result["V"])

    m5, m6, m7, m8 = st.columns(4)
    m5.metric("Qualité des sources", result["source_quality"])
    m6.metric("Risque moyen des claims", result["avg_claim_risk"])
    m7.metric("Vérifiabilité moyenne", result["avg_claim_verifiability"])
    m8.metric("Red flags", len(result["red_flags"]))

    with st.expander("Forces détectées", expanded=True):
        if result["strengths"]:
            for item in result["strengths"]:
                st.success(item)
        else:
            st.info("Peu de signaux forts repérés.")

    with st.expander("Fragilités détectées", expanded=True):
        if result["weaknesses"]:
            for item in result["weaknesses"]:
                st.error(item)
        else:
            st.success("Aucune fragilité majeure repérée par l'heuristique.")

    st.subheader("Fact-checking dur par affirmation")
    claims_df = pd.DataFrame(
        [
            {
                "Affirmation": c.text,
                "Statut": c.status,
                "Vérifiabilité /20": c.verifiability,
                "Risque /20": c.risk,
                "Nombre": "Oui" if c.has_number else "Non",
                "Date": "Oui" if c.has_date else "Non",
                "Nom propre": "Oui" if c.has_named_entity else "Non",
                "Source attribuée": "Oui" if c.has_source_cue else "Non",
            }
            for c in result["claims"]
        ]
    )

    if not claims_df.empty:
        st.dataframe(claims_df, use_container_width=True, hide_index=True)
    else:
        st.info("Collez un texte un peu plus long pour obtenir une cartographie fine des affirmations.")
else:
    st.info("Collez un texte ou chargez une URL, puis cliquez sur « 🔍 Analyser l'article ».")

if show_method:
    st.subheader("Méthode")
    st.markdown(
        """
### Formule originelle
`M = (G + N) − D`

- **G** : densité de savoir articulé — sources, chiffres, noms, références, traces vérifiables.
- **N** : intégration — contexte, nuances, réserves, cohérence argumentative.
- **D** : rigidité assertive — certitudes non soutenues, emballement rhétorique, gonflement doxique.

### Variante améliorée
Ajout de **V** pour la vérifiabilité et de **R** comme pénalité rhétorique.

### Module de fact-checking dur
Chaque phrase est traitée comme une affirmation potentielle, puis évaluée selon :
- présence de dates, nombres, noms propres,
- présence d'une attribution claire,
- degré d'absolutisme,
- charge sensationnaliste,
- qualité probable des sources mentionnées,
- signaux rouges narratifs.

### Formule pratique du hard fact score
`HF = 0.18G + 0.12N + 0.20V + 0.22QS + 0.18VC − 0.16D − 0.12R − 0.18RC − 0.9F + 8`

- **QS** : qualité des sources
- **VC** : vérifiabilité moyenne des affirmations
- **RC** : risque moyen des affirmations
- **F** : nombre de red flags

Cette app ne remplace pas un vrai journaliste, un vrai chercheur, ni un greffier de la réalité. Mais elle retire déjà quelques masques au texte qui parade.
        """
    )
