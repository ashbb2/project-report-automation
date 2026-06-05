"""
RBI key policy rates and lending benchmarks.
Source: Reserve Bank of India (rbi.org.in) — last verified June 2025.
These are updated manually when RBI changes rates; the MPC meets ~6x per year.
"""

_RATES = {
    "repo_rate":            6.25,
    "sdf_rate":             6.00,   # Standing Deposit Facility — effective floor
    "msf_rate":             6.50,   # Marginal Standing Facility — effective ceiling
    "crr":                  4.00,
    "slr":                  18.00,
    "mclr_1yr_range":       "8.90–9.35",  # range across major PSU + private banks
    "msme_term_loan_range": "10.50–13.50",
    "last_verified":        "June 2025",
    "source_url":           "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx",
}


def get_rbi_rates_context() -> str:
    r = _RATES
    return (
        f"RBI KEY POLICY RATES (last verified {r['last_verified']}, "
        f"Source: {r['source_url']}):\n"
        f"• Repo Rate: {r['repo_rate']}%\n"
        f"• Standing Deposit Facility (SDF / floor): {r['sdf_rate']}%\n"
        f"• Marginal Standing Facility (MSF / ceiling): {r['msf_rate']}%\n"
        f"• Cash Reserve Ratio (CRR): {r['crr']}%\n"
        f"• Statutory Liquidity Ratio (SLR): {r['slr']}%\n"
        f"• 1-Year MCLR range (major banks): {r['mclr_1yr_range']}%\n"
        f"• Typical MSME term loan rate: {r['msme_term_loan_range']}% p.a.\n"
        f"  (Note: actual rate depends on borrower credit profile and bank policy)"
    )
