"""Rule-based AI insights engine for Google Ads campaigns."""

from datetime import datetime, timezone
from typing import List


# Thresholds
CTR_LOW_THRESHOLD = 0.01          # 1% CTR — below this is "low CTR"
SPEND_HIGH_THRESHOLD_INR = 500    # INR cost considered "high spend"
CONVERSIONS_ZERO_SPEND_MIN = 100  # Min spend (INR) before flagging zero conversions


def generate_insights(metrics: List[dict]) -> List[dict]:
    """
    Apply rule-based analysis on campaign metrics and return structured insights.

    Rules:
    1. CTR < 1%              → LOW_CTR (WARNING)
    2. cost > 500 INR AND conversions == 0 → ZERO_CONVERSIONS (CRITICAL)
    3. cost > 500 INR AND conversions > 0 AND ctr < 0.005 → HIGH_SPEND_LOW_CONV (WARNING)
    4. ctr >= 0.05 AND conversions > 0   → GOOD_PERFORMANCE (INFO)
    """
    insights = []

    for m in metrics:
        campaign_id = m.get("campaign_id", 0)
        campaign_name = m.get("campaign_name", "Unknown")
        ctr = m.get("ctr", 0.0)
        cost = m.get("cost_inr", 0.0)
        conversions = m.get("conversions", 0.0)

        # Rule 1: Zero conversions with significant spend
        if cost >= CONVERSIONS_ZERO_SPEND_MIN and conversions == 0:
            insights.append({
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "insight_type": "ZERO_CONVERSIONS",
                "severity": "CRITICAL",
                "message": f"Campaign has spent \u20b9{cost:.2f} with zero conversions.",
                "recommendation": "Pause this campaign and review targeting, landing page, and ad copy before resuming.",
            })
            continue

        # Rule 2: High spend, low conversion rate (but some conversions)
        if cost >= SPEND_HIGH_THRESHOLD_INR and conversions > 0 and ctr < 0.005:
            insights.append({
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "insight_type": "HIGH_SPEND_LOW_CONV",
                "severity": "WARNING",
                "message": f"High spend (\u20b9{cost:.2f}) with low CTR ({ctr*100:.2f}%) and only {conversions} conversion(s).",
                "recommendation": "Consider reducing daily budget by 20\u201330% and A/B test new ad creatives.",
            })
            continue

        # Rule 3: Low CTR (any spend)
        if ctr < CTR_LOW_THRESHOLD and cost > 0:
            insights.append({
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "insight_type": "LOW_CTR",
                "severity": "WARNING",
                "message": f"CTR is {ctr*100:.2f}% \u2014 below the 1% benchmark.",
                "recommendation": "Improve ad headlines and descriptions. Test more specific, benefit-driven copy.",
            })
            continue

        # Rule 4: Good performance
        if ctr >= 0.05 and conversions > 0:
            insights.append({
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "insight_type": "GOOD_PERFORMANCE",
                "severity": "INFO",
                "message": f"Strong performance: {ctr*100:.2f}% CTR with {conversions} conversion(s).",
                "recommendation": "Consider increasing budget to scale results.",
            })

    return insights
