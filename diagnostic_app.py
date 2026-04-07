"""
╔══════════════════════════════════════════════════════════════════════╗
║          DIAGNOSTIC EXPLORER — Streamlit MVP                        ║
║  Run:  streamlit run diagnostic_app.py                              ║
╚══════════════════════════════════════════════════════════════════════╝

SETUP
-----
pip install streamlit matplotlib
streamlit run diagnostic_app.py
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import time

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Diagnostic Explorer",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS  (minimal, clean)
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Remove default top padding */
    .block-container { padding-top: 2rem; max-width: 780px; }

    /* Zone card */
    .zone-card {
        background: #f8f8f6;
        border: 1px solid #e0dfd8;
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
    }

    /* Scene block (italic left-border) */
    .scene-block {
        background: #eef4fb;
        border-left: 3px solid #378ADD;
        border-radius: 0 8px 8px 0;
        padding: 0.75rem 1rem;
        color: #444;
        font-style: italic;
        margin-bottom: 1rem;
    }

    /* Zone tag pill */
    .zone-tag {
        display: inline-block;
        background: #e6f1fb;
        color: #185FA5;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 20px;
        letter-spacing: 0.04em;
        margin-bottom: 6px;
        text-transform: uppercase;
    }

    /* Hint box */
    .hint-box {
        background: #faeeda;
        border: 1px solid #FAC775;
        border-radius: 8px;
        padding: 0.65rem 1rem;
        font-size: 0.88rem;
        color: #633806;
        margin-top: 0.5rem;
    }

    /* Report metric */
    .metric-box {
        background: #f1efe8;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        text-align: center;
    }
    .metric-label { font-size: 0.72rem; color: #888; text-transform: uppercase; letter-spacing: 0.05em; }
    .metric-val   { font-size: 1.5rem; font-weight: 600; margin-top: 2px; }

    /* Report section items */
    .report-item { display: flex; gap: 8px; margin-bottom: 6px; font-size: 0.9rem; color: #444; }
    .dot { width: 8px; height: 8px; border-radius: 50%; margin-top: 5px; flex-shrink: 0; }
    .dot-green  { background: #3B6D11; }
    .dot-orange { background: #BA7517; }
    .dot-blue   { background: #185FA5; }

    /* Progress bar label */
    .prog-label { font-size: 0.78rem; color: #888; margin-top: -0.5rem; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  CONTENT DATA
# ═══════════════════════════════════════════════════════════════

SUBJECTS = {
    "Mathematics": {
        "icon": "∫",
        "zones": [
            {
                "tag": "Zone 1 of 5 — Limits",
                "title": "Getting infinitely close without arriving",
                "sub": "An intuition-first look at what a limit actually means",
                "scene": (
                    "You are walking toward a wall. Each step covers exactly half the remaining "
                    "gap — half, then half of that, then half again — forever."
                ),
                "question": (
                    "Will you ever actually reach the wall? "
                    "And what does that have to do with how calculus thinks about limits?"
                ),
                "hint": (
                    "Think about the total distance of all those steps added together — "
                    "is it a finite number or an infinite one?"
                ),
                "chips": [
                    "What does 'approaching a value' mean?",
                    "Is ½ + ¼ + ⅛ + … equal to 1, or less than 1?",
                    "Does a limit have to be 'reached' to exist?",
                ],
                "plot": "limit",
                "weak_flag": "limit_misconception",
            },
            {
                "tag": "Zone 2 of 5 — The Derivative",
                "title": "Speed at a single frozen instant",
                "sub": "What it means to have velocity at just one exact moment",
                "scene": (
                    "You have a graph of your position over time on a road trip — "
                    "not your speed, just where you are at each moment. The curve bends throughout."
                ),
                "question": (
                    "How would you figure out how fast you were going at exactly the 2-hour mark — "
                    "not over an interval, just at that one instant? What would you look at?"
                ),
                "hint": (
                    "Think about what happens when you zoom into a curve at one point "
                    "more and more closely."
                ),
                "chips": [
                    "What does the steepness of the graph tell you?",
                    "What is a tangent line in plain terms?",
                    "What happens to a curve when you zoom in far enough?",
                ],
                "plot": "derivative",
                "weak_flag": "derivative_intuition",
            },
            {
                "tag": "Zone 3 of 5 — Product Rule",
                "title": "Why you can't just multiply two rates",
                "sub": "The hidden interaction that simple multiplication misses",
                "scene": (
                    "A rectangle is growing — both its width and its height are "
                    "increasing at the same time."
                ),
                "question": (
                    "If width and height are both changing, the area changes too. "
                    "Why is the rate of change of area NOT simply (rate of width) × (rate of height)? "
                    "What is being missed?"
                ),
                "hint": (
                    "Draw the rectangle at two moments in time. "
                    "What new region of area appears that was not there before?"
                ),
                "chips": [
                    "Which part of the area depends only on width changing?",
                    "Which part depends only on height changing?",
                    "What tiny region involves BOTH changing at once?",
                ],
                "plot": "product_rule",
                "weak_flag": "product_rule_cross_term",
            },
            {
                "tag": "Zone 4 of 5 — Integration",
                "title": "Building total distance from speed",
                "sub": "What the area under a graph is physically measuring",
                "scene": (
                    "You have a graph of your car's speed over time. "
                    "The speed goes up and down — it is never constant. "
                    "You want to know the total distance travelled."
                ),
                "question": (
                    "You can't just do speed × time because the speed keeps changing. "
                    "How would you estimate total distance? "
                    "And what does each thin vertical strip of the graph represent, physically?"
                ),
                "hint": (
                    "Think of each thin strip as a tiny window of time where the speed "
                    "is almost constant — what is its area equal to?"
                ),
                "chips": [
                    "What is speed × a tiny bit of time equal to?",
                    "If you add up many tiny strips, what do you get?",
                    "Why does 'area' give a physical quantity like distance?",
                ],
                "plot": "integral",
                "weak_flag": "integral_area",
            },
            {
                "tag": "Zone 5 of 5 — Fundamental Theorem",
                "title": "Why differentiation and integration are mirror images",
                "sub": "The surprising bridge between two seemingly different ideas",
                "scene": (
                    "Differentiation breaks things into instantaneous rates. "
                    "Integration builds totals from those rates. "
                    "These sound like they should undo each other."
                ),
                "question": (
                    "Does that connection feel genuinely meaningful — or just like a coincidence? "
                    "Think about speed and position: if you differentiate position you get speed, "
                    "and if you integrate speed you get position back. Why does that work so neatly?"
                ),
                "hint": (
                    "Think about what 'accumulating all the tiny changes' and "
                    "'finding the rate of change' each do — are they really opposites?"
                ),
                "chips": [
                    "What does it mean to 'undo' a derivative?",
                    "If speed is the derivative of position, what is position relative to speed?",
                    "Is this always true or only in special cases?",
                ],
                "plot": "ftc",
                "weak_flag": "ftc_connection",
            },
        ],
        "report": {
            "level": "Medium",
            "strengths": [
                "Strong geometric intuition — tangent line and area reasoning come naturally",
                "Grasps the accumulation idea behind integration without prompting",
                "Correctly identifies the inverse relationship in the Fundamental Theorem",
            ],
            "gaps": [
                "Limit misconception: 'never reaching' confused with 'limit does not exist'",
                "Product rule interaction term — the cross-term Δf·Δg is often missed",
                "Precision gap: reasoning is directionally right but stops short of being airtight",
            ],
            "interventions": [
                "Draw ½+¼+⅛+… on a number line and mark where it lands exactly",
                "Expand (f+Δf)(g+Δg) algebraically and identify each of the four terms",
                "Try differentiating ∫₀ˣ f(t)dt for a concrete f — observe what you get",
            ],
        },
    },

    "Science": {
        "icon": "⚗",
        "zones": [
            {
                "tag": "Zone 1 of 5 — Inertia",
                "title": "Why things keep doing what they are doing",
                "sub": "Newton's first law without the textbook language",
                "scene": (
                    "You are on a perfectly frictionless ice rink. "
                    "You push a puck and let go. There is nothing pushing it after that."
                ),
                "question": (
                    "What happens to the puck? Does it need something to keep it moving, "
                    "or will it carry on by itself? What does that say about the natural state of motion?"
                ),
                "hint": "Think about what it would take to CHANGE the puck's motion — not what started it.",
                "chips": [
                    "What does 'inertia' mean in everyday terms?",
                    "What would eventually stop it in real life?",
                    "Why did Aristotle think things needed a push to keep moving?",
                ],
                "plot": "force",
                "weak_flag": "inertia",
            },
            {
                "tag": "Zone 2 of 5 — Energy",
                "title": "What is actually being exchanged on a roller coaster",
                "sub": "Potential and kinetic energy as two forms of the same thing",
                "scene": (
                    "A ball rolls down a hill, speeds up, then climbs another hill "
                    "and slows down. No engine, no fuel."
                ),
                "question": (
                    "Where is the ball getting its extra speed from when going downhill? "
                    "And where does that speed go when it climbs? "
                    "Something is converting — what is it and where does it live?"
                ),
                "hint": "Name what the ball 'has' at the top of a hill versus at the bottom.",
                "chips": [
                    "What is potential energy in plain terms?",
                    "Is the total amount of energy changing?",
                    "What happens if the second hill is taller than the first?",
                ],
                "plot": "energy",
                "weak_flag": "energy_conservation",
            },
            {
                "tag": "Zone 3 of 5 — Chemical Reactions",
                "title": "What really happens when something burns",
                "sub": "Atoms rearranging, not disappearing",
                "scene": (
                    "You burn a piece of wood. It turns to ash, smoke, and gases. "
                    "The solid seems to vanish — but did anything actually disappear?"
                ),
                "question": (
                    "Where did all the matter in the wood go? "
                    "And if nothing truly disappears, why does the ash weigh less than the original wood?"
                ),
                "hint": "Think about what is in the air around the fire — not just what remains on the ground.",
                "chips": [
                    "What does conservation of mass mean?",
                    "Where does the carbon in wood end up?",
                    "Why does burning require oxygen?",
                ],
                "plot": "chem",
                "weak_flag": "conservation_mass",
            },
            {
                "tag": "Zone 4 of 5 — Waves",
                "title": "Energy moving without matter moving",
                "sub": "What actually travels when a wave passes",
                "scene": (
                    "You drop a stone into still water. Ripples spread outward in rings. "
                    "A leaf floating 2 metres away starts bobbing up and down."
                ),
                "question": (
                    "Did any water travel from the stone to the leaf? "
                    "What actually travelled? "
                    "How is that different from rolling a ball across the surface?"
                ),
                "hint": "Watch one water molecule — does it drift toward the leaf, or just move up and down?",
                "chips": [
                    "What is the 'medium' of a wave?",
                    "How is a wave different from throwing an object?",
                    "What would a sound wave look like if you could see the air molecules?",
                ],
                "plot": "wave",
                "weak_flag": "wave_medium",
            },
            {
                "tag": "Zone 5 of 5 — Entropy",
                "title": "Why broken eggs never unbreak",
                "sub": "The direction of time and the idea of disorder",
                "scene": (
                    "You drop an egg. It shatters. You have never seen a shattered egg "
                    "spontaneously reassemble. But the fundamental laws of physics don't technically forbid it."
                ),
                "question": (
                    "If physics doesn't forbid it, why does it never happen? "
                    "What does this say about why natural processes tend to run in one direction?"
                ),
                "hint": "Think about how many different arrangements a broken egg has versus an intact one.",
                "chips": [
                    "What does entropy actually count or measure?",
                    "Why does disorder tend to win over time?",
                    "What does this have to do with heat flowing from hot to cold?",
                ],
                "plot": "entropy",
                "weak_flag": "entropy_microstates",
            },
        ],
        "report": {
            "level": "Medium",
            "strengths": [
                "Good intuition for conservation laws — mass and energy",
                "Grasps that waves transfer energy without bulk matter movement",
                "Correctly identifies inertia as the natural state, not rest",
            ],
            "gaps": [
                "Entropy often confused with energy loss rather than increase in microstates",
                "Potential energy location (field vs object) often unclear",
                "Reaction mechanism vs equilibrium sometimes conflated",
            ],
            "interventions": [
                "List all possible arrangements of 3 gas molecules in 2 halves of a box",
                "Track a single carbon atom through a combustion reaction start to finish",
                "Plot PE and KE of a pendulum across one full swing",
            ],
        },
    },

    "Business": {
        "icon": "↗",
        "zones": [
            {
                "tag": "Zone 1 of 5 — Supply & Demand",
                "title": "Why prices move without anyone deciding them",
                "sub": "The mechanism behind market prices",
                "scene": (
                    "Concert tickets are listed at ₹500. Fans are willing to pay ₹3,000. "
                    "Scalpers are selling for ₹2,500 outside the venue."
                ),
                "question": (
                    "Why did the original price not stay at ₹500 if people are clearly willing to pay more? "
                    "What force is pushing the price upward — and what would eventually stop it?"
                ),
                "hint": "Think about what happens when more people want something than there is of it available.",
                "chips": [
                    "What does a demand curve actually represent?",
                    "What would happen if tickets were unlimited?",
                    "At what point do buyers stop wanting to pay more?",
                ],
                "plot": "supply_demand",
                "weak_flag": "equilibrium",
            },
            {
                "tag": "Zone 2 of 5 — Profit & Cost",
                "title": "Why selling more doesn't always mean earning more",
                "sub": "The difference between revenue and profit",
                "scene": (
                    "A food stall sells 100 samosas at ₹20 each. Revenue: ₹2,000. "
                    "But the owner says she barely broke even."
                ),
                "question": (
                    "How is that possible? What kinds of costs might be eating into the revenue — "
                    "and which costs exist even if she sells zero samosas?"
                ),
                "hint": "Some costs change with how much you sell. Others do not. Which is which here?",
                "chips": [
                    "What is the difference between fixed and variable cost?",
                    "What is the break-even point?",
                    "If she doubles sales, will profit double too?",
                ],
                "plot": "profit",
                "weak_flag": "fixed_variable_cost",
            },
            {
                "tag": "Zone 3 of 5 — Competitive Advantage",
                "title": "Why some businesses always win and others always lose",
                "sub": "What makes a competitive edge durable",
                "scene": (
                    "Two coffee shops open side by side. One is always packed; the other is always empty. "
                    "The coffee quality is roughly the same and prices are similar."
                ),
                "question": (
                    "What could explain the difference? "
                    "And once a business has loyal customers, what makes them stay — "
                    "even if a cheaper option opens nearby?"
                ),
                "hint": "Think about what would make you personally keep going back to one shop even if a cheaper one opened.",
                "chips": [
                    "What is a switching cost in business?",
                    "What makes a brand valuable beyond the product?",
                    "Why can't a competitor just copy what the successful shop does?",
                ],
                "plot": "comp_adv",
                "weak_flag": "moat_durability",
            },
            {
                "tag": "Zone 4 of 5 — Risk & Return",
                "title": "Why riskier bets need to pay more",
                "sub": "The fundamental tradeoff in investing",
                "scene": (
                    "Bank A offers 4% guaranteed. "
                    "Bank B offers potentially 15% but you might lose everything. "
                    "Most people choose Bank A."
                ),
                "question": (
                    "If Bank B could give you 15%, why would anyone choose 4%? "
                    "And what would need to be true for someone to rationally choose Bank B?"
                ),
                "hint": "Think about what the word 'guaranteed' is actually worth when comparing the two options.",
                "chips": [
                    "What does 'risk premium' mean?",
                    "How does diversification reduce risk?",
                    "Why do government bonds pay less than corporate ones?",
                ],
                "plot": "risk_return",
                "weak_flag": "risk_premium",
            },
            {
                "tag": "Zone 5 of 5 — Incentives",
                "title": "Why people do exactly what you told them — and everything goes wrong",
                "sub": "How incentives shape behaviour and create unintended effects",
                "scene": (
                    "A factory is paid per unit produced. Workers start skipping quality checks "
                    "to hit targets faster. Defects rise. The company loses more money than it saved."
                ),
                "question": (
                    "The workers were doing exactly what they were rewarded for. "
                    "So why did things go wrong — and whose fault is it really? "
                    "What does this tell you about designing incentive systems?"
                ),
                "hint": "Think about whether the reward aligned with what the company actually WANTED — or only what it chose to measure.",
                "chips": [
                    "What is a principal-agent problem?",
                    "Give another real-world example of misaligned incentives.",
                    "How would you redesign the reward system here?",
                ],
                "plot": "incentives",
                "weak_flag": "incentive_alignment",
            },
        ],
        "report": {
            "level": "Medium",
            "strengths": [
                "Good grasp of supply-demand equilibrium mechanics",
                "Understands fixed vs variable cost distinction intuitively",
                "Correctly identifies that incentives drive behaviour — not intentions",
            ],
            "gaps": [
                "Risk premium often understood as punishment rather than rational compensation",
                "Competitive advantage confused with temporary differentiation",
                "Profit maximisation assumed but conditions rarely examined",
            ],
            "interventions": [
                "Draw a supply & demand diagram for concert tickets before and after a price cap",
                "Calculate break-even for the samosa stall with fixed costs of ₹800",
                "Design an incentive structure for the factory that aligns quality and quantity",
            ],
        },
    },
}


# ═══════════════════════════════════════════════════════════════
#  PLOT FUNCTIONS  (matplotlib, small and clean)
# ═══════════════════════════════════════════════════════════════

def make_fig(w=6, h=2.2):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor("#f8f8f6")
    ax.set_facecolor("#f8f8f6")
    for spine in ax.spines.values():
        spine.set_color("#d0cfc8")
    ax.tick_params(colors="#888", labelsize=8)
    return fig, ax


def plot_limit():
    fig, ax = make_fig()
    positions = [0, 0.5, 0.75, 0.875, 0.9375, 0.96875]
    sizes = [220, 160, 120, 90, 70, 55]
    colors = ["#378ADD"] * 5 + ["#185FA5"]
    ax.scatter(positions, [0]*len(positions), s=sizes, c=colors, alpha=0.75, zorder=3)
    ax.axvline(1.0, color="#E24B4A", lw=2, label="Wall (limit = 1)")
    for i in range(len(positions)-1):
        ax.annotate("", xy=(positions[i+1], 0), xytext=(positions[i], 0),
                    arrowprops=dict(arrowstyle="->", color="#888", lw=0.8))
    ax.set_xlim(-0.05, 1.12)
    ax.set_ylim(-0.5, 0.5)
    ax.set_yticks([])
    ax.set_xlabel("Distance covered (out of 1)", fontsize=8, color="#666")
    ax.legend(fontsize=8, framealpha=0)
    ax.set_title("Each step halves the gap — total converges to exactly 1", fontsize=9, color="#444", pad=6)
    plt.tight_layout()
    return fig


def plot_derivative():
    fig, ax = make_fig(h=2.6)
    x = np.linspace(0, 4, 200)
    y = 0.5*x**2 + np.sin(x)
    ax.plot(x, y, color="#378ADD", lw=2, label="Position f(x)")
    # tangent at x=2
    x0 = 2.0
    y0 = 0.5*x0**2 + np.sin(x0)
    slope = x0 + np.cos(x0)
    tx = np.linspace(x0-0.8, x0+0.8, 50)
    ty = y0 + slope*(tx - x0)
    ax.plot(tx, ty, color="#E24B4A", lw=1.5, linestyle="--", label=f"Tangent at t=2 (slope≈{slope:.2f})")
    ax.scatter([x0], [y0], color="#E24B4A", s=60, zorder=5)
    ax.axvline(x0, color="#aaa", lw=0.7, linestyle=":")
    ax.set_xlabel("Time (hrs)", fontsize=8, color="#666")
    ax.set_ylabel("Position", fontsize=8, color="#666")
    ax.legend(fontsize=8, framealpha=0)
    ax.set_title("The slope of the tangent line = instantaneous speed", fontsize=9, color="#444", pad=6)
    plt.tight_layout()
    return fig


def plot_product_rule():
    fig, ax = make_fig(h=3.0)
    f, g, df, dg = 3, 2, 0.6, 0.4
    # Original rectangle
    rect_orig = plt.Rectangle((0, 0), f, g, color="#B5D4F4", ec="#378ADD", lw=1, label="f·g (original area)")
    ax.add_patch(rect_orig)
    # df strip (right)
    rect_df = plt.Rectangle((f, 0), df, g, color="#FAC775", ec="#BA7517", lw=1, label="g·Δf")
    ax.add_patch(rect_df)
    # dg strip (top)
    rect_dg = plt.Rectangle((0, g), f, dg, color="#9FE1CB", ec="#1D9E75", lw=1, label="f·Δg")
    ax.add_patch(rect_dg)
    # corner
    rect_corner = plt.Rectangle((f, g), df, dg, color="#F09595", ec="#E24B4A", lw=1, label="Δf·Δg (tiny)")
    ax.add_patch(rect_corner)
    ax.set_xlim(-0.1, f+df+0.2)
    ax.set_ylim(-0.1, g+dg+0.3)
    ax.set_aspect("equal")
    ax.set_xlabel("Width (f)", fontsize=8, color="#666")
    ax.set_ylabel("Height (g)", fontsize=8, color="#666")
    ax.set_title("Product rule: all four regions count", fontsize=9, color="#444", pad=6)
    ax.legend(fontsize=8, loc="upper left", framealpha=0)
    plt.tight_layout()
    return fig


def plot_integral():
    fig, ax = make_fig(h=2.6)
    x = np.linspace(0, 5, 300)
    speed = 20 + 10*np.sin(x) + 5*np.cos(2*x)
    ax.fill_between(x, speed, alpha=0.25, color="#378ADD", label="Area = total distance")
    ax.plot(x, speed, color="#378ADD", lw=2)
    # show a few strips
    for xi in np.linspace(0.5, 4.5, 8):
        yi = 20 + 10*np.sin(xi) + 5*np.cos(2*xi)
        ax.bar(xi, yi, width=0.25, alpha=0.5, color="#E24B4A", ec="#A32D2D")
    ax.set_xlabel("Time (s)", fontsize=8, color="#666")
    ax.set_ylabel("Speed (km/h)", fontsize=8, color="#666")
    ax.legend(fontsize=8, framealpha=0)
    ax.set_title("Each strip = speed × tiny time = tiny distance", fontsize=9, color="#444", pad=6)
    plt.tight_layout()
    return fig


def plot_ftc():
    fig, ax = make_fig(h=2.2)
    ax.axis("off")
    # Two boxes with arrows
    box_style = dict(boxstyle="round,pad=0.5", facecolor="#e6f1fb", edgecolor="#378ADD", lw=1.2)
    ax.text(0.18, 0.5, "Position\nf(x)", transform=ax.transAxes, ha="center", va="center",
            fontsize=11, fontweight="bold", color="#185FA5", bbox=box_style)
    box_style2 = dict(boxstyle="round,pad=0.5", facecolor="#eaf3de", edgecolor="#3B6D11", lw=1.2)
    ax.text(0.82, 0.5, "Speed\nf′(x)", transform=ax.transAxes, ha="center", va="center",
            fontsize=11, fontweight="bold", color="#27500A", bbox=box_style2)
    ax.annotate("differentiate →", xy=(0.65, 0.65), xytext=(0.35, 0.65),
                xycoords="axes fraction", fontsize=9, color="#185FA5",
                arrowprops=dict(arrowstyle="->", color="#185FA5", lw=1.2))
    ax.annotate("← integrate", xy=(0.35, 0.35), xytext=(0.65, 0.35),
                xycoords="axes fraction", fontsize=9, color="#3B6D11",
                arrowprops=dict(arrowstyle="->", color="#3B6D11", lw=1.2))
    ax.set_title("They undo each other — the Fundamental Theorem", fontsize=9, color="#444", pad=6)
    plt.tight_layout()
    return fig


def plot_force():
    fig, ax = make_fig()
    xs = [0.5, 2.0, 3.5]
    for i, x in enumerate(xs):
        circle = plt.Circle((x, 0), 0.18, color="#378ADD", alpha=0.8-i*0.2)
        ax.add_patch(circle)
        if i < len(xs)-1:
            ax.annotate("", xy=(xs[i+1]-0.18, 0), xytext=(x+0.18, 0),
                        arrowprops=dict(arrowstyle="->", color="#888", lw=1))
    ax.set_xlim(0, 4.5); ax.set_ylim(-0.5, 0.5)
    ax.set_yticks([]); ax.set_xticks([])
    ax.set_title("No friction → puck keeps moving forever (Newton's 1st law)", fontsize=9, color="#444", pad=6)
    plt.tight_layout()
    return fig


def plot_energy():
    fig, ax = make_fig(h=2.6)
    x = np.linspace(0, 2*np.pi, 300)
    hill = np.sin(x) + 0.5
    ax.plot(x, hill, color="#888", lw=2, label="Hill profile")
    ax.fill_between(x, hill, alpha=0.08, color="#888")
    # KE & PE curves (complementary)
    ke = 1 - hill/max(hill)
    pe = hill/max(hill)
    ax.plot(x, ke, color="#3B6D11", lw=1.5, linestyle="--", label="KE (speed)")
    ax.plot(x, pe, color="#BA7517", lw=1.5, linestyle="--", label="PE (height)")
    ax.set_xticks([]); ax.set_ylabel("Energy / Height", fontsize=8, color="#666")
    ax.legend(fontsize=8, framealpha=0)
    ax.set_title("PE converts to KE and back — total stays constant", fontsize=9, color="#444", pad=6)
    plt.tight_layout()
    return fig


def plot_chem():
    fig, ax = make_fig(h=2.0)
    ax.axis("off")
    items = [("C + H", 0.12, "#FAC775", "#633806"), ("+  O₂", 0.38, "#F09595", "#791F1F"),
             ("→", 0.58, "#ddd", "#555"), ("CO₂ + H₂O", 0.82, "#B5D4F4", "#0C447C")]
    for label, x, fc, tc_ in items:
        if label != "→":
            ax.text(x, 0.5, label, transform=ax.transAxes, ha="center", va="center",
                    fontsize=13, fontweight="bold", color=tc_,
                    bbox=dict(boxstyle="round,pad=0.4", facecolor=fc, edgecolor=tc_, lw=0.8))
        else:
            ax.text(x, 0.5, label, transform=ax.transAxes, ha="center", va="center",
                    fontsize=18, color="#888")
    ax.set_title("Same atoms — rearranged into different molecules", fontsize=9, color="#444", pad=6)
    plt.tight_layout()
    return fig


def plot_wave():
    fig, ax = make_fig(h=2.4)
    x = np.linspace(0, 4*np.pi, 400)
    y = np.sin(x)
    ax.plot(x, y, color="#378ADD", lw=2, label="Wave (energy travels →)")
    # Static molecule markers
    for xi in [np.pi/2, 3*np.pi/2, 5*np.pi/2, 7*np.pi/2]:
        ax.scatter([xi], [np.sin(xi)], color="#E24B4A", s=60, zorder=5)
        ax.annotate("", xy=(xi, np.sin(xi)-0.3), xytext=(xi, np.sin(xi)),
                    arrowprops=dict(arrowstyle="<->", color="#E24B4A", lw=1))
    ax.axhline(0, color="#aaa", lw=0.5, linestyle=":")
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("Molecules bob up/down — only energy moves sideways", fontsize=9, color="#444", pad=6)
    ax.legend(fontsize=8, framealpha=0)
    plt.tight_layout()
    return fig


def plot_entropy():
    fig, axes = plt.subplots(1, 2, figsize=(6, 2.2))
    fig.patch.set_facecolor("#f8f8f6")
    for a in axes:
        a.set_facecolor("#eaf3de")
        for sp in a.spines.values(): sp.set_color("#d0cfc8")
    # Ordered
    axes[0].scatter([0.5]*3, [0.3, 0.5, 0.7], s=120, c="#3B6D11", alpha=0.8)
    axes[0].set_title("1 tidy arrangement", fontsize=8, color="#27500A")
    axes[0].set_xlim(0, 1); axes[0].set_ylim(0, 1); axes[0].axis("off")
    # Disordered
    np.random.seed(42)
    xs = np.random.uniform(0.05, 0.95, 18)
    ys = np.random.uniform(0.05, 0.95, 18)
    axes[1].set_facecolor("#fcebeb")
    axes[1].scatter(xs, ys, s=60, c="#E24B4A", alpha=0.7)
    axes[1].set_title("Millions of disordered arrangements", fontsize=8, color="#791F1F")
    axes[1].set_xlim(0, 1); axes[1].set_ylim(0, 1); axes[1].axis("off")
    fig.suptitle("Disorder wins because it has far more possible states", fontsize=9, color="#444", y=1.02)
    plt.tight_layout()
    return fig


def plot_supply_demand():
    fig, ax = make_fig(h=2.6)
    q = np.linspace(0, 10, 200)
    demand = 10 - q
    supply = 1 + 0.9*q
    ax.plot(q, demand, color="#E24B4A", lw=2, label="Demand")
    ax.plot(q, supply, color="#3B6D11", lw=2, label="Supply")
    eq_q = (10-1)/(1+0.9)
    eq_p = 1 + 0.9*eq_q
    ax.scatter([eq_q], [eq_p], color="#185FA5", s=80, zorder=5, label=f"Equilibrium ≈ ₹{eq_p:.0f}")
    ax.axvline(eq_q, color="#aaa", lw=0.7, linestyle=":")
    ax.axhline(eq_p, color="#aaa", lw=0.7, linestyle=":")
    ax.set_xlabel("Quantity", fontsize=8, color="#666")
    ax.set_ylabel("Price", fontsize=8, color="#666")
    ax.legend(fontsize=8, framealpha=0)
    ax.set_title("Price moves until quantity demanded = quantity supplied", fontsize=9, color="#444", pad=6)
    plt.tight_layout()
    return fig


def plot_profit():
    fig, ax = make_fig(h=2.6)
    units = np.linspace(0, 150, 300)
    revenue = 20 * units
    fixed = 800
    variable = 10 * units
    total_cost = fixed + variable
    ax.plot(units, revenue, color="#3B6D11", lw=2, label="Revenue (₹20/unit)")
    ax.plot(units, total_cost, color="#E24B4A", lw=2, label="Total cost (fixed + variable)")
    ax.axhline(fixed, color="#BA7517", lw=1.2, linestyle="--", label=f"Fixed cost = ₹{fixed}")
    bep = fixed / (20 - 10)
    ax.axvline(bep, color="#185FA5", lw=1, linestyle=":", label=f"Break-even = {bep:.0f} units")
    ax.set_xlabel("Units sold", fontsize=8, color="#666")
    ax.set_ylabel("₹", fontsize=8, color="#666")
    ax.legend(fontsize=8, framealpha=0)
    ax.set_title("Revenue crosses total cost at the break-even point", fontsize=9, color="#444", pad=6)
    plt.tight_layout()
    return fig


def plot_comp_adv():
    fig, ax = make_fig(h=2.2)
    ax.axis("off")
    labels = ["Brand\nrecognition", "Location\nadvantage", "Loyalty\n& switching costs"]
    colors = ["#e6f1fb", "#eaf3de", "#faeeda"]
    edges  = ["#185FA5", "#27500A", "#633806"]
    texts  = ["#185FA5", "#27500A", "#633806"]
    for i, (lbl, fc, ec, tc_) in enumerate(zip(labels, colors, edges, texts)):
        ax.text(0.18 + i*0.32, 0.5, lbl, transform=ax.transAxes, ha="center", va="center",
                fontsize=10, fontweight="bold", color=tc_,
                bbox=dict(boxstyle="round,pad=0.5", facecolor=fc, edgecolor=ec, lw=1))
    ax.set_title("The 'moat' — why loyal customers do not leave", fontsize=9, color="#444", pad=6)
    plt.tight_layout()
    return fig


def plot_risk_return():
    fig, ax = make_fig(h=2.6)
    risks   = [0.5, 3.0,  8.0]
    returns = [4.0, 8.0, 15.0]
    labels  = ["Bank A\n(safe)", "Balanced\nfund", "Bank B\n(risky)"]
    colors  = ["#3B6D11", "#185FA5", "#E24B4A"]
    ax.plot([0, 10], [2, 17], color="#ccc", lw=1, linestyle="--", label="Risk-return line")
    for r, ret, lbl, c in zip(risks, returns, labels, colors):
        ax.scatter([r], [ret], s=120, color=c, zorder=5)
        ax.annotate(lbl, (r, ret), textcoords="offset points", xytext=(6, 4), fontsize=8, color=c)
    ax.set_xlabel("Risk level", fontsize=8, color="#666")
    ax.set_ylabel("Expected return (%)", fontsize=8, color="#666")
    ax.set_title("Higher risk → higher required return", fontsize=9, color="#444", pad=6)
    plt.tight_layout()
    return fig


def plot_incentives():
    fig, ax = make_fig(h=2.4)
    ax.axis("off")
    steps = [("Goal:\nmore units", "#e6f1fb", "#185FA5"),
             ("Workers skip\nquality checks", "#faeeda", "#633806"),
             ("Defects\nrise", "#fcebeb", "#791F1F"),
             ("Company\nloses money", "#fcebeb", "#A32D2D")]
    for i, (lbl, fc, tc_) in enumerate(steps):
        ax.text(0.1 + i*0.26, 0.5, lbl, transform=ax.transAxes, ha="center", va="center",
                fontsize=9, fontweight="bold", color=tc_,
                bbox=dict(boxstyle="round,pad=0.4", facecolor=fc, edgecolor=tc_, lw=0.9))
        if i < len(steps)-1:
            ax.annotate("", xy=(0.1+(i+1)*0.26-0.07, 0.5), xytext=(0.1+i*0.26+0.08, 0.5),
                        xycoords="axes fraction",
                        arrowprops=dict(arrowstyle="->", color="#aaa", lw=1.2))
    ax.set_title("Rewarding the wrong metric produces the wrong result", fontsize=9, color="#444", pad=6)
    plt.tight_layout()
    return fig


PLOT_FNS = {
    "limit": plot_limit, "derivative": plot_derivative, "product_rule": plot_product_rule,
    "integral": plot_integral, "ftc": plot_ftc,
    "force": plot_force, "energy": plot_energy, "chem": plot_chem,
    "wave": plot_wave, "entropy": plot_entropy,
    "supply_demand": plot_supply_demand, "profit": plot_profit,
    "comp_adv": plot_comp_adv, "risk_return": plot_risk_return, "incentives": plot_incentives,
}


# ═══════════════════════════════════════════════════════════════
#  SIMULATED ADAPTIVITY
#  — simple keyword scan to flag weak understanding
# ═══════════════════════════════════════════════════════════════

WEAK_SIGNALS = {
    "limit_misconception": [
        "never reach", "can't reach", "doesn't reach", "won't reach", "impossible"
    ],
    "derivative_intuition": [
        "average", "total", "area", "i'm not sure", "i don't know"
    ],
    "product_rule_cross_term": [
        "just multiply", "multiply them", "multiply both", "simple", "easy"
    ],
    "integral_area": [
        "speed times time", "not sure why", "don't know why area"
    ],
    "ftc_connection": [
        "coincidence", "not sure", "i guess", "seems random", "i don't understand why"
    ],
    "inertia": ["needs a push", "needs force", "something pushes"],
    "energy_conservation": ["energy disappears", "energy is lost", "energy destroyed"],
    "conservation_mass": ["matter disappears", "wood disappears", "mass is lost"],
    "wave_medium": ["water travels", "water moves sideways", "water moves forward"],
    "entropy_microstates": ["energy loss", "energy used up", "gets tired"],
    "equilibrium": ["seller decides", "government sets", "company decides price"],
    "fixed_variable_cost": ["all costs are the same", "cost per item is fixed"],
    "moat_durability": ["just copy", "anyone can copy", "same thing"],
    "risk_premium": ["punishment", "bank is greedy", "unfair"],
    "incentive_alignment": ["workers fault", "lazy workers", "bad employees"],
}


def detect_weakness(answer: str, flag: str) -> bool:
    answer_l = answer.lower()
    signals = WEAK_SIGNALS.get(flag, [])
    return any(sig in answer_l for sig in signals)


def adaptive_followup(zone: dict, answer: str) -> str | None:
    """Return a follow-up nudge if a misconception is detected, else None."""
    if detect_weakness(answer, zone["weak_flag"]):
        NUDGES = {
            "limit_misconception": (
                "Interesting — you mentioned not reaching the wall. "
                "Here's a nudge: mathematically, the *sum* ½+¼+⅛+… is **exactly 1**, "
                "not 'almost 1'. So the limit isn't a destination you approach but miss — "
                "it's the precise value the process equals. Does that shift your thinking?"
            ),
            "derivative_intuition": (
                "You seem to be thinking about averages. "
                "The derivative is different — it's the slope of the *tangent line* at one exact point, "
                "not an average over an interval. Try imagining zooming in more and more on the curve."
            ),
            "product_rule_cross_term": (
                "The 'just multiply' instinct is natural — but think about the rectangle diagram. "
                "When BOTH sides grow, a tiny corner piece (Δf·Δg) appears. Simple multiplication forgets that corner."
            ),
            "integral_area": (
                "Speed × time = distance — you know that for constant speed. "
                "Each strip is exactly that: a tiny speed × a tiny time = a tiny distance. "
                "Adding all the tiny distances gives total distance. That's why area works!"
            ),
            "ftc_connection": (
                "It might feel like coincidence, but think about position and speed: "
                "speed *is* how position changes. If you accumulate all those speed values over time, "
                "you rebuild the position. That's not a coincidence — it's the definition."
            ),
        }
        return NUDGES.get(zone["weak_flag"])
    return None


# ═══════════════════════════════════════════════════════════════
#  SESSION STATE INIT
# ═══════════════════════════════════════════════════════════════

def init_state():
    defaults = {
        "screen": "welcome",      # welcome | zone | report
        "subject": None,
        "topic": "",
        "confidence": "Medium",
        "zone_idx": 0,
        "answers": [],            # list of answer strings
        "followups": [],          # list of followup strings or None
        "show_hint": False,
        "chip_pressed": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════

def go(screen):
    st.session_state.screen = screen
    st.session_state.show_hint = False
    st.session_state.chip_pressed = None
    st.rerun()

def current_zones():
    return SUBJECTS[st.session_state.subject]["zones"]

def current_zone():
    return current_zones()[st.session_state.zone_idx]

def progress_bar_html(idx, total):
    dots = []
    for i in range(total):
        if i < idx:
            dots.append('<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#3B6D11;margin:0 3px"></span>')
        elif i == idx:
            dots.append('<span style="display:inline-block;width:24px;height:10px;border-radius:5px;background:#378ADD;margin:0 3px"></span>')
        else:
            dots.append('<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#d0cfd8;margin:0 3px"></span>')
    return "".join(dots) + f'<span style="font-size:0.78rem;color:#888;margin-left:8px">Zone {idx+1} of {total}</span>'


# ═══════════════════════════════════════════════════════════════
#  SCREEN 1 — WELCOME / INPUT
# ═══════════════════════════════════════════════════════════════

def render_welcome():
    st.markdown("## 🧠 Diagnostic Explorer")
    st.markdown(
        "<p style='color:#888;font-size:0.9rem;margin-top:-0.5rem'>"
        "~10–15 min &nbsp;·&nbsp; conversation-style &nbsp;·&nbsp; no grades</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    # Subject picker
    st.markdown("**Choose your subject**")
    col1, col2, col3 = st.columns(3)
    subj_map = {"Mathematics": "col1", "Science": "col2", "Business": "col3"}
    selected = st.session_state.subject
    with col1:
        if st.button("∫  Mathematics\nCalculus · Algebra · Stats",
                     use_container_width=True,
                     type="primary" if selected == "Mathematics" else "secondary"):
            st.session_state.subject = "Mathematics"
            st.rerun()
    with col2:
        if st.button("⚗  Science\nPhysics · Chemistry · Bio",
                     use_container_width=True,
                     type="primary" if selected == "Science" else "secondary"):
            st.session_state.subject = "Science"
            st.rerun()
    with col3:
        if st.button("↗  Business\nEcon · Finance · Strategy",
                     use_container_width=True,
                     type="primary" if selected == "Business" else "secondary"):
            st.session_state.subject = "Business"
            st.rerun()

    st.markdown("")

    # Topic input
    topic = st.text_input(
        "Topic within the subject",
        value=st.session_state.topic,
        placeholder="e.g. Limits, Newton's laws, Supply & demand…",
    )
    st.session_state.topic = topic

    # Confidence
    conf = st.radio(
        "How confident do you feel?",
        ["Low — just starting out", "Medium — some idea", "High — pretty solid"],
        index=1,
        horizontal=True,
    )
    st.session_state.confidence = conf.split(" — ")[0]

    st.markdown("")
    ready = bool(st.session_state.subject) and bool(topic.strip())
    if st.button("Begin exploration →", type="primary", disabled=not ready, use_container_width=True):
        st.session_state.zone_idx = 0
        st.session_state.answers = []
        st.session_state.followups = []
        go("zone")


# ═══════════════════════════════════════════════════════════════
#  SCREEN 2 — ZONE (question flow)
# ═══════════════════════════════════════════════════════════════

def render_zone():
    zones = current_zones()
    idx   = st.session_state.zone_idx
    zone  = current_zone()
    total = len(zones)

    # Progress bar
    st.markdown(
        progress_bar_html(idx, total),
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='prog-label'>{st.session_state.subject} · {st.session_state.topic}</div>",
        unsafe_allow_html=True,
    )

    # Zone card header
    st.markdown(
        f"""
        <div class='zone-card'>
          <div class='zone-tag'>{zone['tag']}</div>
          <h3 style='margin:2px 0 2px;font-size:1.1rem'>{zone['title']}</h3>
          <p style='color:#888;font-size:0.88rem;margin:0'>{zone['sub']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Visual
    plot_fn = PLOT_FNS.get(zone["plot"])
    if plot_fn:
        fig = plot_fn()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    # Scene + Question
    st.markdown(
        f"<div class='scene-block'>{zone['scene']}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(f"**{zone['question']}**")

    # Probe chips (quick-select prompts)
    st.markdown("<p style='font-size:0.82rem;color:#aaa;margin-bottom:4px'>Explore deeper:</p>",
                unsafe_allow_html=True)
    chip_cols = st.columns(len(zone["chips"]))
    for i, (col, chip) in enumerate(zip(chip_cols, zone["chips"])):
        with col:
            if st.button(chip, key=f"chip_{idx}_{i}", use_container_width=True):
                st.session_state.chip_pressed = chip

    if st.session_state.chip_pressed:
        st.info(f"💬 Thinking prompt: *{st.session_state.chip_pressed}*")

    st.markdown("")

    # Hint toggle
    col_h, _ = st.columns([1, 3])
    with col_h:
        if st.button("💡 Peek at a clue", key=f"hint_{idx}"):
            st.session_state.show_hint = not st.session_state.show_hint

    if st.session_state.show_hint:
        st.markdown(
            f"<div class='hint-box'>💡 {zone['hint']}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("")
    st.divider()

    # Answer text area
    answer_key = f"answer_{idx}"
    answer = st.text_area(
        "Share your thinking here — explain your reasoning:",
        key=answer_key,
        height=120,
        placeholder="Type as much or as little as you like. The 'why' matters more than the 'what'.",
    )

    # --- Show adaptive follow-up if answer already submitted for this zone ---
    if idx < len(st.session_state.answers):
        prev_answer = st.session_state.answers[idx]
        prev_fu = st.session_state.followups[idx] if idx < len(st.session_state.followups) else None
        if prev_fu:
            st.markdown("---")
            st.markdown("**A small nudge based on your answer:**")
            st.warning(prev_fu)

    # Navigation buttons
    col_l, col_r = st.columns([1, 1])
    with col_l:
        if idx > 0:
            if st.button("← Previous zone", use_container_width=True):
                st.session_state.zone_idx -= 1
                st.session_state.show_hint = False
                st.session_state.chip_pressed = None
                st.rerun()

    with col_r:
        is_last = (idx == total - 1)
        next_label = "See my report →" if is_last else "Next zone →"

        if st.button(next_label, type="primary", use_container_width=True):
            # Save answer
            if idx >= len(st.session_state.answers):
                st.session_state.answers.append(answer)
                # Run adaptive check
                fu = adaptive_followup(zone, answer) if answer.strip() else None
                st.session_state.followups.append(fu)
            else:
                st.session_state.answers[idx] = answer
                fu = adaptive_followup(zone, answer) if answer.strip() else None
                if idx < len(st.session_state.followups):
                    st.session_state.followups[idx] = fu
                else:
                    st.session_state.followups.append(fu)

            if is_last:
                go("report")
            else:
                st.session_state.zone_idx += 1
                st.session_state.show_hint = False
                st.session_state.chip_pressed = None
                st.rerun()


# ═══════════════════════════════════════════════════════════════
#  SCREEN 3 — REPORT
# ═══════════════════════════════════════════════════════════════

def render_report():
    subj_data = SUBJECTS[st.session_state.subject]
    report    = subj_data["report"]
    zones     = subj_data["zones"]
    answers   = st.session_state.answers
    followups = st.session_state.followups

    # Detect actual weaknesses from answers
    detected_gaps = []
    for i, zone in enumerate(zones):
        ans = answers[i] if i < len(answers) else ""
        if detect_weakness(ans, zone["weak_flag"]):
            detected_gaps.append(zone["title"])

    level = "Low" if len(detected_gaps) >= 3 else ("High" if len(detected_gaps) == 0 else "Medium")
    misc_count = len(detected_gaps)

    # Header
    st.markdown("## 📋 Diagnostic Report")
    st.markdown(
        f"<p style='color:#888;font-size:0.9rem'>"
        f"{st.session_state.subject} &nbsp;·&nbsp; {st.session_state.topic} &nbsp;·&nbsp; "
        f"{st.session_state.confidence} confidence</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    # Metric cards
    level_color = {"Low": "#E24B4A", "Medium": "#BA7517", "High": "#3B6D11"}[level]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"<div class='metric-box'><div class='metric-label'>Overall level</div>"
            f"<div class='metric-val' style='color:{level_color}'>{level}</div></div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"<div class='metric-box'><div class='metric-label'>Zones completed</div>"
            f"<div class='metric-val' style='color:#185FA5'>{len(answers)} / {len(zones)}</div></div>",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"<div class='metric-box'><div class='metric-label'>Misconceptions flagged</div>"
            f"<div class='metric-val' style='color:#E24B4A'>{misc_count}</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("")

    # Strengths
    st.markdown("#### ✅ Strengths detected")
    for s in report["strengths"]:
        st.markdown(
            f"<div class='report-item'><div class='dot dot-green'></div><div>{s}</div></div>",
            unsafe_allow_html=True,
        )

    # Gaps (use detected ones if any, fallback to defaults)
    st.markdown("#### ⚠️ Conceptual gaps")
    gap_items = [f"Weak conceptual grasp detected in: **{g}**" for g in detected_gaps] if detected_gaps else report["gaps"]
    for g in gap_items:
        st.markdown(
            f"<div class='report-item'><div class='dot dot-orange'></div><div>{g}</div></div>",
            unsafe_allow_html=True,
        )

    # Suggested exercises
    st.markdown("#### 📚 Suggested next steps")
    for ex in report["interventions"]:
        st.markdown(
            f"<div class='report-item'><div class='dot dot-blue'></div><div>{ex}</div></div>",
            unsafe_allow_html=True,
        )

    st.divider()

    # Per-zone answer review
    with st.expander("Review your answers zone by zone"):
        for i, zone in enumerate(zones):
            st.markdown(f"**{zone['tag']} — {zone['title']}**")
            ans = answers[i] if i < len(answers) else "_No answer recorded_"
            st.markdown(f"> {ans}" if ans else "_No answer recorded_")
            fu = followups[i] if i < len(followups) else None
            if fu:
                st.warning(f"Adaptive nudge: {fu}")
            st.markdown("")

    st.divider()

    # Restart
    col_a, col_b = st.columns([1, 1])
    with col_a:
        if st.button("← Back to zones", use_container_width=True):
            go("zone")
    with col_b:
        if st.button("Start a new session", type="primary", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# ═══════════════════════════════════════════════════════════════
#  ROUTER
# ═══════════════════════════════════════════════════════════════

screen = st.session_state.screen

if screen == "welcome":
    render_welcome()
elif screen == "zone":
    render_zone()
elif screen == "report":
    render_report()
