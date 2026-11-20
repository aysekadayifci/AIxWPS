import streamlit as st

def render_information(page):
    if page == 'about':
        st.title('About AI × WPS')
        st.subheader('Reimagining Peace and Security in a Technologically Transforming World')
        st.write("AI × WPS is an interactive simulation and experiential learning platform designed to explore the complex relationships between artificial intelligence, emerging technologies, gender, peace, and security. Emerging technologies transform warfare, political power, humanitarian action, governance and everyday life, creating opportunities for peacebuilding as well as new forms of insecurity, exclusion and inequality.")
        st.write("Through immersive scenarios, players assume stakeholder roles, navigate competing priorities, make decisions under uncertainty, and examine immediate, delayed and unintended consequences. The objective is not simply to win a game, but to consider whose security, rights, knowledge and participation are prioritized.")
        sections = {
            'Women, Peace and Security and intersectionality': 'Participation, Protection, Prevention, and Relief & Recovery provide interconnected analytical lenses. The platform retains the WPS commitment to women’s rights and meaningful participation while examining diverse experiences of women, men, girls, boys and gender-diverse people, including intersecting identities, capacities and barriers.',
            'Human security and emerging technologies': 'Explore digital sovereignty, AI-assisted decision-making, conflict prevention, humanitarian action, surveillance, and the interdependence of critical infrastructure and everyday security.',
            'Learning objectives': 'Practice ethical reasoning, systems thinking, stakeholder analysis, assessment of uncertainty, and critical evaluation of technological trade-offs. Compare aggregate indicators with distributional consequences.',
            'Methodology and limitations': 'The current Ardin scenario uses fictional geography, synthetic populations and rule-based effects. Indicator scores are illustrative proxies, not percentages or validated predictions. Six crisis milestones are fixed; role choices and briefings respond to earlier decisions. Broader subgroup and sector effects are not yet fully modeled.',
            'Role of artificial intelligence': 'The optional AI advisor analyzes visible simulation information without altering the game state. AI explanations can be incorrect and are not legal advice or verified evidence. API use requires a locally configured key and sends visible game context to the provider. Do not provide sensitive personal data. Document retrieval and verified citations are planned.',
            'Research and development': 'An academic educational research prototype drawing on Women, Peace and Security, human security, intersectional gender analysis and peacebuilding. Creator biography and formal acknowledgments can be added following approval.'}
        for title,body in sections.items():
            with st.expander(title): st.write(body)
    elif page == 'guide':
        st.title('How to Play')
        for title,body in [('Choose a scenario and role','Open Scenarios, select The Humanitarian Algorithm and choose one of six actors. Read your mandate and objectives.'),('Explore the world','Use the Strategy Room and Living Atlas to inspect Camp 17, its facilities and operational layers.'),('Make decisions','Read the crisis briefing and options, reflect on the trade-offs, and confirm your choice. Review actor reactions and consequences before continuing.'),('Interpret indicators','Open the explanations below the indicator cards. Scores are illustrative; lower exclusion and tension are preferable.'),('Reflect and debrief','Use the population, WPS and governance analysis sections. The final report unlocks after six rounds. The optional AI advisor can help interpret visible information.')]:
            st.subheader(title); st.write(body)
        st.info('Navigation preserves the current browser session. Restarting or closing the session may lose progress; use available downloads. Persistent saved games are not yet implemented.')
    else:
        st.title('For Educators')
        st.write('Use AI × WPS to connect course concepts to complex decisions, competing mandates and uncertain information.')
        st.subheader('Suggested classroom activity')
        st.markdown('1. Assign different roles in Ardin.\n2. Ask students to justify decisions before viewing consequences.\n3. Compare outcomes and actor perspectives.\n4. Evaluate decisions through the four WPS pillars and intersectional analysis.\n5. Submit a reflective debrief grounded in course readings.')
        st.subheader('Assessment')
        st.write('Assess reasoning, evidence use, awareness of uncertainty, equity, and ethical trade-offs rather than maximizing scores.')
        st.warning('Temporary student accounts, instructor monitoring, secure document uploads and multiplayer are planned, not available in this release. Do not deploy with identifiable student data until appropriate privacy and security review.')
