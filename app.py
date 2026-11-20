"""AI × WPS browser prototype. Run: python -m streamlit run app.py"""
import json
import os
from ai_advisor import ask, public_context, PERSPECTIVES
import csv
import io
import tempfile
from functools import lru_cache
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
from educational_content import SCENARIO, ROLE_PROFILES, PILLARS, ISSUE_LENSES, SECTORS, FRAMEWORKS, DEMOGRAPHICS, DEMOGRAPHIC_NOTE, TECH_CONTEXT, ROUND_NARRATIVES
from ai_wps_engine import Game, ROUNDS, ACTORS, METRICS
from reporting import export_report, INITIAL, INITIAL_GROUPS, INTERPRETATION, GROUP_MEANINGS, GROUP_NOTE, GROUP_REFLECTION

st.set_page_config(page_title='AI × WPS | Reimagining Peace and Security', page_icon='🕊️', layout='wide')
st.markdown('''<style>
.stApp, [data-testid="stAppViewContainer"] {background:#080f18;color:#f1f5fa}
[data-testid="stHeader"], [data-testid="stSidebar"] {background:#142636;color:#f1f5fa}
h1,h2,h3,h4 {color:#f0d7a1 !important}
[data-testid="stMarkdownContainer"] p, [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {color:#e4edf5!important}
[data-testid="stMetric"] {background:#1b3245;border:1px solid #58758b;border-radius:12px;padding:12px}
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p, [data-testid="stMetricValue"] {color:#f1f5fa!important}
[data-testid="stMetricDelta"] {background:transparent!important}
[data-testid="stMetricDelta"] svg {fill:currentColor}
button[kind="primary"], button[data-testid="stBaseButton-primary"] {background:#e9bd70!important;color:#102131!important;border:2px solid #e9bd70!important;font-weight:750}
button[kind="primary"] p, button[data-testid="stBaseButton-primary"] p {color:#102131!important}
button[kind="secondary"], button[data-testid="stBaseButton-secondary"], [data-testid="stPopoverButton"] {background:#24445d!important;color:#f1f5fa!important;border:1px solid #7896aa!important}
button[kind="secondary"] p, button[data-testid="stBaseButton-secondary"] p, [data-testid="stPopoverButton"] p {color:#f1f5fa!important}
[data-testid="stRadio"] label {background:#24445d!important;border:2px solid #7896aa!important;border-radius:12px!important;padding:14px 16px!important;margin:8px 0!important;color:#ffffff!important}
[data-testid="stRadio"] label:has(input:checked) {background:#2e6269!important;border:3px solid #f4c87a!important}
[data-testid="stRadio"] label p {color:#ffffff!important;font-weight:650!important}
[data-testid="stForm"] {background:#172f43;border:1px solid #66869d;border-radius:14px;padding:18px}
[data-baseweb="select"] > div, [data-baseweb="input"], [data-baseweb="textarea"], [data-testid="stNumberInput"] input, textarea {background:#1b3245!important;color:#f1f5fa!important;border-color:#7896aa!important}
[data-baseweb="select"] svg {fill:#f1f5fa!important}
[data-baseweb="popover"], [data-baseweb="menu"], [data-testid="stPopoverBody"] {background:#1b3245!important;color:#f1f5fa!important}
[data-baseweb="menu"] li {color:#f1f5fa!important;background:#1b3245!important}
[data-baseweb="menu"] li:hover {background:#34566d!important}
[data-testid="stAlert"] {background:#203d54!important;color:#f1f5fa!important;border:1px solid #678da7}
[data-testid="stAlert"] p {color:#f1f5fa!important}
button:focus-visible, input:focus-visible, textarea:focus-visible, [role="radio"]:focus-visible {outline:3px solid #f4c87a!important;outline-offset:2px}
</style>''', unsafe_allow_html=True)

if 'game' not in st.session_state:
    st.session_state.game = Game()
    st.session_state.started = False
    st.session_state.completed = False
    st.session_state.role = 'humanitarian'
    st.session_state.seed = 17
    st.session_state.reflections = {}

def restart():
    st.session_state.direct_debrief=False
    st.session_state.game = Game(seed=st.session_state.seed, role=st.session_state.role)
    st.session_state.started = False
    st.session_state.completed = False
    st.session_state.reflections = {}
    st.session_state.pop('advisor_result',None)
    st.session_state.advisor_history=[]
    st.session_state.advisor_calls=0
    st.session_state.advisor_open=False

def ensure_round():
    game=st.session_state.game
    if not st.session_state.completed and not st.session_state.started:
        game.start_round()
        st.session_state.started=True

def timeline(game):
    rows=[{'Round':0,**INITIAL}]
    rows += [{'Round':x['round'],**x['metrics']} for x in game.history]
    return rows

def population_timeline(game):
    return [{'Round':0,**INITIAL_GROUPS}]+[{'Round':x['round'],**x['groups']} for x in game.history]

def embedded_atlas():
    """Use the same interactive atlas on both Strategy and Living Atlas pages."""
    raw=(Path(__file__).parent/'ardin_map.html').read_text(encoding='utf-8')
    # Hide only the legacy, disconnected power-outage choice and its result.
    return raw.replace('</head>','<style>#choices,#result{display:none!important}</style></head>')

OPERATIONAL_MEANINGS={
    'access':'This proxy concerns the ability to deliver and obtain assistance. A decrease suggests more friction in routes, eligibility, staffing or distribution; it does not identify a number of missed households. Ask which sectors and residents face the barriers.',
    'trust':'This proxy reflects perceived legitimacy and willingness to cooperate. Lower trust could mean more complaints, reluctance to register or reduced cooperation; these are possible interpretations, not measured behaviors.',
    'participation':'This proxy concerns meaningful influence of women in decisions, not merely attendance. A decline suggests less opportunity to shape rules, oversight or appeals; men and other marginalized groups also require separate participation analysis.',
    'security':'This proxy concerns civilian safety. Changes may signal different protection pressures, but do not establish actual incident rates, attacks or deaths.',
    'exclusion':'This proxy reflects barriers caused by digital and registration systems. A rise is adverse and may especially affect people without documents, connectivity, accessible devices or digital literacy.',
    'privacy':'This proxy concerns confidentiality, oversight and exposure of personal data. An improvement suggests stronger safeguards, not proof of compliance with any specific law.',
    'tension':'This proxy represents political and institutional friction. A rise may increase the risk of obstruction or conflict escalation, but does not predict a particular incident.'
}

def operational_explanation(key,delta):
    return OPERATIONAL_MEANINGS[key]

def causal_explanation(key, event, previous):
    """Describe modeled contributors, without claiming a score is a measured impact."""
    audit = event.get('audit_entries', [])
    relevant = [a.split(': ',2)[-1] for a in audit if f': {key} ' in a]
    if not relevant:
        return ('This net change includes effects recorded when the new round began, '
                'including possible delayed consequences of earlier decisions. '
                'Review the causal audit to identify the contributing event.')
    return 'Modeled contributors: ' + '; '.join(relevant) + '.'

def next_round_bridge(game):
    nxt=game.round_number+1
    if nxt>len(ROUNDS):
        return ''
    prev=game.history[-1]
    scenario=ROUND_NARRATIVES[nxt-1]
    reactions=' '.join(prev.get('responses', [])) or 'No separate institutional reaction was recorded.'
    return (f"After your decision to **{prev['choice']}**, {reactions} "
            f"Current conditions include community trust **{game.metrics['trust']}**, "
            f"digital exclusion **{game.metrics['exclusion']}**, and humanitarian access "
            f"**{game.metrics['access']}** (illustrative 0–100 proxies). "
            f"**Your next challenge:** {scenario}")

def report_files(game):
    with tempfile.TemporaryDirectory(prefix='ardin_web_') as temp:
        paths=export_report(game,folder=temp)
        return {Path(path).name:Path(path).read_bytes() for path in paths}


# Platform navigation is separate from the live simulation state.
if 'screen' not in st.session_state: st.session_state.screen='home'
def navigate(screen):
    st.session_state.screen=screen
    st.rerun()

from platform_pages import render_information
nav = [('Home','home'),('About','about'),('Scenarios','library'),('How to Play','guide'),('For Educators','educators')]
cols = st.columns(5)
for col,(label,target) in zip(cols,nav):
    if col.button(label,key='nav_'+target,use_container_width=True): navigate(target)
if st.session_state.screen != 'play':
    if st.session_state.started or st.session_state.game.history:
        if st.button('Resume current simulation',key='resume_navigation'): navigate('play')
    if st.session_state.screen in ('about','guide','educators'):
        render_information(st.session_state.screen)
        st.stop()
    st.title('AI × WPS')
    st.markdown('### Reimagining Peace and Security')
    if st.session_state.screen=='home':
        st.image(str(Path(__file__).parent/'assets/images/welcome_banner.png'),use_container_width=True)
        st.markdown('### Explore a changing world. Navigate complex crises. Shape the future of human security.')
        st.write('AI × WPS is an interactive simulation and experiential learning platform exploring how artificial intelligence and emerging technologies transform conflict, peacebuilding, governance, gender relations and human security.')
        if st.button('Learn more about AI × WPS →'): navigate('about')
        a,b=st.columns(2)
        with a:
            with st.container(border=True):
                st.subheader('Existing scenarios')
                st.write('Enter a developed fictional world, select a role and navigate interconnected crises.')
                if st.button('Explore scenarios',type='primary',use_container_width=True): navigate('library')
        with b:
            with st.container(border=True):
                st.subheader('Create your own scenario')
                st.write('Build a planning brief for a real, imagined or hybrid context. Playable custom scenarios are a future feature.')
                if st.button('Open scenario builder',use_container_width=True): navigate('builder')
        st.divider()
        st.subheader('Discover. Decide. Reflect.')
        for col,(title,desc) in zip(st.columns(3), [('Explore','Discover complex worlds and interconnected crises.'),('Decide','Navigate competing interests and difficult trade-offs.'),('Reflect','Analyze consequences through AI and WPS perspectives.')]):
            col.markdown('**'+title+'**')
            col.write(desc)
        st.caption('AI × WPS · Educational research prototype · v0.7.1')
    elif st.session_state.screen=='library':
        if st.button('← Home'): navigate('home')
        st.subheader('Scenario library')
        with st.container(border=True):
            st.caption('SCENARIO 01 · PLAYABLE PROTOTYPE')
            st.image(str(Path(__file__).parent/'assets/images/ardin_humanitarian.png'),use_container_width=True)
            st.subheader('The Humanitarian Algorithm')
            st.write(SCENARIO)
            st.write('Themes: humanitarian AI, critical infrastructure, data governance, intersectional inclusion and civilian protection.')
            role=st.selectbox('Choose your role',list(ACTORS),format_func=lambda k:ACTORS[k][0],index=list(ACTORS).index(st.session_state.role),key='launch_role')
            st.write(ROLE_PROFILES[role])
            if st.button('Start new scenario',type='primary'):
                st.session_state.role=role
                restart()
                navigate('play')
            if st.session_state.started or st.session_state.game.history:
                if st.button('Resume existing session'): navigate('play')
        st.caption('Planned scenarios: Critical Infrastructure Crisis · Digital Sovereignty · AI at the Peace Table · Information Battlefield · Algorithmic Security Dilemma')
    elif st.session_state.screen=='builder':
        if st.button('← Home'): navigate('home')
        st.subheader('Design your own scenario')
        st.info('Planning workspace only: this creates a downloadable brief, not a playable game.')
        kind=st.radio('Context',['Imagined','Real-world','Hybrid'])
        location=st.text_input('Country, region or fictional world')
        setting=st.selectbox('Environment',['Humanitarian emergency','Active conflict','Post-conflict recovery','Political crisis','Peacetime security challenge'])
        themes=st.multiselect('Themes',list(ISSUE_LENSES)+['Digital sovereignty','Peace negotiations','Disinformation','Technology-facilitated GBV'])
        infrastructure=st.multiselect('Critical infrastructure',['Electricity','Water and sanitation','Telecommunications','Healthcare','Transport and logistics','Food systems','Finance'])
        goals=st.text_area('Learning objectives and central dilemma')
        roles=st.text_area('Proposed actors and their objectives')
        brief={'context':kind,'location':location,'environment':setting,'themes':themes,'infrastructure':infrastructure,'learning_objectives':goals,'actors':roles,'status':'Draft only; verify real-world facts and label assumptions before use.'}
        st.download_button('Download scenario design brief',json.dumps(brief,indent=2),file_name='scenario_brief.json',mime='application/json')
    st.stop()

with st.sidebar:
    st.markdown('## 🕊️ AI × WPS')
    st.caption('Republic of Ardin · Camp 17')
    if st.button('← Platform home',use_container_width=True): navigate('home')
    role=st.selectbox('Play as', list(ACTORS), format_func=lambda k:ACTORS[k][0], index=list(ACTORS).index(st.session_state.role), help='Each role now has its own institutional choices, objectives, and adaptive context.')
    seed=st.number_input('Scenario seed',min_value=0,max_value=999999,value=st.session_state.seed,step=1,help='Changes the hidden security assessment outcome. The result stays hidden until the debrief.')
    if role!=st.session_state.role or seed!=st.session_state.seed:
        st.session_state.role=role; st.session_state.seed=int(seed); restart(); st.rerun()
    if st.button('↻ Restart simulation', use_container_width=True):
        restart(); st.rerun()
    st.divider()
    st.session_state.setdefault('advisor_limit',20)
    st.number_input('AI request limit per simulation',min_value=1,max_value=100,key='advisor_limit')
    st.caption('Educational prototype · Synthetic scenario · No autonomous actors or real-world prediction')

st.title('AI × WPS · The Humanitarian Algorithm')
st.caption('Hybrid strategy simulation and policy analysis · Six distinct playable roles · Adaptive briefings')
game=st.session_state.game
ensure_round()
if len(game.history)==len(ROUNDS):
    st.session_state.completed=True
current=ROUNDS[game.round_number-1]

def render_advisor(game, prefix='advisor'):
    st.subheader('AI Advisor · Your analytical partner')
    st.caption('Read-only assistance · Current role and visible situation · No changes to scores or decisions')
    history=st.session_state.setdefault('advisor_history',[])
    st.session_state.setdefault('advisor_calls',0)
    if not os.environ.get('OPENAI_API_KEY','').strip():
        st.info('AI is not configured. Set OPENAI_API_KEY in Terminal before launching. You can continue playing offline.')
    perspective=st.selectbox('Advisory perspective',PERSPECTIVES,key=prefix+'_perspective')
    mode=st.radio('Learning mode',['Consultative','Socratic'],horizontal=True,key=prefix+'_mode')
    limit=st.session_state.get('advisor_limit',20)
    st.caption(f"Requests attempted: {st.session_state.advisor_calls} / {limit}. This is a session limit, not a shared API spending cap.")
    st.caption('Your fictional visible game state, question and up to six recent exchanges are sent to the OpenAI API only when you submit. Charges may apply. Do not enter personal or sensitive information. AI responses may be inaccurate.')
    for t in history:
        with st.chat_message('user'):
            st.caption(f"Round {t['round']} · {t['phase']} · {t['perspective']}")
            st.write(t['question'])
        with st.chat_message('assistant'):
            st.markdown(t['answer'])
    with st.form(prefix+'_ask',clear_on_submit=True):
        prompt=st.selectbox('Suggested question (optional)',['Write my own','What information am I missing?','Compare the trade-offs of my options.','Analyze the latest decision through the four WPS pillars.','Explain the changes in trust and access.','Which governance frameworks might be relevant?'],key=prefix+'_suggest')
        question=st.text_area('Ask your advisor or follow up',max_chars=2000,key=prefix+'_question')
        consent=st.checkbox('I agree to send this question and visible context to the AI service.',key=prefix+'_consent')
        submit=st.form_submit_button('Ask Advisor',type='primary')
    if submit:
        q=question.strip() or (prompt if prompt!='Write my own' else '')
        if not consent or not q: st.warning('Enter a question and confirm consent.')
        elif not os.environ.get('OPENAI_API_KEY','').strip(): st.warning('Configure your API key first.')
        elif st.session_state.advisor_calls>=limit: st.warning('Request limit reached.')
        else:
            context=public_context(game)
            st.session_state.advisor_calls+=1
            try:
                with st.spinner('Analyzing your situation…'):
                    answer=ask(context,q,history=history,perspective=perspective,mode=mode)
                history.append({'question':q,'answer':answer,'round':context['round'],'phase':context['phase'],'perspective':perspective,'mode':mode})
                st.rerun()
            except Exception as exc: st.error(str(exc))
    if history:
        st.download_button('Download advisor conversation',json.dumps(history,ensure_ascii=False,indent=2),file_name='advisor_conversation.json',mime='application/json',key=prefix+'_download')
        if st.button('Clear advisor conversation',key=prefix+'_clear'):
            history.clear(); st.rerun()
    st.caption('AI-generated interpretation, not verified research, legal advice or an official simulation outcome.')

if st.button('Open AI Advisor' if not st.session_state.get('advisor_open') else 'Close AI Advisor',key='advisor_global'):
    st.session_state.advisor_open=not st.session_state.get('advisor_open',False)
    st.rerun()
if st.session_state.get('advisor_open'):
    render_advisor(game,'global_advisor')
    st.stop()

def render_debrief(game):
    st.download_button('⬇ Download current session (JSON)', data=json.dumps({
        'role':game.role, 'round':game.round_number, 'history':game.history,
        'metrics':game.metrics, 'groups':game.groups,
        'note':'Fictional illustrative simulation, not field data.'
    },indent=2), file_name='ardin_progress.json',mime='application/json',
    use_container_width=True)
    if len(game.history)<6:
        st.info('The complete debrief, causal audit, hidden scenario outcome, and downloads unlock after Round 6. This prevents spoilers during gameplay.')
        st.write(f'{len(game.history)} of 6 decisions completed.')
    else:
        st.subheader('Post-simulation WPS analysis')
        st.write('**Security warning, revealed after play:**',game.hidden_threat)
        st.markdown('#### Four WPS lenses')
        st.markdown('**Participation:** Examine whether affected women gained actual decision authority or were only consulted.')
        st.markdown('**Protection:** Examine civilian security, privacy, exclusion and the risks faced by specific groups.')
        st.markdown('**Prevention:** Examine political tension, community trust, contested intelligence and institutional reactions.')
        st.markdown('**Relief and recovery:** Compare aggregate humanitarian access with outcomes for undocumented women and other residents.')
        st.markdown('#### Reflection prompts')
        st.write('Who gained authority? Which choices relied on uncertain AI claims? Whose well-being diverged from aggregate access? Which delayed effects altered later rounds?')
        try:
            files=report_files(game)
        except Exception as exc:
            st.error(f'Report generation failed: {exc}')
            files={}
        include_ai=st.checkbox("Include advisor conversations in Word report (optional)",value=False,key="include_advisor_report")
        try:
            from reporting import export_word_report
            with tempfile.TemporaryDirectory() as tmp:
                word=export_word_report(game,tmp,st.session_state.reflections, st.session_state.get('advisor_history',[]) if include_ai else None)
                files[word.name]=word.read_bytes()
        except Exception as exc:
            st.warning(f"Word report unavailable: {exc}")
        for filename,blob in files.items():
            st.download_button(f'⬇ Download {filename}',data=blob,file_name=filename,mime='text/html' if filename.endswith('.html') else 'text/csv' if filename.endswith('.csv') else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' if filename.endswith('.docx') else 'application/json',use_container_width=True)
        with st.expander('Full causal audit'):
            for event in game.audit:
                st.write(event)
        st.caption('Reports contain modeled effects and explicitly labeled educational interpretations. No empirical causal validity is claimed.')


if st.session_state.get("direct_debrief", False) and len(game.history)==6:
    if st.button("← Return to simulation and tabs"):
        st.session_state.direct_debrief=False
        st.rerun()
    render_debrief(game)
    st.stop()

strategy,atlas,population,analysis,library,debrief,advisor=st.tabs(['🎯 Strategy room','🗺️ Living atlas','👥 Population & WPS','📈 Situation dashboard','📚 Governance library','📑 Debrief & downloads','AI advisor'])
with strategy:
    st.subheader(f'Round {game.round_number} of 6 · {current.title}')
    st.info(ROUND_NARRATIVES[game.round_number-1])
    st.markdown('**How we reached this crisis**')
    st.write(game.adaptive_context())
    st.markdown('#### Operational map · Republic of Ardin / Camp 17')
    st.caption('Zoom, select sectors, and inspect infrastructure while planning your decision. This map is exploratory; sector visuals do not yet update from game scores.')
    components.html(embedded_atlas(), height=485, scrolling=True)
    left,right=st.columns([1.4,1],gap='large')
    with left:
        st.markdown('#### Situation and evidence')
        st.write('**Camp 17:** 8,000 fictional displaced residents. Crowded temporary shelters, repaired habitat pods, damaged service links, and contested aid routes.')
        with st.expander('Full context and constraints'):
            st.write(SCENARIO)
        st.write('**Incoming briefing:**',game.role_briefing(current))
        if game.round_number==1:
            st.markdown('**Technology and operational context**')
            st.write(TECH_CONTEXT)
        st.caption(f'Intelligence signal: {current.signal}')
        st.caption('The current dilemma incorporates prior decisions, stakeholder reactions, and changing world indicators. Its six crisis milestones remain fixed in this version.')
    with right:
        st.markdown('#### Your mandate')
        st.write(f'**{ACTORS[game.role][0]}** — {ACTORS[game.role][1]}')
        st.write(ROLE_PROFILES[game.role])
        with st.expander('Stakeholders and competing objectives'):
            for actor,(title,desc) in ACTORS.items():
                if actor!=game.role: st.markdown(f'**{title}:** {ROLE_PROFILES[actor]}')
    st.divider()
    st.markdown('### Decision center')
    if not st.session_state.completed and len(game.history)<game.round_number:
        st.session_state.reflections[game.round_number]=st.text_area('Your reasoning (optional): what evidence, affected populations, and trade-offs matter?',value=st.session_state.reflections.get(game.round_number,''),key=f'rationale_{game.round_number}')
        with st.form(f'decision_round_{game.round_number}'):
            choices=game.available_choices()
            choice=st.radio('Select your response',range(len(choices)),format_func=lambda i:choices[i][0])
            st.markdown('**What this option would mean operationally**')
            st.info(choices[choice][1])
            st.caption('Consider who makes this decision, who must implement it, which residents may be excluded, what evidence is missing, and what alternative safeguards are available.')
            submit=st.form_submit_button('Confirm decision and see consequences',type='primary',use_container_width=True)
        if submit:
            game.decide(choice)
            st.rerun()
    else:
        last=game.history[-1]
        st.success(f"Decision recorded: {last['choice']}")
        st.markdown('#### What changed, and why it matters')
        previous=INITIAL if len(game.history)==1 else game.history[-2]['metrics']
        group_previous=INITIAL_GROUPS if len(game.history)==1 else game.history[-2]['groups']
        metric_changes={k:last['metrics'][k]-previous[k] for k in METRICS}
        changed=[(k,d) for k,d in metric_changes.items() if d]
        if changed:
            for k,d in changed:
                direction='improved' if (d<0 if k in ('exclusion','tension') else d>0) else 'worsened'
                st.markdown(f'**{METRICS[k]}: {d:+d} ({direction})** — {operational_explanation(k,d)}')
                st.write(causal_explanation(k,last,previous))
        else: st.write('No change in the aggregate world indicators this round.')
        st.caption('All values are fictional 0–100 scenario proxies, not percentages, counts, or validated predictions. Net changes may include delayed effects from previous choices and other actors.')
        st.markdown('#### Intersectional human security outcomes')
        st.caption(GROUP_NOTE)
        st.write(GROUP_REFLECTION)
        changed_groups=[(k,last['groups'][k]-group_previous[k]) for k in INITIAL_GROUPS if last['groups'][k]!=group_previous[k]]
        if changed_groups:
            for k,d in changed_groups:
                st.write(f"**{k.replace('_',' ').title()}: {d:+d}** — Modeled change in an illustrative group outcome; investigate the relevant barriers and who within this group may be differently affected.")
        else: st.write('No additional group-level score change was modeled. This does not imply that no residents were affected.')
        st.markdown('#### What this means for your role')
        st.write(last.get('role_impact',''))
        st.markdown('#### Stakeholder reactions')
        if last['responses']:
            for response in last['responses']:st.markdown(f'- {response}')
        else: st.write('No separate actor response recorded for this decision.')
        with st.expander('Intersectional and WPS interpretation'):
            st.write('Consider the different experiences of women, men, girls, boys, older residents, people with disabilities, undocumented households, and those without digital access. The current engine does not calculate separate scores for all these groups.')
            st.write('**Participation:** Who shaped the choice and whose voice was absent? **Protection:** Who faces new risks? **Prevention:** Did grievances or trust change? **Relief & Recovery:** Who can reach services?')
        if game.round_number<6:
            st.markdown('#### Next: the crisis evolves')
            st.write(f"**Round {game.round_number+1}: {ROUNDS[game.round_number].title}**")
            st.write(next_round_bridge(game))
            st.caption('The next milestone remains fixed; its briefing reflects the recorded decision and current conditions. Some delayed effects will only be applied when the next round begins.')
            if st.button('Continue to next decision →',type='primary',use_container_width=True):
                st.session_state.started=False
                st.rerun()
        else:
            st.session_state.completed=True
            st.success('Simulation complete — all six decisions recorded.')
            if st.button('View your report →',type='primary',use_container_width=True):
                st.session_state.direct_debrief=True
                st.rerun()
    st.divider()
    st.markdown('### Situation indicators')
    st.caption('Two-row overview. Select “What does this measure?” under any indicator to understand its meaning, direction, and operational implications.')
    for row_start in (0,4):
        cols=st.columns(4)
        for j,(key,label) in enumerate(list(METRICS.items())[row_start:row_start+4]):
            with cols[j]:
                st.metric(label,game.metrics[key],delta=game.metrics[key]-INITIAL[key],delta_color='inverse' if key in ('exclusion','tension') else 'normal')
                with st.popover('ⓘ What does this measure?',use_container_width=True):
                    st.write(INTERPRETATION[key])
                    st.write('**Direction:** '+('Lower is generally better.' if key in ('exclusion','tension') else 'Higher is generally better.'))
                    st.write(operational_explanation(key,-2 if key in ('exclusion','tension') else 2))
                    st.caption('A two-point change does not mean two people, two percent, or two hours.')

with atlas:
    st.subheader('Ardin · Conflict-affected operational atlas')
    st.caption('Detailed map and context: inspect neighborhoods, infrastructure, demographics and stakeholders. Decisions are made in Strategy room.')
    with st.expander('Scenario background and political context',expanded=True): st.write(SCENARIO)
    with st.expander('Stakeholder mandates and objectives'):
        for actor,(title,desc) in ACTORS.items():st.markdown(f'**{title}:** {ROLE_PROFILES[actor]}')
    components.html(embedded_atlas(),height=830,scrolling=True)
    st.markdown('#### Camp-wide population profile')
    dcols=st.columns(4)
    for col,(label,count) in zip(dcols,DEMOGRAPHICS.items()):
        col.metric(label,f'{count:,}')
    st.caption(DEMOGRAPHIC_NOTE)
    st.markdown('#### Sector demographics and access conditions')
    st.dataframe([{'Sector':name,'Residents (synthetic)':data['population'],'Reported operational concerns':data['focus']} for name,data in SECTORS.items()],hide_index=True,use_container_width=True)
    st.caption('These sector totals are fictional. The model does not yet allocate the game outcomes to individual sectors.')
    st.markdown('#### Live simulation indicators')
    cols=st.columns(4)
    for i,k in enumerate(['access','security','exclusion','trust']):
        cols[i].metric(METRICS[k],game.metrics[k],delta=game.metrics[k]-INITIAL[k],delta_color='inverse' if k=='exclusion' else 'normal')
    st.info('The atlas and the six-round engine are displayed together, but sector-level map changes are not yet calculated from the engine. The map’s separate power-outage choice is a visual demonstration, not an additional game round.')
with population:
    st.subheader('Intersectional population and WPS analysis')
    st.markdown('#### Illustrative camp population: 8,000 residents')
    demo_cols=st.columns(4)
    for col,(label,count) in zip(demo_cols,DEMOGRAPHICS.items()):
        col.metric(label,f'{count:,}',help='Illustrative scenario demographic assumption')
    st.caption(DEMOGRAPHIC_NOTE)
    st.write('The scenario currently models three population outcome proxies: undocumented women, camp residents overall, and the host community. The broader intersectional categories below are qualitative analysis prompts, not simulated subgroup scores.')
    st.dataframe([{'Sector':name,'Residents (synthetic)':data['population'],'Operational focus':data['focus']} for name,data in SECTORS.items()],hide_index=True,use_container_width=True)
    st.markdown('#### Who might be overlooked?')
    st.write('Assess women and men across age, disability, documentation, household structure, livelihood, displacement status and digital access. Consider young men exposed to profiling, older people with mobility barriers, female-headed households, adolescent boys and girls, and gender-diverse residents. Do not infer vulnerability from identity alone.')
    st.markdown('#### Four WPS pillars')
    for title,content in PILLARS.items():
        with st.expander(title): st.write(content)
    st.markdown('#### Intersectional human security outcomes')
    st.write(GROUP_NOTE)
    st.write(GROUP_REFLECTION)
    for group,score in game.groups.items(): st.metric(group.replace('_',' ').title(),score,delta=score-INITIAL_GROUPS[group],help=GROUP_MEANINGS[group])
    st.caption('No invented subgroup effects: a future engine version must explicitly model additional population categories and validate their interaction rules.')
with library:
    st.subheader('Issue-based Decision Impact Explorer')
    st.caption('Select a WPS pillar and cross-cutting issue. Explanations are educational interpretations, not additional model outputs.')
    pillar=st.selectbox('WPS pillar',list(PILLARS))
    issue=st.selectbox('Issue',list(ISSUE_LENSES))
    st.markdown('**Pillar definition and relevance**')
    st.write(PILLARS[pillar])
    st.markdown('**Issue analysis**')
    st.write(ISSUE_LENSES[issue])
    if game.history:
        chosen=st.selectbox('Review a recorded decision',list(range(len(game.history))),format_func=lambda i:f"Round {game.history[i]['round']}: {game.history[i]['choice']}")
        event=game.history[chosen]
        prior=INITIAL if chosen==0 else game.history[chosen-1]['metrics']
        st.write('**Observed net changes since previous recorded decision**')
        st.write(', '.join(f'{METRICS[k]} {event["metrics"][k]-prior[k]:+d}' for k in METRICS if event['metrics'][k]!=prior[k]) or 'No indicator changes')
        st.caption('Net changes can include delayed effects from earlier decisions. Inspect the final causal audit for attribution. These scores are not percentages or counts.')
    else: st.info('Record a decision in Strategy room to explore its outcomes.')
    st.markdown('#### Governance and reference framework directory')
    for title,desc in FRAMEWORKS.items():
        with st.expander(title): st.write(desc)
    uploaded=st.file_uploader('Optional course reading (local preview only; no AI retrieval yet)',type=['pdf','docx','txt','md'],accept_multiple_files=True)
    if uploaded: st.info(f'{len(uploaded)} file(s) selected. This prototype does not ingest, analyze, store, or cite their contents. AI-assisted document retrieval is a future module.')
    st.markdown('#### Future classroom and scenario features')
    st.write('Instructor-controlled temporary access, assignments, evidence-grounded uploaded readings, and guided real/fictional scenario creation are planned, but not implemented or security-reviewed in this release.')

with analysis:
    st.subheader('World indicators · observed so far')
    st.caption('Only rounds already played appear here. Hidden scenario truth is withheld until the final debrief.')
    rows=timeline(game)
    selected=st.multiselect('Indicators',list(METRICS),default=['access','trust','participation','security'],format_func=lambda k:METRICS[k])
    if selected:
        st.line_chart({METRICS[k]:[r[k] for r in rows] for k in selected},height=320)
    st.subheader('Intersectional human security outcomes')
    st.write(GROUP_NOTE)
    pops=population_timeline(game)
    st.line_chart({k.replace('_',' ').title():[r[k] for r in pops] for k in INITIAL_GROUPS},height=260)
    st.caption('These are illustrative scenario proxies, not measured real-world outcomes.')
    with st.expander('What do the indicators mean?'):
        for k,label in METRICS.items():
            st.markdown(f'**{label}:** {INTERPRETATION[k]}')
    st.subheader('Recorded decisions')
    for event in game.history:
        with st.expander(f"Round {event['round']}: {event['choice']}"):
            st.write('Other actor responses:', '; '.join(event['responses']) or 'None recorded')
            st.write('Resulting world indicators:',event['metrics'])

with debrief:
    render_debrief(game)

with advisor:
    render_advisor(game)
