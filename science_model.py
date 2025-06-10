import pandas as pd

# 15 SPARK questions mapping
QUESTIONS = {
    1: {'item': 'Stability',    'question': 'When tasks come with clear structure, you feel…', 
        'choices': ['⚡ Super-charged','🛑 Short-circuited','🟡 Static','⚠️ Overloaded']},
    2: {'item': 'Trust',        'question': 'Collaborating with teammates you trust, you feel…',
        'choices': ['🤝 Aligned','🔒 Guarded','➡️ Neutral','❓ Exposed']},
    3: {'item': 'Singularity',  'question': 'When you tunnel-vision on a solo project, you feel…',
        'choices': ['🔋 Sharpened','🪫 Diffuse','⚖️ Steady','❓ Uncertain']},
    4: {'item': 'Principles',   'question': 'Guided by our core principles, your dedication feels…',
        'choices': ['🚀 Committed','⛔ Resistant','➖ Neutral','❓ Conflicted']},
    5: {'item': 'Passion',      'question': 'At the start of your day, your energy level is…',
        'choices': ['⚡ Fired-up','😴 Drained','🔄 Steady','💤 Lethargic']},
    6: {'item': 'Purpose',      'question': 'When your work aligns with your purpose, you feel…',
        'choices': ['🎯 Centered','🌪 Aimless','🟡 Grounded','🌫 Adrift']},
    7: {'item': 'Accountability','question': 'Owning your outcomes fully, you feel…',
        'choices': ['✅ Effective','❌ Ineffective','🎉 Valued','🙁 Overlooked']},
    8: {'item': 'Appreciation', 'question': 'When peers recognize your efforts, you feel…',
        'choices': ['👏 Seen','👻 Invisible','🙂 Acknowledged','😐 Neutral']},
    9: {'item': 'Belonging',    'question': 'Being included in team decisions, you feel…',
        'choices': ['🤗 Embraced','🚫 Excluded','😌 Accepted','😕 Isolated']},
    10:{'item': 'Resilience',   'question': 'After a high-stress sprint, you feel…',
        'choices': ['💪 Bounced-back','😩 Drained','🔄 Stable','😓 Shaky']},
    11:{'item': 'Renewal',      'question': 'Following a recharge (break/weekend), you feel…',
        'choices': ['⚡ Fully-charged','😪 Still-tired','🙂 Refreshed','😐 No-change']},
    12:{'item': 'Adaptability', 'question': 'When plans shift quickly, you feel…',
        'choices': ['🤸 Agile','🧱 Rigid','➖ Neutral','😤 Frustrated']},
    13:{'item': 'Connection',   'question': 'Striking up a genuine connection, you feel…',
        'choices': ['🔗 Bonded','⚪ Alone','🤝 Supported','❔ Detached']},
    14:{'item': 'Candor',       'question': 'Sharing honest feedback, you feel…',
        'choices': ['🔊 Unfiltered','🔒 Reserved','✔️ Clear','😬 Awkward']},
    15:{'item': 'Contribution', 'question': 'Making an impact today, you feel…',
        'choices': ['✨ Purposeful','⚪ Ineffective','🚀 Motivated','🙁 Overlooked']}
}

# Map each emoji choice to a numeric score
CHOICE_TO_SCORE = {
    emoji: score for score, emojis in {
        4:['⚡ Super-charged','🤝 Aligned','🔋 Sharpened','🚀 Committed','⚡ Fired-up',
           '🎯 Centered','✅ Effective','👏 Seen','🤗 Embraced','💪 Bounced-back',
           '⚡ Fully-charged','🤸 Agile','🔗 Bonded','🔊 Unfiltered','✨ Purposeful'],
        3:['⚠️ Overloaded','❓ Exposed','❓ Uncertain','❓ Conflicted','💤 Lethargic',
           '🌫 Adrift','🙁 Overlooked','😐 Neutral','😌 Accepted','🔄 Stable',
           '😐 No-change','😤 Frustrated','❔ Detached','😬 Awkward','🚀 Motivated'],
        2:['🟡 Static','➡️ Neutral','⚖️ Steady','➖ Neutral','🔄 Steady',
           '🟡 Grounded','🎉 Valued','🙂 Acknowledged','➖ Neutral','🔄 Stable',
           '🙂 Refreshed','➖ Neutral','🤝 Supported','✔️ Clear','🚀 Motivated'], # adjust specifics
        1:['🛑 Short-circuited','🔒 Guarded','🪫 Diffuse','⛔ Resistant','😴 Drained',
           '🌪 Aimless','❌ Ineffective','👻 Invisible','🚫 Excluded','😩 Drained',
           '😪 Still-tired','🧱 Rigid','⚪ Alone','🔒 Reserved','⚪ Ineffective']
    }.items() for emoji in emojis
}

# Scales for each framework
SCALES = {
  'SDT_Autonomy':     ['Stability','Adaptability'],
  'SDT_Competence':   ['Singularity','Contribution'],
  'SDT_Relatedness':  ['Trust','Appreciation','Belonging','Connection','Candor'],
  'MBI_Exhaustion':   ['Resilience','Renewal'],
  'MBI_Efficacy':     ['Accountability','Contribution'],
  'UWES_Vigor':       ['Passion'],
  'UWES_Dedication':  ['Principles','Purpose'],
  'UWES_Absorption':  ['Singularity']
}

def preprocess_raw_responses(raw: list) -> pd.DataFrame:
    """Convert raw list of {q#: emoji} into DataFrame of scores."""
    records = []
    for entry in raw:
        scored = {}
        for q_num, ans in entry.items():
            item = QUESTIONS[int(q_num)]['item']
            scored[item] = CHOICE_TO_SCORE.get(ans, None)
        records.append(scored)
    return pd.DataFrame(records)

def compute_ctt_indices(df: pd.DataFrame, items: list) -> dict:
    """
    Compute Cronbach's alpha and item statistics for given items,
    but guard against zero total variance (e.g. only one response).
    """
    sub = df[items]
    total = sub.sum(axis=1)
    var_items = sub.var(ddof=1)
    var_total = total.var(ddof=1)

    # Safeguard: if total variance is zero or not enough respondents, skip alpha
    if var_total == 0 or len(df) < 2:
        alpha = None
        item_total_corr = {item: None for item in items}
    else:
        n = len(items)
        alpha = (n / (n - 1)) * (1 - var_items.sum() / var_total)
        item_total_corr = {item: sub[item].corr(total) for item in items}

    return {
        'alpha': alpha,
        'item_total_corr': item_total_corr,
        'item_means': sub.mean().to_dict(),
        'item_vars': var_items.to_dict()
    }


def run_ctt_analysis_from_raw(raw: list) -> dict:
    df = preprocess_raw_responses(raw)
    return {scale: compute_ctt_indices(df, items) for scale, items in SCALES.items()}
