 

GLIMMORA REACH 

Phase 1 — Campaign Engine 

Statement of Work — Developer Specification 

 

Module 

Campaign Engine — Phase 1 (AGI-Powered) 

Version 

2.0 

Scope 

Campaign Builder + AGI Intelligence + Optimization + Creative AI + Analytics 

DSP Coverage 

Google Ads (5 types) + Meta Ads (6 types) + LinkedIn Ads (5 types) 

Audience 

1 Frontend Developer (+ 1 on-call if needed), 3 Backend Developers, 1 Senior Backend Developer (5 core + 1 on-call) 

Status 

APPROVED — Development Ready 

Reference 

Glimmora_CampaignBuilder_DSP_Fields.docx (companion field-level spec) 

 

Table of Contents 

​​ 

​1. Executive Summary 

​2. Platform Architecture Overview 

​2.1 Architecture Layers 

​2.2 Technology Stack 

​2.3 Data Flow — Campaign Lifecycle 

​3. Campaign Builder — Manual Form Engine 

​3.1 Campaign Builder Summary 

​3.2 Campaign Types Covered 

​3.3 What Developer Must Build (Campaign Builder) 

​4. AGI Growth Brain — Central Intelligence Layer 

​4.1 AGI Growth Brain — Module Overview 

​4.2 AGI Recommendations Panel — UI Specification 

​4.3 Strategy Engine — Detailed Specification 

​4.4 Audience AI — Detailed Specification 

​4.5 Budget AI — Detailed Specification 

​4.6 Bidding AI — Detailed Specification 

​4.7 Campaign Memory Vault 

​5. Creative AI Studio 

​5.1 AI Ad Copy Generation 

​5.2 AI Image Generation & Suggestion 

​5.3 A/B Testing Framework 

​6. Autonomous Optimization Engine 

​6.1 Optimization Actions 

​6.2 Optimization Rules Engine — User Configuration 

​6.3 Performance Monitoring Service 

​7. Campaign Analytics & Reporting 

​7.1 Executive Dashboard 

​7.2 Campaign Detail View 

​7.3 Cross-DSP Comparison View 

​8. UI/UX Specification 

​8.1 Screen Inventory — Phase 1 

​8.2 Design Principles 

​9. Integrations — Phase 1 

​9.1 DSP API Integrations (Core) 

​9.2 CRM & External Integrations 

​10. Security, Compliance & Governance 

​11. Non-Functional Requirements 

​12. Implementation Plan — Phase 1 

​12.1 Week-by-Week Breakdown 

​12.2 Full Task Checklist 

​13. Team Structure — Phase 1 

​14. Phase 2+ Roadmap — Remaining Features (Summary) 

​15. Assumptions, Risks & Acceptance Criteria 

​15.1 Assumptions 

​15.2 Risks & Mitigation 

​15.3 Acceptance Criteria 

​16. Sign-Off 

​​ 

 

1. Executive Summary 

Glimmora Reach Phase 1 delivers the Campaign Engine — the core module that enables users to create, launch, optimize, and analyze advertising campaigns across Google Ads, Meta Ads, and LinkedIn Ads from a single unified platform. 

Unlike the original field specification (Glimmora_CampaignBuilder_DSP_Fields.docx) which defines the manual campaign builder form engine, this SOW adds the AGI intelligence layer on top. Phase 1 transforms the campaign builder from a manual form into an AI-native campaign engine where the AGI Growth Brain assists, recommends, generates, and autonomously optimizes every aspect of campaign management. 

 

What Phase 1 Delivers: Campaign Builder (manual DSP forms) + AGI Growth Brain + AI Creative Studio + Autonomous Optimization Engine + Campaign Analytics & Reporting + Automation Rules Engine. 

What Phase 1 Does NOT Include: Lead Intelligence System, Influencer Marketplace, Affiliate Console, Global Distribution Engine, Revenue Forecasting AI, White-Label Enterprise, Multi-Region Compliance Expansion. These are Phase 2+. 

 

2. Platform Architecture Overview 

The Phase 1 Campaign Engine follows a cloud-native microservices architecture with the AGI Growth Brain as the central intelligence layer. 

2.1 Architecture Layers 

Layer 

Components 

Responsibility 

Presentation Layer 

React SPA, Executive Dashboard, Campaign Builder UI, Creative Studio UI 

All user-facing interfaces. Real-time form rendering, previews, dashboards. 

API Gateway 

REST API, WebSocket, Rate Limiter, Auth (JWT/OAuth2) 

Single entry point. Request routing, authentication, rate limiting. 

AGI Growth Brain 

Strategy Engine, Audience AI, Budget AI, Creative AI, Optimization AI 

Central intelligence. Generates recommendations, predictions, and autonomous actions. 

Campaign Orchestration 

Campaign Manager, Channel Adapters (Google/Meta/LinkedIn), Scheduler, Queue 

Campaign CRUD, DSP API translation, scheduling, retry logic. 

Optimization Engine 

A/B Test Manager, Performance Monitor, Auto-Scaler, Kill-Switch 

Continuous optimization. Monitors KPIs, triggers automated actions. 

Data Layer 

PostgreSQL, Redis, Campaign Memory Vault, Event Stream (Kafka) 

Persistent storage, caching, campaign history, real-time event processing. 

Integration Layer 

DSP Connectors, CRM Connectors, Webhook Engine, Asset CDN 

External API integrations, media storage, event notifications. 

2.2 Technology Stack 

Component 

Technology 

Frontend 

React 18+ / Next.js, TypeScript, Tailwind CSS, React Hook Form + Zod, Zustand (state), Recharts/D3 (charts) 

Backend 

Node.js (Express/Fastify) or Python (FastAPI), TypeScript/Python 

AI/ML Layer 

Python, LangChain/LlamaIndex, OpenAI GPT-4o / Claude API, Custom fine-tuned models 

Database 

PostgreSQL (primary), Redis (cache/sessions), ClickHouse or TimescaleDB (analytics) 

Message Queue 

Apache Kafka or RabbitMQ (campaign events, optimization triggers) 

Storage 

AWS S3 / GCS (creative assets, campaign exports) 

Infrastructure 

Docker, Kubernetes, AWS/GCP, Terraform, Feature Flags (LaunchDarkly or Unleash) for progressive rollout of new features, AGI modules, and DSP integrations 

Auth 

OAuth 2.0, JWT, RBAC (Role-Based Access Control) 

Monitoring 

Prometheus, Grafana, Sentry (error tracking), AI Observability: LangSmith or custom tracing for all LLM calls (prompt, response, latency, tokens, cost, confidence score). Trace ID links AI recommendations to campaign outcomes for quality measurement. 

2.3 Data Flow — Campaign Lifecycle 

Every campaign follows this lifecycle through the system: 

Step 

Stage 

What Happens 

1 

Campaign Creation 

User opens Campaign Builder → selects DSP + type → form schema loads dynamically. AGI Growth Brain provides real-time recommendations in side panel. 

2 

AGI Enrichment 

As user fills fields, AGI suggests: audience segments, bidding strategy, budget allocation, ad copy, creative assets. User can accept/reject/edit each suggestion. 

3 

Validation 

Frontend Zod validation + backend pre-flight check against DSP API constraints. All errors shown inline. 

4 

Payload Build 

Form values mapped to exact DSP API payload via adapter (Google/Meta/LinkedIn). Zero abstraction loss. 

5 

Asset Upload 

Images, videos, lead forms uploaded to DSP first (required by Meta/LinkedIn before ad creation). 

6 

Campaign Dispatch 

API calls sent to DSP in correct sequence. Campaign ID returned and stored. Idempotency keys prevent duplicate creation. On partial failure (e.g., campaign created but ad group fails), rollback logic reverts completed steps or flags for manual review. 

7 

Monitoring 

Optimization Engine begins polling DSP reporting APIs. Performance data flows into Campaign Memory Vault. 

8 

Autonomous Optimization 

AGI evaluates performance vs KPIs. Triggers: bid adjustments, budget reallocation, creative rotation, geo-rebalancing, pause/scale actions. 

9 

Reporting 

Real-time dashboards updated. AGI generates insights and next-step recommendations. 

 

3. Campaign Builder — Manual Form Engine 

The Campaign Builder is the foundation of the Campaign Engine. It dynamically renders DSP-specific forms, validates inputs, and dispatches campaigns to DSP APIs. The complete field-level specification is defined in the companion document: Glimmora_CampaignBuilder_DSP_Fields.docx. 

Developer Reference: All field definitions, input types, API mappings, character limits, conditional visibility rules, and bidding strategy matrices are in the DSP Fields document. This SOW does NOT duplicate those. This section summarizes the builder architecture and what the developer must implement. 

3.1 Campaign Builder Summary 

Aspect 

Detail 

Total DSPs 

3 — Google Ads, Meta Ads, LinkedIn Ads 

Total Campaign Types 

16 unique schemas (5 Google + 6 Meta + 5 LinkedIn) 

Core Principle 

DSP Selection + Campaign Type = Unique Field Schema. Every field maps 1:1 to DSP native API parameter. 

Form Engine 

React Hook Form + Zod validation. Dynamic rendering from JSON schema per DSP+type. 

Conditional Logic 

Fields show/hide based on other field values (e.g., bidding fields change per strategy selected). 

Payload Builder 

One mapper per DSP. Transforms form values to exact API payload with zero abstraction loss. 

Asset Sequencing 

Meta and LinkedIn require assets (images/videos/forms) uploaded BEFORE ad creative. Builder handles this. 

Validation 

Real-time client-side (Zod) + server-side pre-flight validation against DSP constraints. 

3.2 Campaign Types Covered 

DSP 

Campaign Type 

Key Ad Formats 

Google Ads 

Search 

Responsive Search Ads (RSA) + Extensions 

Google Ads 

Display 

Responsive Display Ads (RDA) 

Google Ads 

Video 

In-stream Skippable/Non-skip, Bumper, Out-stream, Discovery 

Google Ads 

App 

Auto-generated from asset pool (text/image/video/HTML5) 

Google Ads 

Performance Max 

Asset Groups across all Google channels 

Meta Ads 

Awareness 

Single Image, Video, Carousel, Collection 

Meta Ads 

Traffic 

Single Image, Video, Carousel, Collection, Dynamic 

Meta Ads 

Engagement 

Single Image, Video, Carousel 

Meta Ads 

Leads 

Single Image, Video, Carousel + Instant Form 

Meta Ads 

App Promotion 

Single Image, Video, Carousel (App Install) 

Meta Ads 

Sales 

Single Image, Video, Carousel, Collection, Dynamic (Catalog) 

LinkedIn Ads 

Sponsored Content 

Single Image, Video, Carousel, Document, Event 

LinkedIn Ads 

Message Ads 

InMail Message, Conversation Ads 

LinkedIn Ads 

Text Ads 

Text + small image 

LinkedIn Ads 

Dynamic Ads 

Spotlight, Follower, Jobs 

LinkedIn Ads 

Lead Gen Forms 

Sponsored Content + native Lead Form 

3.3 What Developer Must Build (Campaign Builder) 

Refer to Glimmora_CampaignBuilder_DSP_Fields.docx Section 15 for the full implementation checklist. Key deliverables: 

# 

Deliverable 

Details 

1 

16 JSON Field Schemas 

One schema per DSP+campaignType. Defines every field, type, constraints, visibility rules. Each schema has a version number (semver). When a DSP updates their API, a new schema version is created without breaking existing campaigns. 

2 

16 Zod Validation Schemas 

Matching DSP API constraints: char limits, enums, ranges, required/conditional logic. 

3 

Bidding Options Registry 

{ dsp, campaignType } → available strategies. Filter dropdown per combination. 

4 

3 API Payload Mappers 

formValues → Google Ads API payload, Meta Marketing API payload, LinkedIn Marketing API payload. 

5 

DSP Selector UI 

Visual cards with connection status. Step 1 of campaign creation. 

6 

Dynamic Form Renderer 

Loads schema per DSP+type. Conditional show/hide per Section 14.1 rules in DSP Fields doc. 

7 

14 Creative Builder Components 

RSA, RDA, Video, App Assets, PMax Asset Groups, Meta Image/Video/Carousel/Catalog/Lead, LinkedIn Image/Video/Carousel/Message/Text/Dynamic/Lead. 

8 

3 DSP API Integrations 

Campaign creation, asset upload, extension/form creation. Correct sequencing per DSP. 

9 

Error Handling 

Map DSP error codes to user-friendly messages. Show inline field-level errors. 

10 

Draft Save & Resume 

Save incomplete campaign state. Resume later. 

11 

Campaign Duplication 

Copy existing campaign structure. Allow edits before re-submission. 

 

4. AGI Growth Brain — Central Intelligence Layer 

The AGI Growth Brain is the AI core of Glimmora Reach. It sits alongside the Campaign Builder and provides intelligent recommendations, predictions, and autonomous decisions throughout the campaign lifecycle. It does NOT replace user control — every AI suggestion is presented as a recommendation that the user can accept, reject, or modify. 

4.1 AGI Growth Brain — Module Overview 

AGI Module 

Function 

Integration Point 

Strategy Engine 

Recommends campaign type, objective, channel mix based on user goals 

Campaign Builder — Step 1 (before user selects DSP/type) 

Audience AI 

Discovers target audiences, predicts intent, suggests segments 

Campaign Builder — Targeting section 

Budget AI 

Allocates budget across campaigns, channels, geos. Forecasts ROI. 

Campaign Builder — Budget section + Optimization Engine 

Creative AI 

Generates ad copy (headlines, descriptions), suggests images/videos 

Creative Studio + Campaign Builder — Ad Creative section 

Bidding AI 

Recommends bidding strategy based on goals, historical data, conversion maturity 

Campaign Builder — Bidding section 

Optimization AI 

Monitors live campaigns, triggers autonomous actions (pause/scale/rotate/rebalance) 

Optimization Engine (post-launch) 

Cultural & Language AI 

Adapts creatives and targeting for different regions, languages, cultural contexts 

Campaign Builder — when multi-geo campaigns selected 

Campaign Memory 

Stores all campaign decisions, outcomes, learnings. Feeds back into all other modules. 

Data Layer — Campaign Memory Vault 

4.2 AGI Recommendations Panel — UI Specification 

The AGI Recommendations Panel appears as a persistent side panel (right side) in the Campaign Builder. It updates in real-time as the user fills the form. 

Panel Section 

What It Shows 

User Actions 

Strategy Recommendation 

Based on user's stated goal (e.g., 'drive website sales'), AGI recommends: DSP, campaign type, objective 

Accept (auto-fills form) / Reject / Ask AGI to explain reasoning. Each recommendation shows a confidence score (High/Medium/Low) based on data quality and match strength. 

Audience Suggestions 

AGI suggests audience segments: in-market, affinity, custom, lookalike, retargeting lists. Shows estimated reach per segment. 

Add to targeting / Remove / Modify / Ask for alternatives 

Budget Recommendation 

Suggested daily/lifetime budget based on goal, geo, audience size, historical CPMs. Shows projected results (impressions, clicks, conversions). 

Accept / Adjust slider / Ask AGI to recalculate 

Bidding Strategy Advice 

Recommends strategy (e.g., Target CPA vs Maximize Conversions) with reasoning. Shows if account has enough conversion data for smart bidding. 

Accept / Override with manual choice 

Ad Copy Suggestions 

AI-generated headlines, descriptions, primary text for the selected ad format. Shows ad strength prediction. 

Use as-is / Edit in-place / Regenerate / Generate more variations 

Creative Asset Suggestions 

Recommends image dimensions, video length, CTA based on format + objective. Can generate images via AI. 

Use suggestion / Upload own / Generate AI image 

Performance Forecast 

Estimated reach, impressions, clicks, conversions, CPA/ROAS based on all settings. Updates live as form changes. 

View-only. Adjust settings to see forecast change. 

Warnings & Alerts 

Flags potential issues: budget too low, audience too narrow, missing conversion tracking, creative mismatch. 

Fix now (link to field) / Dismiss / Ask AGI for fix 

4.3 Strategy Engine — Detailed Specification 

The Strategy Engine is the first AGI module the user encounters. Before any form fields load, the user states their campaign goal. The Strategy Engine then recommends the optimal path. 

Input: User provides a goal in natural language or selects from predefined options. 

 

User Goal (Input) 

Recommended DSP 

Recommended Campaign Type 

Reasoning 

Drive website sales from search intent 

Google Ads 

Search 

Highest purchase intent from keyword targeting 

Build brand awareness at scale 

Meta Ads 

Awareness 

Largest reach network. CPM-optimized. 

Generate B2B leads from decision-makers 

LinkedIn Ads 

Lead Gen Forms 

Professional targeting: job title, seniority, company. 

Promote mobile app installs 

Google Ads + Meta Ads 

App Campaign + App Promotion 

Cross-platform app install optimization. 

Retarget website visitors with visual ads 

Google Ads or Meta Ads 

Display or Traffic 

Remarketing lists + visual creative formats. 

Drive video views on YouTube 

Google Ads 

Video (In-stream Skippable) 

Native YouTube placement. CPV bidding. 

Maximize eCommerce revenue across all channels 

Google Ads 

Performance Max 

Cross-channel automation. Shopping + Search + Display + YouTube. 

Reach professionals at specific companies 

LinkedIn Ads 

Sponsored Content 

Company name + job function targeting. 

Implementation: The Strategy Engine uses an LLM (GPT-4o/Claude) with a system prompt containing the full DSP capability matrix, bidding requirements, audience capabilities, and historical Glimmora campaign performance data. The LLM reasons about the user's goal and returns structured JSON with recommendations. 

4.4 Audience AI — Detailed Specification 

Audience AI discovers and recommends target audiences based on the user's product/service, goal, and selected DSP. 

Capability 

How It Works 

Developer Implementation 

Audience Discovery 

User describes their product/target customer in natural language. AI maps this to DSP-specific audience segments (in-market, affinity, custom intent, etc.). 

LLM call with DSP audience taxonomy as context. Returns structured audience IDs/URNs. Critical: A PII masking layer strips all personally identifiable information (emails, names, phone numbers, IP addresses) from any data sent to the LLM. Only anonymized product descriptions, audience categories, and aggregated campaign metrics are passed to the AI. 

Lookalike Expansion 

AI recommends lookalike audiences based on existing customer lists or pixel data. 

Query DSP API for available lookalike sources. Present options with estimated reach. 

Audience Sizing 

Shows estimated reach for each audience combination before campaign launch. 

Call DSP Reach Estimation APIs (Google: ReachPlanService, Meta: delivery_estimate, LinkedIn: audience_count). 

Cross-DSP Mapping 

If user runs campaigns on multiple DSPs, AI maps equivalent audiences across platforms. 

Internal mapping table: Google in-market ↔ Meta interests ↔ LinkedIn industries/skills. 

Exclusion Recommendations 

AI suggests audience exclusions (e.g., exclude existing customers from prospecting). 

Analyze connected CRM/pixel data. Suggest custom audience exclusions. 

Seasonal/Trend Signals 

AI flags seasonal audience opportunities (e.g., 'Back to school' audiences in August). 

Date-aware prompts to LLM. Calendar-based audience suggestion triggers. 

4.5 Budget AI — Detailed Specification 

Budget AI recommends optimal budget allocation and forecasts campaign performance. 

Capability 

How It Works 

Developer Implementation 

Budget Recommendation 

Based on goal, geo, audience size, and industry benchmarks, AI suggests daily/lifetime budget. 

LLM with industry CPM/CPC benchmark data + DSP minimum requirements. 

Budget Split (Multi-Campaign) 

If user creates multiple campaigns, AI recommends % allocation per campaign. 

Optimization algorithm (or LLM) weighing historical performance, audience size, geo potential. 

ROI Forecasting 

Given budget + targeting + bidding, predicts: impressions, clicks, conversions, CPA, ROAS. 

Statistical model using historical Glimmora data + DSP benchmark APIs. 

Budget Pacing 

Monitors daily spend vs budget. Alerts if over/under-pacing. 

Daily spend tracking via DSP reporting API. Alert thresholds: >120% or <80% of expected pace. 

Geo Budget Allocation 

For multi-country campaigns, recommends budget split per geo based on market size, CPMs, competition. 

LLM with geo-specific advertising cost data. Adjustable by user. 

4.6 Bidding AI — Detailed Specification 

Bidding AI recommends the optimal bidding strategy for each campaign based on account maturity, conversion data availability, and campaign goals. 

Scenario 

AI Recommendation 

Reasoning Shown to User 

New account, no conversion data 

Maximize Clicks (Google) / Lowest Cost (Meta) / Max Delivery (LinkedIn) 

Your account doesn't have conversion history yet. Start with volume-based bidding to gather data. 

Account has 30+ conversions/month 

Target CPA (Google) / Cost Cap (Meta) / Target Cost (LinkedIn) 

You have enough conversion data for smart bidding. Set a target cost per result. 

Account has 50+ conversions with value 

Target ROAS (Google) / Minimum ROAS (Meta) 

Strong value data available. Optimize for return on ad spend. 

Brand awareness goal 

Target CPM (Google Video) / Lowest Cost with reach optimization (Meta) 

Awareness goals optimize for impressions/reach, not clicks. 

eCommerce with product feed 

Maximize Conversion Value (PMax) 

Product feed + conversion value tracking = best for revenue optimization. 

Implementation: Bidding AI queries the connected DSP account's conversion history via API (Google: ConversionActionService, Meta: ads_insights, LinkedIn: conversion reporting). Based on data volume, it selects from the bidding strategy matrix in the DSP Fields document (Section 13). 

4.7 Campaign Memory Vault 

The Campaign Memory Vault is the persistent knowledge store that makes the AGI Growth Brain smarter over time. Every campaign decision and outcome is stored and fed back into future recommendations. 

Data Stored 

Purpose 

Schema 

Campaign Configuration 

What settings were used (DSP, type, targeting, bidding, budget, creatives) 

JSON snapshot of full campaign payload at launch time. Indexed on: org_id, campaign_id, dsp, campaign_type, geo, created_at. 

Performance Outcomes 

What results the campaign achieved (impressions, clicks, conversions, CPA, ROAS, spend) 

Time-series data from DSP reporting API. Stored daily. Indexed on: campaign_id, date, metric_type. Partitioned by month for query performance. 

AGI Decisions 

What the AI recommended vs what the user accepted/rejected 

Decision log: { recommendation, user_action, timestamp, reasoning, confidence_score }. Indexed on: org_id, campaign_id, module, created_at. 

Optimization Actions 

What autonomous actions were taken (pause, scale, rotate, rebalance) 

Action log: { action_type, trigger_condition, before_state, after_state, result } 

Creative Performance 

Which headlines, images, videos performed best per audience/geo/format 

Creative asset ID + performance metrics + audience context. 

Audience Learnings 

Which audience segments converted best, at what CPA, in which geos 

Audience segment + geo + time period + performance metrics. 

 

5. Creative AI Studio 

The Creative AI Studio is the content generation engine within Glimmora Reach. It generates ad copy, suggests creative assets, and enables A/B testing — all integrated directly into the Campaign Builder. 

5.1 AI Ad Copy Generation 

Feature 

How It Works 

Technical Implementation 

Headline Generation 

AI generates multiple headline variations for the selected ad format, respecting char limits per DSP. 

LLM prompt with: product description, target audience, tone, DSP format constraints. Returns JSON array of headlines. All AI-generated copy passes through a content moderation layer (OpenAI Moderation API or similar) before being shown to the user. Flagged content is blocked with explanation. This prevents policy violations (hate speech, misleading claims, prohibited content) from reaching DSP ad review. 

Description Generation 

Generates descriptions/primary text matching format requirements. 

Same LLM call. Separate prompt templates per ad format (RSA, RDA, Meta single, Carousel, LinkedIn). 

Full Ad Copy Sets 

Generates complete ad copy sets (all headlines + descriptions + CTA) ready to paste into form. 

Batch generation. User reviews and cherry-picks. 

Tone Selector 

User picks tone: Professional, Casual, Urgent, Playful, Authoritative, Empathetic. 

Tone injected into LLM system prompt. Affects all generated copy. 

Competitor Analysis Input 

User can paste competitor ad URLs. AI analyzes and generates differentiated copy. 

Web scrape competitor landing page → LLM extracts messaging → generates contrasting copy. 

Multi-Language Generation 

Generates ad copy in any language. Cultural adaptation, not just translation. 

LLM with cultural context prompt. Native language generation, not machine translation. 

Ad Strength Prediction 

Before submission, predicts Google Ad Strength (Poor/Average/Good/Excellent) based on copy diversity. 

Heuristic model: headline uniqueness, keyword inclusion, description variety, pinning usage. 

Character Counter 

Live char count with DSP limit enforcement on every text field. 

Frontend component: count chars, show remaining, block input at limit, color code (green/yellow/red). 

5.2 AI Image Generation & Suggestion 

Feature 

How It Works 

Technical Implementation 

AI Image Generation 

User describes desired image in natural language. AI generates ad-ready images in correct dimensions. 

Integration with DALL-E 3 / Stable Diffusion API. Auto-crop to DSP-required aspect ratios. 

Dimension Auto-Sizing 

Generated images auto-sized to the required format (e.g., 1200x628 for Meta feed, 1080x1080 for square). 

Post-generation image processing: resize, crop, format conversion (PNG/JPG). 

Asset Library 

All uploaded and generated images stored in a searchable asset library for reuse. 

S3/GCS storage + PostgreSQL metadata (tags, dimensions, campaigns used, performance data). 

Image Recommendations 

Based on ad format + objective, AI suggests ideal image characteristics (color, composition, text overlay rules). 

LLM with creative best-practice knowledge per DSP. Returns guidelines before user uploads. 

Brand Kit Integration 

User uploads brand colors, fonts, logos. AI-generated images respect brand guidelines. 

Brand kit stored per organization. Injected into image generation prompts. 

5.3 A/B Testing Framework 

Feature 

How It Works 

Technical Implementation 

Ad Variant Creation 

User creates 2+ ad variations per ad group (different headlines, images, or CTAs). 

Campaign Builder supports multiple ad creatives per ad group. Each tagged as variant. 

Auto-Variant Generation 

AI generates variant sets automatically: e.g., 3 headline variations × 2 image variations. 

LLM generates copy variants. Image variants from asset library or AI-generated. 

Statistical Significance 

Dashboard shows when a variant has reached statistical significance (95% confidence). 

Bayesian test on conversion rates with 95% confidence threshold. Minimum sample size: 100 conversions per variant before significance can be declared. Sample size calculator shown in UI. 

Auto-Winner Selection 

When significance reached, AI can auto-pause losing variants and scale winners. 

Optimization Engine monitors variant performance. Triggers pause/scale via DSP API. 

Test Results Log 

All A/B test results stored in Campaign Memory Vault for future learning. 

Test config + results + winner stored. Fed back into Creative AI for better future generation. 

 

6. Autonomous Optimization Engine 

The Optimization Engine continuously monitors live campaigns and takes autonomous actions to improve performance. It runs as a background service, evaluating campaigns against KPIs and triggering predefined rules. 

Critical Design Principle: Every autonomous action is logged with full reasoning. Users can review, undo, or disable any automation. The system never takes irreversible actions without user confirmation. Rule Conflict Resolution: When two rules produce conflicting actions (e.g., Rule A says scale budget up, Rule B says pause campaign), the system uses a priority hierarchy: Kill Switch (highest) > Pause > Bid Adjustment > Budget Scale > Creative Rotation (lowest). If same-priority rules conflict, the more conservative action wins. Conflicts are logged and the user is notified. 

6.1 Optimization Actions 

Action 

Trigger Condition 

Implementation 

Pause Underperformer 

Campaign/ad group CPA exceeds 2x target for 3+ consecutive days, OR spend > 3x daily budget with 0 conversions. 

DSP API: Update campaign/ad group status to PAUSED. Notify user via dashboard + email. 

Scale Winner 

Campaign CPA < 80% of target AND daily budget fully spent for 3+ consecutive days. 

DSP API: Increase daily budget by 20% (configurable). Cap at user-set maximum budget. 

Creative Rotation 

Ad creative CTR drops below ad group average by >30% for 7+ days. 

DSP API: Pause underperforming creative. Activate next creative from queue. Generate new AI creative if queue empty. 

Bid Adjustment 

Actual CPA drifting >20% from target. Or impression share dropping. 

DSP API: Adjust bid/target CPA. For manual bidding: increase/decrease CPC by 10-15%. 

Geo Rebalancing 

Specific geo underperforming vs others by >40% on primary KPI. 

DSP API: Reduce budget/bid for underperforming geo. Increase for outperforming geo. 

Audience Refinement 

Specific audience segment CPA > 3x campaign average for 7+ days. 

DSP API: Exclude or reduce bid modifier for underperforming audience. Suggest similar replacement. 

Schedule Optimization 

Specific day/hour slots show consistently poor performance. 

DSP API: Add negative bid modifiers for poor-performing time slots. Increase for high-performing. 

Kill Switch 

Campaign spend exceeds 5x daily budget in a single day (anomaly detection). 

Immediately PAUSE campaign. Send urgent alert to user. Require manual re-enable. 

6.2 Optimization Rules Engine — User Configuration 

Users can configure automation rules through a visual rules builder UI. Each rule has: Trigger Condition, Action, Frequency, and Scope. 

Rule Component 

Options 

Example 

UI Element 

Trigger Metric 

CPA, ROAS, CTR, Spend, Impressions, Conversions, Impression Share 

CPA > $50 

Dropdown + operator + value input 

Time Window 

Last 24h, Last 3 days, Last 7 days, Last 14 days, Last 30 days 

Last 7 days 

Dropdown 

Action 

Pause, Enable, Increase budget %, Decrease budget %, Increase bid %, Decrease bid %, Send alert 

Decrease budget by 20% 

Dropdown + value input 

Frequency 

Once, Daily check, Hourly check 

Daily check 

Dropdown 

Scope 

Campaign, Ad Group, Ad Creative, Keyword, Audience, Geo 

Ad Group level 

Dropdown 

Max Actions per Day 

1, 3, 5, 10, Unlimited 

3 actions max per day 

Number input 

Notification 

Dashboard only, Email, SMS, Slack webhook 

Email + Dashboard 

Multi-select 

6.3 Performance Monitoring Service 

Component 

Specification 

Technical Detail 

Data Polling Frequency 

Every 4 hours for active campaigns. Every 15 minutes for campaigns in first 48 hours. 

Cron jobs or Kafka-scheduled consumers calling DSP Reporting APIs. 

Metrics Collected 

Impressions, Clicks, CTR, Conversions, Conv. Rate, Cost, CPC, CPM, CPA, ROAS, Impression Share, Quality Score (Google) 

Stored in analytics DB (ClickHouse/TimescaleDB). Daily + hourly granularity. 

Anomaly Detection 

Flags sudden spikes in spend (>3x normal), sudden drops in performance (>50% CTR/Conv decline), zero-impression alerts. 

Statistical thresholds + rolling averages. Alert triggers stored as events. 

DSP API Rate Limits 

Respect rate limits per DSP. Google: 15,000 requests/day. Meta: 200 calls/hour. LinkedIn: 100 calls/day. 

Rate limiter with backoff. Queue system for API calls. Batch where possible. 

 

7. Campaign Analytics & Reporting 

The analytics module provides real-time dashboards, cross-DSP performance comparison, and AI-generated insights. Cross-DSP Metric Normalization: Each DSP defines metrics differently (e.g., Google counts a “conversion” differently than Meta). Glimmora normalizes all metrics to a common schema with clear definitions: Impression = ad rendered on screen; Click = user click to destination; Conversion = user-defined goal event via pixel/tag. Discrepancies between DSP definitions are documented and shown as tooltips in the UI. 

7.1 Executive Dashboard 

Dashboard Widget 

Data Shown 

Implementation 

Global Reach Map 

World map showing active campaigns by country. Color intensity = spend/performance. 

D3.js or Mapbox GL. Data from campaign geo targeting + DSP performance per geo. 

Live KPI Cards 

Total Spend, Total Impressions, Total Clicks, Total Conversions, Avg CPA, Avg ROAS — across all DSPs. 

Aggregated from all DSP reporting APIs. Real-time or near-real-time (4hr cache). 

Campaign Status Overview 

Count of Active, Paused, Ended, Draft campaigns per DSP. Visual bar/pie chart. 

PostgreSQL query on campaign status. Grouped by DSP. 

Top Performers 

Top 5 campaigns by conversion volume, lowest CPA, highest ROAS. 

Sorted query on analytics DB. Configurable metric selector. 

AI Insights Feed 

AGI-generated natural language insights: 'Campaign X outperforming by 40%. Consider scaling budget.' 

LLM call with campaign performance data. Generates 3-5 insights per dashboard load. 

Spend Trend 

Line chart: daily spend over time. Filterable by DSP, campaign, date range. 

Time-series chart (Recharts/D3). Data from analytics DB. 

Budget Utilization 

% of budget spent vs allocated per campaign. Over/under-pacing indicators. 

Current spend / daily budget × days elapsed. Color-coded bars. 

7.2 Campaign Detail View 

Section 

Content 

Campaign Summary 

Name, DSP, Type, Status, Date range, Budget, Bidding strategy, Target metrics. 

Performance Metrics Table 

Full metrics: Impressions, Clicks, CTR, Conversions, Conv Rate, Cost, CPC, CPM, CPA, ROAS, Impression Share. Filterable by date. 

Performance Charts 

Line/bar charts: daily metrics over time. Multi-metric overlay (e.g., Spend + Conversions). 

Ad Group / Ad Set Breakdown 

Performance per ad group (Google), ad set (Meta), campaign (LinkedIn). Sortable table. 

Creative Performance 

Each ad creative with individual metrics. Thumbnail preview + key stats. 

Audience Performance 

Performance breakdown per audience segment (where DSP reporting supports it). 

Geo Performance 

Performance per country/region/city. Map visualization. 

Device Performance 

Desktop vs Mobile vs Tablet breakdown. 

Optimization Log 

Timeline of all AGI actions taken: pauses, scaling, bid changes, creative rotations. With reasoning. 

AI Recommendations 

Current AI suggestions for this campaign: what to change, expected impact. 

7.3 Cross-DSP Comparison View 

A unified view comparing performance across Google, Meta, and LinkedIn for the same time period. 

Feature 

What It Shows 

Implementation 

Side-by-Side Metrics 

Same metrics (Impressions, Clicks, Conversions, CPA, ROAS) per DSP in columns. 

Normalized metrics from all 3 DSP APIs into common schema. 

Cost Efficiency Comparison 

Which DSP delivers cheapest CPA, highest ROAS for the user's goals. 

Calculated comparison. Highlighted winner per metric. 

Channel Mix Recommendation 

AGI suggests optimal budget split across DSPs based on performance. 

LLM analysis of cross-DSP data. Returns % allocation recommendation. 

 

8. UI/UX Specification 

Glimmora Reach follows a Netflix-grade simplicity principle: powerful features, minimal cognitive load. Every screen serves one primary purpose. 

8.1 Screen Inventory — Phase 1 

# 

Screen 

Primary Purpose 

Key Components 

1 

Login / SSO 

Authentication 

Email/password, Google SSO, Microsoft SSO. Role-based redirect. 

2 

Organization Selector 

Multi-org support 

Switch between organizations (for agencies managing multiple clients). 

3 

Executive Dashboard 

Overview of all campaigns 

Global map, KPI cards, campaign status, AI insights, spend trend. 

4 

Campaign List 

View & manage all campaigns 

Filterable table: name, DSP, type, status, budget, KPIs. Bulk actions. 

5 

Campaign Builder — Step 1 

Select DSP 

Visual DSP cards (Google/Meta/LinkedIn) with connection status. 

6 

Campaign Builder — Step 2 

Select Campaign Type 

Type cards specific to selected DSP. Brief description per type. 

7 

Campaign Builder — Step 3 

Fill Campaign Fields 

Dynamic form (from DSP Fields spec) + AGI Recommendations side panel. 

8 

Campaign Builder — Step 4 

Review & Launch 

Summary of all settings. Final validation. Launch or Save as Draft. 

9 

Creative Studio 

Generate & manage ad creatives 

AI copy generator, image generator, asset library, A/B variant builder. 

10 

Campaign Detail View 

Deep dive into single campaign 

Metrics, charts, ad/audience/geo breakdown, optimization log, AI recommendations. 

11 

Cross-DSP Comparison 

Compare performance across DSPs 

Side-by-side metrics, cost efficiency, channel mix recommendation. 

12 

Automation Rules Builder 

Configure optimization rules 

Visual rule builder: trigger + condition + action + frequency. 

13 

Automation Rules Log 

Review all automated actions 

Timeline of actions taken, trigger conditions met, results. 

14 

Settings — DSP Connections 

Connect/disconnect DSP accounts 

OAuth flows for Google, Meta, LinkedIn. Connection status. Account selector. 

15 

Settings — Organization 

Org settings, billing, team 

Organization name, billing info, team members, roles. 

16 

Settings — Brand Kit 

Upload brand assets 

Logo, brand colors, fonts, tone of voice description. Used by Creative AI. 

17 

Notifications Center 

View alerts and AI recommendations 

Real-time alerts, performance warnings, optimization suggestions. 

18 

Help / AI Explainability 

Understand AI decisions 

Natural language explanations of why AGI made each recommendation/action. 

8.2 Design Principles 

Principle 

Implementation 

Netflix-Grade Simplicity 

One primary action per screen. Progressive disclosure (advanced options collapsed by default). No screen requires more than 3 clicks to reach. 

Data-Driven Visualization 

Charts and visual indicators preferred over raw numbers. Color-coded status (green/yellow/red). Sparklines in tables. 

AI as Co-Pilot, Not Autopilot 

Every AI suggestion has Accept/Reject/Edit controls. AI reasoning always accessible. User always has final control. 

Real-Time Feedback 

Form validation as you type. Live character counters. Performance forecast updates as fields change. 

Responsive Design 

Desktop-first (campaign management is a desktop task). Tablet-friendly dashboard. Mobile: view-only dashboards. 

Minimal Cognitive Load 

Consistent layout patterns. Predictable navigation. Tooltips on every field explaining what it does. 

Dark Mode Support 

Full dark mode theme. User preference stored. 

 

9. Integrations — Phase 1 

9.1 DSP API Integrations (Core) 

DSP 

API 

Auth Method 

Key Endpoints Used 

Google Ads 

Google Ads API v17+ 

OAuth 2.0 + Developer Token 

Campaign, AdGroup, Ad, Asset, BiddingStrategy, CampaignCriterion, ReachPlan, Reporting 

Meta Ads 

Marketing API v20+ 

OAuth 2.0 (Facebook Login) 

Campaign, AdSet, Ad, AdCreative, AdImage, AdVideo, LeadGenForm, AdsInsights, DeliveryEstimate 

LinkedIn Ads 

Marketing API v202402+ 

OAuth 2.0 (3-legged) 

CampaignGroup, Campaign, Creative, Asset, LeadGenForm, AdTargetingFacets, Analytics 

9.2 CRM & External Integrations 

Integration 

Purpose 

Priority 

Implementation 

HubSpot 

Sync conversion events, customer lists for remarketing 

P1 (Phase 1) 

HubSpot API. Bi-directional sync: contacts → custom audiences. 

Salesforce 

Sync conversion events, lead data, customer lists 

P1 (Phase 1) 

Salesforce REST API. Push campaign leads, pull customer segments. 

Google Analytics 4 

Import conversion events, audience segments 

P0 (Phase 1) 

GA4 API. Pull conversion data for campaign attribution. 

Slack 

Real-time campaign alerts, optimization notifications 

P1 (Phase 1) 

Slack Webhook API. Configurable per alert type. 

Webhook (Generic) 

Push campaign events to any external system 

P1 (Phase 1) 

User configures webhook URL + events. POST JSON payloads. 

 

10. Security, Compliance & Governance 

Requirement 

Specification 

Implementation 

Authentication 

OAuth 2.0 + JWT tokens. SSO via Google/Microsoft. 

NextAuth.js or Auth0. JWT with short expiry (15min) + refresh tokens. 

Role-Based Access Control (RBAC) 

Roles: Super Admin, Admin, Campaign Manager, Analyst (view-only), Client. 

RBAC middleware. Permission matrix per role per resource. 

Data Encryption 

AES-256 at rest. TLS 1.3 in transit. 

Cloud KMS for key management. HTTPS everywhere. 

GDPR Compliance 

User consent management. Data export. Right to deletion. 

Consent flags per user. Data export API. Cascade delete for user data. 

Audit Logs 

Every campaign creation, edit, deletion, optimization action logged with user/AI identity + timestamp. 

Append-only audit log table. Immutable. Queryable by admin. 

DSP Token Security 

OAuth tokens for Google/Meta/LinkedIn encrypted at rest. Never exposed to frontend. 

Token vault (AWS Secrets Manager or similar). Backend-only token access. 

Rate Limiting 

API rate limiting per user/org to prevent abuse. 

Redis-based rate limiter. Configurable per endpoint. 

IP Whitelisting (Enterprise) 

Optional IP restriction for enterprise clients. 

Configurable per organization. Middleware check. 

 

11. Non-Functional Requirements 

Requirement 

Target 

How to Achieve 

Availability 

99.9% uptime (max 8.7 hours downtime/year) 

Multi-AZ deployment. Health checks. Auto-restart on failure. 

Response Time 

API: < 200ms (p95). Dashboard load: < 2 seconds. Campaign Builder: < 1 second per field schema load. 

Redis caching. CDN for static assets. Lazy loading for heavy components. 

Scalability 

Support 10,000+ concurrent users. 100,000+ active campaigns. 

Horizontal scaling (Kubernetes). Database read replicas. Queue-based processing. 

AI Response Time 

LLM recommendations: < 3 seconds. Image generation: < 15 seconds. 

Streaming LLM responses. Async image generation with loading states. AI Cost Governance: LLM API usage tracked per org (tokens consumed, image generations). Monthly cost dashboard in admin panel. Per-org soft limits with alerts at 80% threshold. Hard limits configurable per plan tier. Prompt optimization to minimize token usage (short system prompts, structured outputs). Image generation limited to 50/org/day default (configurable). 

Data Retention 

Campaign data retained for 2 years. Audit logs retained for 5 years. 

Tiered storage: hot (90 days), warm (2 years), cold (5 years for audit). 

Multi-Tenancy 

Complete data isolation between organizations. 

Schema-per-tenant or row-level security in PostgreSQL. Org ID on every query. 

Backup & Recovery 

Daily automated backups. RPO: 1 hour. RTO: 4 hours. 

Automated DB snapshots. Point-in-time recovery. DR drill: full recovery test quarterly. Results documented. RTO/RPO validated each drill. 

 

12. Implementation Plan — Phase 1 

Phase 1 is a 30-day sprint divided into 4 weeks. Each week has clear deliverables and success criteria. 

12.1 Week-by-Week Breakdown 

Period 

Focus Area 

Deliverables 

Week 1 (Day 1-7) 

Foundation & Architecture 

Finalize system architecture. Set up cloud infra (K8s, DB, Redis, Kafka). Build auth system (OAuth, JWT, RBAC). Create 16 JSON field schemas from DSP Fields doc. Build Zod validation schemas. Build DSP OAuth connection flows (Google/Meta/LinkedIn). UX wireframes finalized (Figma). 

Week 2 (Day 8-14) 

Core Campaign Builder + AGI 

Build dynamic form renderer (React Hook Form + Zustand). Build all 16 campaign forms (5 Google + 6 Meta + 5 LinkedIn). Build 3 API payload mappers. Build bidding options registry. Implement AGI Growth Brain core: Strategy Engine + Audience AI + Budget AI + Bidding AI. Build AGI Recommendations side panel UI. Build Creative AI Studio: ad copy generation. 

Week 3 (Day 15-21) 

Integrations + Optimization + Analytics 

Complete DSP API integrations (campaign creation, asset upload, extensions). Build Optimization Engine: monitoring service, rule engine, autonomous actions. Build Analytics module: executive dashboard, campaign detail view, cross-DSP comparison. Build automation rules builder UI. CRM integrations (HubSpot/Salesforce/GA4). Notification system. 

Week 4 (Day 22-30) 

Hardening + Testing + Launch 

Security hardening: encryption, RBAC, audit logs, rate limiting. Performance optimization: caching, lazy loading, API response tuning. End-to-end testing: create campaign on each DSP, verify data flow, test optimization triggers. UAT with internal Glimmora pilot campaigns. Bug fixes. Production deployment. Global launch. 

12.2 Full Task Checklist 

Master checklist combining Campaign Builder tasks (from DSP Fields doc) with new AGI/Optimization/Analytics tasks. 

Phase A — Schema & Data Model 

# 

Task 

Owner 

Priority 

Status 

A1 

Build 16 JSON field schemas (5 Google + 6 Meta + 5 LinkedIn) per DSP Fields spec 

Backend 

P0 

Open 

A2 

Build Zod validation schemas matching each DSP API constraint 

Frontend/Backend 

P0 

Open 

A3 

Build biddingOptions registry: { dsp, campaignType } → available strategies 

Backend 

P0 

Open 

A4 

Build API payload mappers: formValues → Google Ads API payload (all 5 types) 

Backend 

P0 

Open 

A5 

Build API payload mappers: formValues → Meta Marketing API payload (all 6 objectives) 

Backend 

P0 

Open 

A6 

Build API payload mappers: formValues → LinkedIn Marketing API payload (all 5 types) 

Backend 

P0 

Open 

A7 

Design Campaign Memory Vault schema (PostgreSQL + analytics DB) 

Backend/Data 

P0 

Open 

A8 

Design AGI decision log schema (recommendations, user actions, outcomes) 

Backend/AI 

P0 

Open 

A9 

Design optimization action log schema 

Backend 

P0 

Open 

A10 

Cache LinkedIn targeting facet taxonomy — refresh weekly 

Backend 

P1 

Open 

A11 

Store/retrieve Google audience lists per connected account 

Backend 

P1 

Open 

 

Phase B — Frontend & UI 

# 

Task 

Owner 

Priority 

Status 

B1 

DSP selector step (Google/Meta/LinkedIn visual cards + connection status) 

Frontend 

P0 

Open 

B2 

Campaign Type selector per DSP (dynamic options) 

Frontend 

P0 

Open 

B3 

Conditional field renderer (show/hide based on form state) 

Frontend 

P0 

Open 

B4 

Google Search form: Campaign + Ad Group + RSA + Extensions 

Frontend 

P0 

Open 

B5 

Google Display form: Campaign + RDA + Audience/Placement targeting 

Frontend 

P0 

Open 

B6 

Google Video form: Subtype selector + format-specific fields + YouTube URL validator 

Frontend 

P0 

Open 

B7 

Google App form: App ID lookup + Asset pool upload grid 

Frontend 

P0 

Open 

B8 

Google PMax form: Asset Group builder + Audience Signals + Feed selector 

Frontend 

P0 

Open 

B9 

Meta Campaign form: Objective picker + CBO toggle + all campaign fields 

Frontend 

P0 

Open 

B10 

Meta Ad Set form: Budget/schedule + Bidding + Full audience targeting + Placements 

Frontend 

P0 

Open 

B11 

Meta Ad Creative forms: Image/Video/Carousel/Catalog/Lead Form builders 

Frontend 

P0 

Open 

B12 

LinkedIn Campaign Group + Campaign form 

Frontend 

P0 

Open 

B13 

LinkedIn Targeting form: Full facet taxonomy with search-as-you-type 

Frontend 

P0 

Open 

B14 

LinkedIn Creative forms: Image/Video/Carousel/Message/Text/Dynamic/Lead Gen 

Frontend 

P0 

Open 

B15 

Bidding strategy form component (conditional inputs per strategy) 

Frontend 

P0 

Open 

B16 

AGI Recommendations side panel (persistent right panel in Campaign Builder) 

Frontend 

P0 

Open 

B17 

Executive Dashboard (global map, KPI cards, status overview, AI insights, spend trend) 

Frontend 

P0 

Open 

B18 

Campaign List view (filterable table with bulk actions) 

Frontend 

P0 

Open 

B19 

Campaign Detail view (metrics, charts, breakdown, optimization log) 

Frontend 

P0 

Open 

B20 

Cross-DSP Comparison view 

Frontend 

P1 

Open 

B21 

Creative Studio UI: AI copy generator + image generator + asset library 

Frontend 

P0 

Open 

B22 

Automation Rules Builder UI (visual rule builder) 

Frontend 

P0 

Open 

B23 

Automation Rules Log (timeline of actions) 

Frontend 

P1 

Open 

B24 

Settings: DSP Connections (OAuth flows) 

Frontend 

P0 

Open 

B25 

Settings: Organization + Brand Kit 

Frontend 

P1 

Open 

B26 

Notification Center 

Frontend 

P1 

Open 

B27 

Ad preview component (real-time per format per DSP) 

Frontend 

P1 

Open 

B28 

Character counter on all text fields 

Frontend 

P0 

Open 

B29 

Login / SSO screen 

Frontend 

P0 

Open 

B30 

Help / AI Explainability screen 

Frontend 

P2 

Open 

 

Phase C — Backend & API Integration 

# 

Task 

Owner 

Priority 

Status 

C1 

Google Ads campaign creation via API (all 5 campaign types) 

Backend 

P0 

Open 

C2 

Google Ads asset creation (images, logos to Asset Library) 

Backend 

P0 

Open 

C3 

Google Ads extensions/assets (Sitelinks, Callouts, Structured Snippets, Call, Lead Form) 

Backend 

P1 

Open 

C4 

Meta campaign creation via API (Campaign + AdSet + AdCreative + Ad, all objectives) 

Backend 

P0 

Open 

C5 

Meta image/video upload (AdImages/AdVideos before ad creative) 

Backend 

P0 

Open 

C6 

Meta Lead Form creation API 

Backend 

P1 

Open 

C7 

LinkedIn campaign creation via API (CampaignGroup + Campaign + Creatives, all formats) 

Backend 

P0 

Open 

C8 

LinkedIn asset upload (image/video via Digital Media API) 

Backend 

P0 

Open 

C9 

LinkedIn Lead Gen Form creation API 

Backend 

P1 

Open 

C10 

DSP Reporting API integration (Google/Meta/LinkedIn → analytics DB) 

Backend 

P0 

Open 

C11 

API error handling: Map DSP error codes to user-friendly messages 

Backend 

P0 

Open 

C12 

Pre-flight validation: Validate all fields before API dispatch 

Backend 

P0 

Open 

C13 

Draft save: Save incomplete campaign builder state; resume later 

Backend 

P1 

Open 

C14 

Campaign duplication: Copy + edit before re-submission 

Backend 

P1 

Open 

 

Phase D — AGI & Intelligence Layer 

# 

Task 

Owner 

Priority 

Status 

D1 

AGI Strategy Engine: Goal → DSP + campaign type recommendation (LLM integration) 

AI/Backend 

P0 

Open 

D2 

AGI Audience AI: Product description → DSP audience segment mapping 

AI/Backend 

P0 

Open 

D3 

AGI Budget AI: Budget recommendation + ROI forecasting 

AI/Backend 

P0 

Open 

D4 

AGI Bidding AI: Account maturity analysis + strategy recommendation 

AI/Backend 

P0 

Open 

D5 

Creative AI: Ad copy generation (headlines, descriptions) per DSP format + char limits 

AI/Backend 

P0 

Open 

D6 

Creative AI: AI image generation integration (DALL-E 3 / Stable Diffusion) 

AI/Backend 

P1 

Open 

D7 

Creative AI: Multi-language ad copy generation 

AI/Backend 

P1 

Open 

D8 

Campaign Memory Vault: Store campaign configs, performance, decisions, actions 

Backend/Data 

P0 

Open 

D9 

AI Insights Generator: Generate natural language insights from campaign data 

AI/Backend 

P0 

Open 

D10 

AI Explainability: Generate reasoning explanations for every AI recommendation 

AI/Backend 

P1 

Open 

D11 

Audience Sizing: Integrate DSP reach estimation APIs 

Backend 

P1 

Open 

D12 

Performance Forecast: Predict campaign results based on settings 

AI/Backend 

P1 

Open 

 

Phase E — Optimization & Automation 

# 

Task 

Owner 

Priority 

Status 

E1 

Performance monitoring service: Poll DSP reporting APIs on schedule 

Backend 

P0 

Open 

E2 

Anomaly detection: Spend spikes, performance drops, zero-impression alerts 

Backend 

P0 

Open 

E3 

Auto-pause underperformers (rule-based) 

Backend 

P0 

Open 

E4 

Auto-scale winners (rule-based) 

Backend 

P0 

Open 

E5 

Creative rotation (pause underperforming creatives, activate new) 

Backend 

P0 

Open 

E6 

Bid adjustment automation 

Backend 

P1 

Open 

E7 

Geo rebalancing automation 

Backend 

P1 

Open 

E8 

Kill switch (emergency pause on anomalous spend) 

Backend 

P0 

Open 

E9 

User-configurable rules engine (visual builder → rule storage → execution) 

Backend 

P0 

Open 

E10 

Optimization action logging (full audit trail with reasoning) 

Backend 

P0 

Open 

E11 

A/B test statistical significance calculator 

Backend/Data 

P1 

Open 

E12 

Auto-winner selection for A/B tests 

Backend 

P1 

Open 

 

Phase F — Security & Infrastructure 

# 

Task 

Owner 

Priority 

Status 

F1 

OAuth 2.0 + JWT authentication system 

Backend 

P0 

Open 

F2 

SSO integration (Google, Microsoft) 

Backend 

P0 

Open 

F3 

RBAC: Roles + permissions matrix + middleware 

Backend 

P0 

Open 

F4 

Data encryption (AES-256 at rest, TLS 1.3 in transit) 

DevOps 

P0 

Open 

F5 

DSP OAuth token vault (encrypted storage, backend-only access) 

Backend/DevOps 

P0 

Open 

F6 

Audit logging system (append-only, queryable) 

Backend 

P0 

Open 

F7 

API rate limiting (Redis-based) 

Backend 

P0 

Open 

F8 

Cloud infrastructure setup (K8s, load balancing, auto-scaling) 

DevOps 

P0 

Open 

F9 

Database setup (PostgreSQL + Redis + analytics DB) 

DevOps 

P0 

Open 

F10 

CI/CD pipeline 

DevOps 

P0 

Open 

F11 

Monitoring & alerting (Prometheus, Grafana, Sentry) 

DevOps 

P0 

Open 

F12 

GDPR compliance: Consent management, data export, right to deletion 

Backend 

P1 

Open 

 

13. Team Structure — Phase 1 

Role 

Count 

Responsibilities 

Senior Backend Developer 

1 

System architecture, technical decisions, AGI Growth Brain design and implementation (Strategy Engine, Audience AI, Budget AI, Bidding AI), optimization engine core logic, LLM prompt engineering, campaign memory vault design, security architecture, code review for all backend PRs, DevOps and cloud infrastructure. 

Backend Developer 1 

1 

Google Ads API integration (all 5 campaign types: Search, Display, Video, App, PMax), Google Ads payload mapper, Google asset upload service, Google extensions creation, Google Reporting API integration, Google error code mapping. 

Backend Developer 2 

1 

Meta Ads API integration (all 6 objectives), Meta payload mapper, Meta image/video upload, Meta Lead Form API, Meta Reporting API (AdsInsights), Meta error code mapping. Also handles CRM integrations (HubSpot, Salesforce, GA4). 

Backend Developer 3 

1 

LinkedIn Ads API integration (all 5 types), LinkedIn payload mapper, LinkedIn asset upload (2-step register+PUT), LinkedIn Lead Gen Form API, LinkedIn Reporting API, LinkedIn targeting facets cache. Also handles webhook engine, Slack integration, notification system, campaign export. 

Frontend Developer 

1 

All frontend development: Campaign Builder (16 dynamic forms), conditional field renderer, Executive Dashboard, Campaign Detail views, Creative Studio UI, AGI Recommendations panel, Automation Rules Builder, Settings screens, charts/maps, ad preview components, responsive design. Owns entire frontend codebase. 

Frontend Developer 2 (On-Call) 

1 

On-call support for Frontend Developer during peak workload weeks (Week 2-3: form building, Week 4: dashboard wiring). Assists with UI screens, testing, and polish. Not required full-time — engaged only when Frontend Developer flags capacity issues. 

 

14. Phase 2+ Roadmap — Remaining Features (Summary) 

The following features are OUT OF SCOPE for Phase 1 but planned for subsequent phases. They are listed here for context so developers understand the full platform vision and can make Phase 1 architecture decisions that support future expansion. 

# 

Feature 

Description 

Phase 1 Architecture Impact 

1 

Lead Intelligence System 

AI lead scoring, fraud detection, intent classification, readiness scoring, CRM routing. Leads captured from campaigns scored and routed automatically. 

Phase 1 must store lead data from DSP lead forms. Schema should support lead scoring fields. CRM integration in Phase 1 enables Phase 2 routing. 

2 

Influencer Marketplace 

AI-powered influencer discovery, scoring, automated onboarding, contract management, performance tracking, commission payouts. 

Phase 1 has no direct dependency. Separate microservice. Ensure user/org model supports influencer accounts. 

3 

Affiliate Console 

Affiliate onboarding, tracking link generation, conversion attribution, commission calculation, analytics dashboard. 

Phase 1 has no direct dependency. Separate microservice. UTM/tracking infrastructure in Phase 1 supports affiliate attribution. 

4 

Global Distribution Engine 

App store distribution, SaaS onboarding funnel automation, website traffic orchestration, event/content promotion beyond paid ads. 

Phase 1 focuses on paid advertising only. Distribution engine is a separate system. Campaign orchestration architecture should be extensible to non-DSP channels. 

5 

Revenue Forecasting AI 

Advanced revenue prediction models using campaign data + CRM data + market signals. Predictive LTV, churn probability, revenue attribution. 

Campaign Memory Vault in Phase 1 stores the historical data needed. Analytics DB schema should support forecasting queries. 

6 

White-Label Enterprise 

Multi-tenant white-labeling: custom branding, custom domains, reseller management, per-tenant billing. 

Phase 1 multi-tenancy (org isolation) is foundation. Theme/branding system should be configurable per org. 

7 

Multi-Region Compliance 

Region-specific data residency (EU, APAC, etc.), CCPA, LGPD, PIPA compliance. Data processing agreements. 

Phase 1 GDPR compliance is foundation. Data model should include region flags. Storage layer should support geo-partitioning. 

8 

Advanced Admin Panel 

Full enterprise admin: user lifecycle management, API key management, usage metering, billing integration, platform health monitoring. 

Phase 1 basic admin (user/role management, DSP connections) is foundation. Extensible settings architecture. 

 

15. Assumptions, Risks & Acceptance Criteria 

15.1 Assumptions 

# 

Assumption 

1 

Cloud infrastructure (AWS/GCP) is provisioned and accessible from Day 1. 

2 

Google Ads, Meta, and LinkedIn developer accounts with API access are approved before development starts. 

3 

LLM API access (OpenAI GPT-4o or Anthropic Claude) is available with sufficient rate limits. 

4 

Image generation API (DALL-E 3 or Stable Diffusion) is available. 

5 

UX wireframes are finalized in Figma by end of Week 1. 

6 

Stakeholder approvals for architecture decisions happen within 24 hours of request. 

7 

Test DSP accounts with billing enabled are available for integration testing. 

8 

The DSP Fields specification document (Glimmora_CampaignBuilder_DSP_Fields.docx) is the authoritative source for field-level details and will not change during Phase 1 without formal review. 

15.2 Risks & Mitigation 

Risk 

Severity 

Mitigation 

DSP API policy changes during development 

Medium 

Multi-channel abstraction layer. Adapter pattern isolates DSP-specific logic. Quick adapter updates. 

LLM response quality inconsistent 

Medium 

Extensive prompt engineering. Output validation schemas. Fallback to deterministic rule-based engine if LLM unavailable. AI Guardrails: All LLM outputs are validated against DSP constraint schemas before display (e.g., headline must be ≤ 30 chars, bid must be > 0). Budget recommendations capped at 2x user’s historical max. Audience suggestions validated against DSP’s actual taxonomy. No AI output directly modifies a live campaign without user confirmation. 

DSP API rate limits hit during optimization 

High 

Queue-based API calls with backoff. Batch reporting requests. Cache aggressively. 

30-day timeline too aggressive 

High 

P0 tasks are non-negotiable. P1 tasks can slip to Week 5-6 if needed. P2 moves to Phase 2. 

Data privacy risks from AI processing 

Medium 

No PII sent to LLM. Campaign data anonymized before AI processing. User consent for AI features. 

Cross-DSP metric normalization inaccurate 

Low 

Documented metric definitions per DSP. Disclaimer on cross-DSP comparisons. 

15.3 Acceptance Criteria 

# 

Criterion 

Validation Method 

1 

User can create and successfully launch a campaign on each DSP (Google Search, Display, Video, App, PMax, Meta all 6 objectives, LinkedIn all 5 types) from Glimmora. 

End-to-end test: create → launch → verify campaign appears in DSP dashboard. 

2 

AGI Growth Brain provides recommendations during campaign creation (strategy, audience, budget, bidding, creative). 

Verify recommendations panel updates as user fills form. Verify accept/reject works. AI Quality KPIs: Strategy recommendation acceptance rate > 40%. Generated ad copy passes DSP ad review > 90% of the time. Budget forecast accuracy within ±30% of actual results after 7 days. LLM response latency < 3 seconds (p95). Fallback activation rate < 5% (LLM availability > 95%). 

3 

Creative AI generates ad copy that respects DSP character limits and format constraints. 

Generate copy for each ad format. Verify all within char limits. 

4 

Optimization Engine monitors live campaigns and triggers at least one autonomous action. 

Run test campaign, trigger rule condition, verify action taken and logged. 

5 

Executive Dashboard shows live data from all 3 DSPs. 

Verify KPIs, campaign list, spend trend populate from DSP reporting APIs. 

6 

Security: RBAC, encryption, audit logs all functional. 

Security review checklist. Penetration test scope: OWASP Top 10, authentication flows, DSP OAuth token vault, API abuse/rate limit bypass, input injection, RBAC privilege escalation. 

7 

Platform handles 100 concurrent users without degradation. 

Load test with k6 or similar. p95 response < 200ms. 

 

16. Sign-Off 

This Statement of Work defines the complete scope, architecture, features, implementation plan, and acceptance criteria for Glimmora Reach Phase 1 — Campaign Engine. 

 

Companion Document: Glimmora_CampaignBuilder_DSP_Fields.docx — Contains all field-level specifications, input types, API mappings, character limits, conditional visibility rules, bidding strategy matrices, and API creation sequences for all 16 campaign types. Developers MUST reference both documents together. 

 

  

Product Owner / CEO 

  

Technical Lead / Architect 

  

Date 

  

Date 

 

10.1 Incident Response & Escalation Matrix 

When a production incident occurs, the following escalation matrix applies. All incidents logged with timestamps and resolution details. 

Severity 

Examples 

Respond 

Resolve 

Who Is Called 

P0 Critical 

Platform down, uncontrolled ad spend, data breach, kill switch failure 

15 min 

1 hour 

Senior BE + relevant DSP dev. All hands if needed. 

P1 High 

One DSP failing, reporting gaps, AGI errors, optimization not firing 

1 hour 

4 hours 

Relevant DSP dev or Senior BE for AGI issues. 

P2 Medium 

UI bugs, slow dashboard, low-quality AGI suggestions, chart issues 

4 hours 

24 hours 

Assigned in next standup. Scheduled fix. 

P3 Low 

Cosmetic issues, tooltip errors, dark mode glitch, minor UX improvements 

Next day 

Next sprint 

Backlog. Picked up when capacity allows. 

Communication: P0 via Slack #incidents immediately. P1 via Slack within 1 hour. P2/P3 tracked in issue tracker. Post-mortems written for all P0/P1 incidents within 48 hours. 

End of Document 