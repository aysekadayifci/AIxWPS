"""Self-contained HTML report (inline SVG charts), CSV, JSON. Standard library only."""
import csv
import html
import json
from pathlib import Path

METRICS = {'access':'Humanitarian access','trust':'Community trust', 'participation':"Women's participation",'security':'Civilian security','exclusion':'Digital exclusion','privacy':'Data privacy','tension':'Political tension'}
GROUPS = {'undocumented_women':'Undocumented women','camp_residents':'Camp residents','host_community':'Host community'}
GROUP_MEANINGS = {'undocumented_women': 'Illustrative access to assistance, documentation barriers and protection from exploitation.', 'camp_residents': 'Overall modeled conditions for displaced residents, including essential services and protection.', 'host_community': 'Modeled conditions for surrounding communities, including shared resources, livelihoods and social cohesion.'}
GROUP_NOTE = 'These are fictional 0–100 human security proxies, not population counts, percentages, or measured outcomes. Higher scores indicate more favorable modeled conditions. Groups overlap: undocumented women may be camp residents; the host community lives primarily outside the camp. Scores are not additive or a calculated population average.'
GROUP_REFLECTION = 'Who benefits, who bears the costs, and who is left behind? Aggregate humanitarian access can improve while marginalized groups face worsening conditions.'
INITIAL = {'access':45,'trust':50,'participation':35,'security':55,'exclusion':45,'privacy':60,'tension':40}
INITIAL_GROUPS = {'undocumented_women':45,'camp_residents':50,'host_community':50}
INTERPRETATION = {
 'access': 'Relief and recovery: aggregate humanitarian service access. This does not measure equal distribution.',
 'trust': 'Community confidence and legitimacy: cooperation may become harder when trust declines.',
 'participation': 'Participation: this proxy does not separately measure consultation, influence, or formal decision authority.',
 'security': 'Protection and prevention: a higher score represents the scenario’s modeled security conditions, not observed casualty counts.',
 'exclusion': 'Protection and relief: higher digital exclusion indicates greater barriers to accessing digital services.',
 'privacy': 'Protection: data safeguards and exposure to misuse; a proxy, not a legal compliance assessment.',
 'tension': 'Prevention: higher political tension indicates greater risk of conflict escalation in this scenario.'
}

def svg_chart(title, series, names):
    w, h, left, right, top, bottom = 790, 250, 56, 25, 36, 42
    pw, ph = w-left-right, h-top-bottom
    parts = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(title)}" xmlns="http://www.w3.org/2000/svg">',f'<text x="{left}" y="20" font-size="16" font-weight="bold">{html.escape(title)}</text>']
    for val in (0,25,50,75,100):
        y=top+ph*(1-val/100)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{w-right}" y2="{y:.1f}" stroke="#dce3eb"/><text x="{left-10}" y="{y+4:.1f}" font-size="11" text-anchor="end" fill="#596777">{val}</text>')
    count=len(next(iter(series.values())))
    for i in range(count):
        x=left+pw*i/max(1,count-1)
        parts.append(f'<text x="{x:.1f}" y="{h-14}" font-size="11" text-anchor="middle" fill="#596777">{("Start" if i==0 else "R"+str(i))}</text>')
    palette=['#007c91','#d97706','#7654aa','#2e8b57','#c04a6b','#536fb1','#ad563f']
    for j,(key,values) in enumerate(series.items()):
        color=palette[j%len(palette)]
        coords=' '.join(f'{left+pw*i/max(1,count-1):.1f},{top+ph*(1-v/100):.1f}' for i,v in enumerate(values))
        parts.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round"/>')
        for i,v in enumerate(values):
            x=left+pw*i/max(1,count-1); y=top+ph*(1-v/100)
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{color}"><title>{html.escape(names[key])}: {v}</title></circle>')
    parts.append('</svg>')
    legend=''.join(f'<span class="legend"><span class="swatch" style="background:{palette[i%len(palette)]}"></span>{html.escape(names[k])}</span>' for i,k in enumerate(series))
    return '<div class="chart">'+''.join(parts)+'<div class="legends">'+legend+'</div></div>'

def direction(key, delta):
    if delta == 0: return 'unchanged'
    positive=(delta<0 if key in ('exclusion','tension') else delta>0)
    return 'improved' if positive else 'worsened'

def export_report(game, folder='reports'):
    if len(game.history)!=6:
        raise ValueError('Complete all six rounds before exporting the final report.')
    folder=Path(folder).expanduser().resolve(); folder.mkdir(parents=True, exist_ok=True)
    timeline=[INITIAL]+[r['metrics'] for r in game.history]
    populations=[INITIAL_GROUPS]+[r['groups'] for r in game.history]
    metrics_chart=svg_chart('World indicators across six rounds', {k:[r[k] for r in timeline] for k in METRICS}, METRICS)
    groups_chart=svg_chart('Population outcomes across six rounds', {k:[r[k] for r in populations] for k in GROUPS}, GROUPS)
    rows=[]
    for k,label in METRICS.items():
        start=INITIAL[k]; end=game.metrics[k]; delta=end-start
        rows.append(f'<tr><td>{html.escape(label)}</td><td>{start}</td><td>{end}</td><td>{delta:+d}</td><td>{direction(k,delta)}</td><td>{html.escape(INTERPRETATION[k])}</td></tr>')
    decision_html=[]
    previous=INITIAL; previous_group=INITIAL_GROUPS
    for item in game.history:
        changes=[]
        for k,label in METRICS.items():
            delta=item['metrics'][k]-previous[k]
            if delta: changes.append(f'{label} {delta:+d}')
        for k,label in GROUPS.items():
            delta=item['groups'][k]-previous_group[k]
            if delta: changes.append(f'{label} {delta:+d}')
        actors='; '.join(item['responses']) or 'No recorded response'
        decision_html.append(f'<section><h3>Round {item["round"]}: {html.escape(item["title"])}</h3><p><b>Decision:</b> {html.escape(item["choice"])}</p><p><b>Recorded actor responses:</b> {html.escape(actors)}</p><p><b>Net changes since previous decision:</b> {html.escape("; ".join(changes) or "None")}</p><p class="note">These net changes can include effects scheduled by earlier decisions. See the causal audit for attribution.</p></section>')
        previous=item['metrics']; previous_group=item['groups']
    audit_html=''.join(f'<li>{html.escape(a)}</li>' for a in game.audit)
    start_u=INITIAL_GROUPS['undocumented_women']; end_u=game.groups['undocumented_women']
    summary=f'Humanitarian access changed {game.metrics["access"]-INITIAL["access"]:+d} points; community trust {game.metrics["trust"]-INITIAL["trust"]:+d}; women’s participation {game.metrics["participation"]-INITIAL["participation"]:+d}; political tension {game.metrics["tension"]-INITIAL["tension"]:+d} (higher is worse). Undocumented women’s outcome changed {end_u-start_u:+d}, compared with aggregate access {game.metrics["access"]-INITIAL["access"]:+d}. These are separate illustrative proxies, not directly comparable welfare units.'
    css='''body{font:15px/1.6 system-ui,-apple-system,sans-serif;color:#213246;max-width:1000px;margin:32px auto;padding:0 24px}h1,h2,h3{color:#173f58}h1{font-size:30px}.muted,.note{color:#627185}.note{font-size:13px}table{border-collapse:collapse;width:100%;font-size:13px}th,td{padding:9px;border-bottom:1px solid #dce3eb;text-align:left;vertical-align:top}th{background:#eef3f6}section{border-top:1px solid #dce3eb;padding:8px 0}.chart{border:1px solid #dce3eb;border-radius:12px;margin:18px 0;padding:10px}.chart svg{width:100%;height:auto}.legends{display:flex;flex-wrap:wrap;gap:8px 16px;font-size:12px}.legend{white-space:nowrap}.swatch{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px}details{margin:15px 0}li{margin:5px 0}@media print{body{margin:0}.chart,section{break-inside:avoid}details{display:block}}'''
    group_meanings_html="".join(f"<li><b>{html.escape(GROUPS[k])}:</b> {html.escape(v)}</li>" for k,v in GROUP_MEANINGS.items())
    content=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AI × WPS — Ardin Simulation Report</title><style>{css}</style></head><body><h1>AI × WPS — Republic of Ardin</h1><p class="muted">Post-simulation analysis · 6 rounds · {html.escape(game.role)} role · Generated locally; no data uploaded</p><h2>Executive summary</h2><p>{html.escape(summary)}</p><h2>Outcome indicators</h2><p class="note">All scores 0–100; lower is better for digital exclusion and political tension. Scores are fictional design assumptions, not empirical predictions.</p><table><thead><tr><th>Indicator</th><th>Start</th><th>End</th><th>Δ</th><th>Direction</th><th>WPS / governance interpretation</th></tr></thead><tbody>{''.join(rows)}</tbody></table><h2>Intersectional human security outcomes</h2><p>{html.escape(GROUP_NOTE)}</p><ul>{group_meanings_html}</ul><p>{html.escape(GROUP_REFLECTION)}</p><h2>Graphs</h2>{metrics_chart}{groups_chart}<h2>Decision-by-decision feedback</h2>{''.join(decision_html)}<h2>WPS pillar analysis</h2><p><b>Participation:</b> Examine changes in the participation indicator and whether affected groups gained decision authority, rather than only being consulted. The current engine does not separately model formal authority.</p><p><b>Protection:</b> Compare civilian security, privacy, digital exclusion, and population outcomes. Improvements in aggregate security do not establish equal protection.</p><p><b>Prevention:</b> Consider political tension and community trust, alongside whether AI warnings were independently verified.</p><p><b>Relief and recovery:</b> Compare humanitarian access with group-specific outcomes. Higher throughput may coexist with exclusion.</p><h2>AI uncertainty and disclosure</h2><p>The security warning was <b>{html.escape(game.hidden_threat)}</b> in this seeded fictional run. This truth was hidden during play. The 76% confidence figure was not a probability of an attack; the 88% vendor accuracy claim lacked subgroup evidence.</p><h2>Reflection questions</h2><ol><li>Which groups gained or lost decision-making authority?</li><li>Where did aggregate humanitarian access diverge from group outcomes?</li><li>Which AI claims were uncertain, and who could challenge them?</li><li>How did censorship, verification, and data-sharing choices affect trust?</li><li>Which trade-offs might change if actors had independent veto power?</li></ol><details><summary><b>Full causal audit (expand)</b></summary><ol>{audit_html}</ol></details><p class="note"><b>Limitations:</b> Actor responses are deterministic rules, not autonomous language-model agents. Effects are illustrative, and the current engine does not fully model bargaining, legal compliance, or counterfactual causation. Round-level net changes may include scheduled effects from earlier rounds. The report explains recorded effects and plausible educational implications, not verified causal mechanisms in real conflicts.</p></body></html>'''
    html_path=folder/'ardin_report.html'; html_path.write_text(content,encoding='utf-8')
    json_path=folder/'ardin_session.json'
    payload={'role':game.role,'initial_metrics':INITIAL,'initial_groups':INITIAL_GROUPS,'history':game.history,'final_metrics':game.metrics,'final_groups':game.groups,'hidden_threat':game.hidden_threat,'audit':game.audit,'caveat':'All effects are illustrative educational assumptions.'}
    json_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    csv_path=folder/'ardin_timeline.csv'
    with csv_path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f); writer.writerow(['round']+list(METRICS)+list(GROUPS))
        for i,(m,g) in enumerate(zip(timeline,populations)):
            writer.writerow([i]+[m[k] for k in METRICS]+[g[k] for k in GROUPS])
    return html_path,csv_path,json_path


# Word export is separate so existing machine-readable exports retain their interface.
def export_word_report(game, folder='reports', reflections=None, advisor_history=None):
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from educational_content import SCENARIO, ROLE_PROFILES, PILLARS, DEMOGRAPHICS, DEMOGRAPHIC_NOTE, ROUND_NARRATIVES, TECH_CONTEXT
    from ai_wps_engine import ACTORS
    if len(game.history)!=6:
        raise ValueError('Complete all six rounds before exporting the final report.')
    d=Document(); sec=d.sections[0]
    sec.top_margin=sec.bottom_margin=Inches(.8); sec.left_margin=sec.right_margin=Inches(.85)
    normal=d.styles['Normal']; normal.font.name='Calibri'; normal.font.size=Pt(11)
    normal.paragraph_format.space_after=Pt(7)
    for style in ('Heading 1','Heading 2','Title'):
        d.styles[style].font.color.rgb=RGBColor.from_string('173F58')
    sec.header.paragraphs[0].text='AI × WPS  |  THE HUMANITARIAN ALGORITHM'
    sec.footer.paragraphs[0].text='Educational simulation • Fictional data • Not a field assessment'
    d.add_heading('Republic of Ardin',0); d.add_paragraph('Post-simulation decision analysis | '+ACTORS[game.role][0],style='Subtitle')
    def h(t): d.add_heading(t,1)
    def para(t): d.add_paragraph(t)
    def delta(k): return game.metrics[k]-INITIAL[k]
    def evidence(k): return f'{METRICS[k]}: {INITIAL[k]} → {game.metrics[k]} ({delta(k):+d}; {direction(k,delta(k))})'
    h('Executive summary'); para('The player completed six decisions as '+ACTORS[game.role][0]+'. '+ '; '.join(evidence(k) for k in ('access','trust','participation','exclusion'))+'. These outcomes describe separate simulated proxies, not measured humanitarian impacts.')
    h('1. Context, technology and actors'); para(SCENARIO); para(TECH_CONTEXT)
    para('Population planning profile: '+ '; '.join(f'{k}: {v:,}' for k,v in DEMOGRAPHICS.items())+'. '+DEMOGRAPHIC_NOTE)
    for k,(name,_) in ACTORS.items(): para(name+(' (player)' if k==game.role else '')+': '+ROLE_PROFILES[k])
    h('2. Outcomes and indicator meanings')
    para('Scores range from 0–100. Lower is better for exclusion and tension; higher is generally better for the others. A point is not a percentage or a person.')
    for k in METRICS: para(evidence(k)+'. '+INTERPRETATION[k])
    para(GROUP_NOTE)
    para(GROUP_REFLECTION)
    for k,label in GROUPS.items(): para(f'{label}: {INITIAL_GROUPS[k]} → {game.groups[k]} ({game.groups[k]-INITIAL_GROUPS[k]:+d}). {GROUP_MEANINGS[k]}')
    h('3. Decisions, reactions and causal mechanisms')
    prev=INITIAL; pg=INITIAL_GROUPS
    for r in game.history:
        n=r['round']; d.add_heading(f'Round {n} — {r["title"]}',2); para(ROUND_NARRATIVES[n-1]); para('Decision: '+r['choice'])
        if reflections and reflections.get(n): para('Player reasoning: '+reflections[n])
        para('Recorded reactions: '+ ('; '.join(r['responses']) or 'None recorded.'))
        changes=[f'{METRICS[k]} {r["metrics"][k]-prev[k]:+d}' for k in METRICS if r['metrics'][k]!=prev[k]]+[f'{GROUPS[k]} {r["groups"][k]-pg[k]:+d}' for k in GROUPS if r['groups'][k]!=pg[k]]
        para('Net changes: '+('; '.join(changes) or 'None')+'.')
        for a in game.audit:
            if a.startswith(f'Round {n}: '): d.add_paragraph(a.split(': ',1)[1],style='List Bullet')
        para('Audit entries show rule contributions before score bounds; net changes may include delayed effects. Consider who benefits, who bears barriers, and which evidence is missing.')
        prev=r['metrics']; pg=r['groups']
    h('4. Gender, Peace & Security / WPS analysis')
    lenses=[('Participation',('participation','trust'), 'Review whether eligibility, consultation and appeals gave women meaningful influence. Examine representation among men, youth and marginalized residents too. Formal decision authority is not separately measured.',(1,2,6)),('Protection',('security','privacy','exclusion'),'Consider confidentiality, discriminatory screening, safe movement and access for residents without documents. Do not infer actual violence or surveillance incidents from these scores.',(3,4)),('Prevention',('tension','trust','security'),'Examine whether verification, transparent communication and grievances could reduce or amplify escalation. A security alert is not proof of an attack.',(3,5)),('Relief & Recovery',('access','exclusion'),'Compare throughput with the undocumented-women outcome and consider service barriers for older people, children and people with disabilities. Infrastructure cascading effects are not separately modeled.',(1,2,6))]
    for title,keys,interpret,rounds in lenses:
        d.add_heading(title,2); para(PILLARS[title]); para('Observed simulation trajectory: '+ '; '.join(evidence(k) for k in keys)+'.'); para('Relevant decisions: '+ '; '.join(f'Round {n}: {game.history[n-1]["choice"]}' for n in rounds)+'.'); para(interpret)
    h('5. Intersectional and technology implications'); para('Potential differential effects to investigate include documentation and care barriers for women, profiling of young men, accessibility for disabled residents, disrupted education for girls and boys, and privacy risks for gender-diverse people. These are analytical hypotheses, not separately calculated outcomes. Compare group outcomes above; avoid treating groups as homogeneous or assuming vulnerability without evidence.')
    para('The seeded warning was '+game.hidden_threat+'. This was hidden during play. The 76% confidence figure is not an attack probability; the advertised 88% accuracy lacks subgroup evidence.')
    h('6. Recommendations and reflection');
    priorities=sorted(METRICS,key=lambda k: (delta(k) if k not in ('exclusion','tension') else -delta(k)))
    actions={'access':'Preserve manual alternatives and monitor service access by group.','trust':'Establish accessible complaints and publish responses to documented errors.','participation':'Give affected women meaningful authority over eligibility and oversight.','security':'Verify warnings independently and review civilian impacts.','exclusion':'Test subgroup errors and support offline registration and appeals.','privacy':'Minimize data collection and require purpose limits and independent review.','tension':'Engage community representatives and negotiate proportionate responses.'}
    for k in priorities[:3]: para(evidence(k)+'. Suggested safeguard: '+actions[k])
    para('Reflection: Which decisions prioritized your institutional mandate over other groups’ needs? What alternative safeguards would you consider? What evidence would change your judgment?')
    h('Methodology and limitations'); para('The six crisis milestones are fixed. Roles share illustrative effect pathways; actor responses are rule-driven, not autonomous agents. The report uses recorded decisions and audit entries, not an external AI service or verified legal assessment. Counterfactual outcomes and separate demographic impacts are not calculated.')
    if advisor_history:
        h('Appendix: AI advisor conversation'); para('Optional AI-generated interpretations, not validated evidence or modeled outcomes. Responses reflect the information available when requested.')
        for t in advisor_history:
            d.add_heading(f"Round {t['round']} | {t['phase']} | {t['perspective']}",2); para('Question: '+t['question']); para(t['answer'])
    folder=Path(folder); folder.mkdir(parents=True,exist_ok=True); path=folder/'ardin_analysis.docx'; d.save(path); return path
