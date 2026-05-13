<!-- Profile README — github.com/YACINBK -->

<p align="center">
  <img src="./readme-assets/system-pulse-mark.svg" alt="System pulse" />
</p>

<p align="center">
  <img src="./readme-assets/hero-runtime-panel.svg" width="100%" alt="Hero panel — Yacin Ben Kacem" />
</p>

<p align="center">
  <a href="https://yacinbenkacem.me/">
    <img src="https://img.shields.io/badge/Portfolio-Live-050705?style=for-the-badge&logo=firefoxbrowser&logoColor=8FFF52&labelColor=11160F" alt="Portfolio" />
  </a>
  <a href="https://github.com/YACINBK">
    <img src="https://img.shields.io/badge/GitHub-YACINBK-050705?style=for-the-badge&logo=github&logoColor=FFFFFF&labelColor=11160F" alt="GitHub" />
  </a>
  <a href="https://www.linkedin.com/in/yacin-ben-kacem/">
    <img src="https://img.shields.io/badge/LinkedIn-Yacin%20Ben%20Kacem-050705?style=for-the-badge&logo=linkedin&logoColor=0A66C2&labelColor=11160F" alt="LinkedIn" />
  </a>
  <a href="mailto:yacinbenkacem19@gmail.com">
    <img src="https://img.shields.io/badge/Email-Contact-050705?style=for-the-badge&logo=gmail&logoColor=EA4335&labelColor=11160F" alt="Email" />
  </a>
</p>

<p align="center">
  <img src="https://komarev.com/ghpvc/?username=YACINBK&style=for-the-badge&color=8FFF52&label=PROFILE+VIEWS" alt="Profile views" />
</p>

---

<p align="center">
  <img src="./readme-assets/about-control-bar.svg" width="100%" alt="About" />
</p>

```bash
> whoami
Yacin Ben Kacem

> studying
Applied Computer Science Engineering @ ENISo — National School of Engineering of Sousse

> based_in
Monastir, Tunisia

> core_focus
Agentic systems, secure backend architecture, resilient workflows, shipping under constraints
```

I am **Yacin Ben Kacem**, an Applied Computer Science Engineering student at **ENISo**. I architect secure backend systems and agentic AI workflows that survive real-world failure.

What matters most to me is that systems hold up when things go wrong: missing API key, no GPU, 400 concurrent users, unavailable external service. I treat those as **design inputs**, not edge cases.

- **Agentic Systems** — Multi-step AI workflows with state checks, tool routing, retries, and explicit failure states.
- **Secure Backend** — Gateways, identity, JWT/OIDC validation, access boundaries, and clean API contracts.
- **Resilient Workflows** — Caching, preprocessing, explicit fallbacks, reproducible outputs, and resource-aware execution.
- Treating hardware limits, performance constraints, and integration reality as part of the spec.

---

<p align="center">
  <img src="./readme-assets/projects-control-bar.svg" width="100%" alt="Featured Projects" />
</p>

### 🔷 [UX Insight Platform](https://github.com/YACINBK/ux-insight-platform)

> `Spring Boot` `FastAPI` `Angular` `ChromaDB` `OCR` `PostgreSQL` `Docker Compose`

A fully containerized UX analysis platform built around a clear service separation: Spring Boot acts as the API gateway, routing to two dedicated FastAPI services — one for LLM-powered heuristic and behavioral analysis backed by ChromaDB RAG with query-level caching, one for Vision/OCR. The Angular frontend consumes reports and dashboard stats from the gateway only. Provider-agnostic by design. Everything boots with `docker-compose up`.

---

### 🔷 [QuickFlow](https://github.com/TaherBenAfia/quickflow) — *Team of 4 · Security & Data Orchestration*

> `Spring Boot` `Spring AI` `Spring Security` `Ollama` `React` `MongoDB` `Whisper`

An AI productivity suite for meeting minutes and email drafting. I owned two layers:
**Authentication architecture** — email/password with bcrypt, OAuth2 via Google and Microsoft with encrypted token storage in MongoDB, SMTP fallback for non-OAuth users, JWT session management, TOTP infrastructure for MFA.
**Data orchestration** — applied caching to the Ollama inference layer to eliminate redundant model calls under concurrent load, aligned retrieval with system design rules.

---

### 🔷 [Smart City Sousse 2030 V2](https://github.com/YACINBK/smart-city-sousse-2030-V2)

> `Python` `PostgreSQL` `Streamlit` `FSM` `NL→SQL Compiler` `OpenAI-compatible`

An urban operations platform built around a French NL→SQL compiler, Finite-state machines, AI reporting, and a Streamlit operational dashboard. Dockerized, TimescaleDB-compatible schema, automated test suites. Offline capability is a first-class requirement.

---

### 🔷 [Image Vectorization Pipeline](https://github.com/YACINBK/image-vectorization)

> `Python` · local pipeline

Raster-to-vector conversion replicating the Illustrator/Photoshop vectorization workflow without the software dependency. Verbose output at every processing stage, explicit fallbacks throughout. Designed to stay fully local.

---

### 🔷 [Webots UR10 Pick-and-Place + YOLOv8](https://github.com/YACINBK/webots-ur10-pick-and-place-yolo8)

> `Python` `Webots` `YOLOv8`

YOLOv8 object detection integrated with a UR10 arm simulation in Webots, controlled by an FSM-driven pick-and-place sequence.

---

<p align="center">
  <img src="./readme-assets/stack-control-bar.svg" width="100%" alt="Stack" />
</p>

<p align="center">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=py,java,c,cpp,cs,ts&theme=dark" alt="Languages" />
  </a>
</p>

<p align="center">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=spring,fastapi,flask,django,angular,react&theme=dark" alt="Frameworks" />
  </a>
</p>

<p align="center">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=postgres,mongo,docker,pytorch,tensorflow,git&theme=dark" alt="Tools & DBs" />
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Spring%20AI-050705?style=for-the-badge&logo=spring&logoColor=8FFF52&labelColor=11160F"            alt="Spring AI" />
  <img src="https://img.shields.io/badge/Keycloak-050705?style=for-the-badge&logo=keycloak&logoColor=8FFF52&labelColor=11160F"              alt="Keycloak" />
  <img src="https://img.shields.io/badge/Ollama-050705?style=for-the-badge&logo=ollama&logoColor=8FFF52&labelColor=11160F"                  alt="Ollama" />
  <img src="https://img.shields.io/badge/Playwright-050705?style=for-the-badge&logo=playwright&logoColor=8FFF52&labelColor=11160F"          alt="Playwright" />
  <img src="https://img.shields.io/badge/GitHub%20Actions-050705?style=for-the-badge&logo=githubactions&logoColor=8FFF52&labelColor=11160F" alt="GitHub Actions" />
</p>

<p align="center">
  <code>RAG</code>&nbsp;
  <code>ChromaDB</code>&nbsp;
  <code>YOLOv8</code>&nbsp;
  <code>OCR</code>&nbsp;
  <code>LLMOps</code>&nbsp;
  <code>OIDC / JWT</code>&nbsp;
  <code>LoRA / QLoRA</code>&nbsp;
  <code>Triton Server</code>&nbsp;
  <code>Agentic Systems</code>&nbsp;
  <code>Automation Pipelines</code>
</p>

---

<p align="center">
  <img src="./readme-assets/activity-control-bar.svg" width="100%" alt="Activity" />
</p>

<p align="center">
  <img
    src="https://github-readme-activity-graph.vercel.app/graph?username=YACINBK&bg_color=0B100D&color=D9FFB8&line=8FFF52&point=EEF6EF&area=true&area_color=132015&hide_border=true&title_color=8FFF52&custom_title=Contribution%20Flow"
    alt="Contribution graph"
  />
</p>

<p align="center">
  <img
    src="https://github-readme-stats.vercel.app/api?username=YACINBK&show_icons=true&bg_color=0B100D&title_color=8FFF52&text_color=EEF6EF&icon_color=8FFF52&border_color=253128&rank_icon=github"
    height="165"
    alt="GitHub stats"
  />
  <img
    src="https://github-readme-stats.vercel.app/api/top-langs/?username=YACINBK&layout=compact&bg_color=0B100D&title_color=8FFF52&text_color=EEF6EF&icon_color=8FFF52&border_color=253128"
    height="165"
    alt="Top languages"
  />
</p>

<p align="center">
  <img
    src="https://streak-stats.demolab.com?user=YACINBK&background=0B100D&border=253128&stroke=8FFF52&ring=8FFF52&fire=8FFF52&currStreakLabel=D9FFB8&sideLabels=EEF6EF&currStreakNum=EEF6EF&sideNums=EEF6EF&dates=8CA08A"
    alt="GitHub streak"
  />
</p>

---

<p align="center">
  <img src="./readme-assets/learning-control-bar.svg" width="100%" alt="Context" />
</p>

- Applied Computer Science Engineering student at **ENISo**, Sousse
- Built production-grade systems around agentic workflows, backend orchestration, secure auth delivery, and CV pipelines
- Internship experience at **Whitecape Technologies** — AI-assisted UX analysis, heuristic engines, RAG with caching, production FastAPI delivery
- Fine-tuning open-source models with **LoRA/QLoRA + quantization** on an RTX 4060; local serving via Ollama and Triton Server
- Active **Zindi competitor** — 31st/69 at IndabaX Tunisia 2025 (soil nutrient prediction)
- Open to internships and technical collaborations in AI systems, backend engineering, intelligent tooling, or automation

---

<p align="center">
  <img src="./readme-assets/connect-control-bar.svg" width="100%" alt="Connect" />
</p>

<p align="center">
  <a href="mailto:yacinbenkacem19@gmail.com">
    <img src="https://img.shields.io/badge/EMAIL-CONTACT-050705?style=for-the-badge&logo=gmail&logoColor=EA4335&labelColor=11160F" alt="Email" />
  </a>
  <a href="https://github.com/YACINBK">
    <img src="https://img.shields.io/badge/GITHUB-YACINBK-050705?style=for-the-badge&logo=github&logoColor=FFFFFF&labelColor=11160F" alt="GitHub" />
  </a>
  <a href="https://www.linkedin.com/in/yacin-ben-kacem/">
    <img src="https://img.shields.io/badge/LINKEDIN-YACIN%20BEN%20KACEM-050705?style=for-the-badge&logo=linkedin&logoColor=0A66C2&labelColor=11160F" alt="LinkedIn" />
  </a>
  <a href="https://yacinbenkacem.me/">
    <img src="https://img.shields.io/badge/PORTFOLIO-OPEN-050705?style=for-the-badge&logo=firefoxbrowser&logoColor=8FFF52&labelColor=11160F" alt="Portfolio" />
  </a>
</p>

<p align="center">
  <img
    src="https://capsule-render.vercel.app/api?type=waving&section=footer&height=120&color=0:050705,40:132015,72:8FFF52,100:050705"
    alt="Footer"
  />
</p>