"""AI x WPS: Republic of Ardin, solo simulation engine v0.2.
Run in Spyder with F5. Standard-library only, Python 3.11+.
All numerical rules are illustrative educational assumptions.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import random

METRICS = {
    'access': 'Humanitarian access', 'trust': 'Community trust',
    'participation': "Women's participation", 'security': 'Civilian security',
    'exclusion': 'Digital exclusion (lower better)', 'privacy': 'Data privacy',
    'tension': 'Political tension (lower better)',
}

ACTORS = {
    'humanitarian': ('UN Humanitarian Coordinator', 'Deliver aid while protecting humanitarian principles.'),
    'government': ('Government Minister', 'Maintain legitimacy, administrative control, and service delivery.'),
    'women': ("Women's Coalition Leader", 'Secure meaningful influence and protect excluded groups.'),
    'military': ('Security Commander', 'Prevent attacks and preserve operational authority.'),
    'technology': ('Technology Provider', 'Keep systems operational and retain institutional contracts.'),
    'community': ('Community Representative', 'Protect residents, local autonomy, and reliable access to aid.'),
}

@dataclass
class ScheduledEffect:
    due_round: int
    changes: dict[str, int]
    description: str
    groups: dict[str, int] = field(default_factory=dict)

@dataclass
class Action:
    title: str
    changes: dict[str, int]
    group_changes: dict[str, int] = field(default_factory=dict)
    delayed: list[tuple[int, dict[str, int], str, dict[str, int]]] = field(default_factory=list)
    note: str = ''

@dataclass
class Round:
    title: str
    briefing: str
    choices: list[Action]
    signal: str

ROUNDS = [
    Round('The Aid Crisis', 'Camp 17 has an aid-registration backlog. An AI system could accelerate allocation.', [
        Action('Deploy AI registration immediately', {'access': 13, 'exclusion': 10, 'trust': -6}, {'undocumented_women': -12}, [(3, {'trust': -5}, 'Unresolved registration appeals accumulate.', {'undocumented_women': -5})]),
        Action('Pilot AI with manual alternatives', {'access': 7, 'exclusion': -5, 'trust': 3}, {'undocumented_women': 4}, [(3, {'access': 3}, 'Manual appeals resolve some earlier registration gaps.', {'undocumented_women': 3})]),
        Action('Pause for independent assessment', {'access': -5, 'privacy': 6, 'trust': 2}, {'undocumented_women': 2}, [(3, {'access': -4}, 'The registration backlog worsens during the pause.', {})]),
    ], 'Technology provider reports 88% accuracy, but has not supplied subgroup performance data.'),
    Round('The Missing Population', 'Local groups report undocumented residents and women without connectivity are being missed.', [
        Action('Give women-led organizations authority to redesign eligibility', {'participation': 14, 'trust': 7, 'exclusion': -10, 'access': -3}, {'undocumented_women': 13}, [(4, {'access': 7}, 'Community-led corrections improve registration quality.', {'undocumented_women': 5})]),
        Action('Maintain eligibility rules to protect throughput', {'access': 5, 'participation': -5, 'exclusion': 6}, {'undocumented_women': -9}, [(4, {'trust': -7}, 'Excluded residents organize a public complaint.', {})]),
        Action('Send mobile teams without changing governance', {'access': 5, 'exclusion': -7, 'participation': 1}, {'undocumented_women': 7}, [(4, {'access': -2}, 'Mobile teams require sustained staffing.', {})]),
    ], 'Women-led organizations have household-level information unavailable to the central database.'),
    Round('The Security Warning', 'An AI-assisted assessment flags possible armed activity near Camp 17 using imagery three days old.', [
        Action('Restrict access immediately', {'security': 6, 'access': -13, 'trust': -8, 'tension': 7}, {'camp_residents': -8}, [(5, {'security': -3}, 'Prolonged restrictions increase instability around the camp.', {})]),
        Action('Verify through multiple independent sources', {'security': 2, 'trust': 5, 'participation': 4, 'access': -3}, {'camp_residents': 2}, [(5, {'security': 4}, 'Verified local reporting improves protective planning.', {})]),
        Action('Ignore the assessment', {'access': 4, 'security': -7, 'tension': 3}, {}, [(5, {'security': -4}, 'Uninvestigated warnings leave a preparedness gap.', {})]),
    ], 'The reported 76% confidence is not a probability that an attack will occur.'),
    Round('The Data Request', 'The government requests named humanitarian records for security screening.', [
        Action('Transfer full identifiable records', {'security': 4, 'privacy': -18, 'trust': -12, 'tension': 6}, {'undocumented_women': -10}, [(6, {'access': -7}, 'Residents avoid services after learning of data sharing.', {'undocumented_women': -7})]),
        Action('Negotiate a narrow, independently reviewed protocol', {'privacy': 4, 'trust': 4, 'security': 1, 'access': -2}, {'undocumented_women': 3}, [(6, {'trust': 3}, 'Clear safeguards improve willingness to register.', {})]),
        Action('Refuse any data sharing', {'privacy': 8, 'security': -2, 'tension': 10, 'trust': 3}, {}, [(6, {'access': -5}, 'Government obstruction slows deliveries.', {})]),
    ], 'A government legal adviser privately questions the scope of the request.'),
    Round('The Information Crisis', 'Conflicting claims about the AI system spread through local media.', [
        Action('Publish audited evidence and hold community briefings', {'trust': 9, 'participation': 5, 'access': -2, 'tension': -4}, {'camp_residents': 4}, []),
        Action('Issue a short institutional reassurance', {'trust': -2, 'tension': 2, 'access': 3}, {}, [(6, {'trust': -4}, 'Unanswered questions deepen skepticism.', {})]),
        Action('Suppress disputed claims through emergency controls', {'trust': -12, 'privacy': -6, 'tension': 10, 'security': 2}, {'camp_residents': -5}, []),
    ], 'Some viral allegations are false; others describe real registration failures.'),
    Round('The Humanitarian Decision', 'A final aid convoy and protection plan must be approved under severe time pressure.', [
        Action('Joint plan with community oversight and independent safeguards', {'access': 9, 'participation': 8, 'trust': 6, 'security': 1}, {'undocumented_women': 6, 'camp_residents': 4}, []),
        Action('Centralized rapid delivery under security command', {'access': 12, 'security': 5, 'participation': -8, 'trust': -6, 'tension': 5}, {'undocumented_women': -5}, []),
        Action('Suspend operations until political guarantees are secured', {'access': -12, 'privacy': 4, 'security': -3, 'tension': 5}, {'camp_residents': -9}, []),
    ], 'No institution can fully control how other actors respond.'),
]


# Role-specific decisions share the established numerical outcome pathways.
# Mapping is explicit: a distinct institutional action may produce the same
# illustrative effect family as an existing humanitarian action. This is a
# design assumption, not an empirically validated equivalence.
ROLE_DECISIONS = {
 'government': [
  [('Mandate national AI registration across agencies','Offer a supervised registration pilot with appeals','Commission a public procurement and rights review'),('Speed and visibility may exclude undocumented residents.','A staged rollout allows corrections but demands coordination.','A review improves oversight but postpones deliveries.')],
  [('Authorize community-led eligibility revision','Keep centralized eligibility criteria','Fund mobile civil-registration teams'),('Sharing authority challenges ministry control.','Uniform rules maintain throughput but can institutionalize exclusions.','Mobile services reach people outside the digital system.')],
  [('Impose a temporary security perimeter','Request independent verification before restrictions','Reject the warning as unreliable'),('Movement restrictions may obstruct humanitarian access.','Verification requires time and interagency cooperation.','Dismissal may leave security institutions acting alone.')],
  [('Order transfer of all beneficiary records','Approve a limited independently reviewed data protocol','Block security access to aid records'),('Broad disclosure risks loss of confidentiality.','Limited disclosure requires legal oversight and negotiation.','Refusal may provoke institutional conflict.')],
  [('Publish an independent audit and hold public hearings','Issue a ministerial reassurance','Restrict circulation of disputed reports'),('Scrutiny may expose government failures.','Reassurance is fast but may not resolve grievances.','Information controls may undermine public trust.')],
  [('Negotiate a joint humanitarian delivery agreement','Place final delivery under centralized security command','Suspend delivery until guarantees are secured'),('Shared oversight can improve legitimacy.','Centralization may speed operations but exclude some households.','Delay may preserve leverage but increases unmet needs.')]],
 'women': [
  [('Demand immediate inclusive deployment','Negotiate a pilot with manual access','Call for an independent gender and accessibility assessment'),('Fast implementation may reproduce unseen bias.','A pilot gives community groups a chance to correct exclusion.','Assessment can reveal gaps but delays aid.')],
  [('Lead redesign of eligibility and appeals','Accept existing criteria to preserve immediate throughput','Organize mobile registration and outreach teams'),('Meaningful authority can change exclusionary rules.','Compromise may leave undocumented households behind.','Outreach helps access without necessarily changing power.')],
  [('Support temporary restrictions for immediate safety','Demand triangulation with women-led community reporting','Publicly challenge the warning as unsubstantiated'),('Restrictions may increase protection barriers.','Independent testimony can test uncertain intelligence.','A categorical dismissal may miss real risks.')],
  [('Accept comprehensive data sharing to expedite screening','Insist on narrow consent-aware independent oversight','Mobilize opposition to any identifiable disclosure'),('Disclosure may expose survivors and marginalized residents.','Safeguards require negotiating power and enforcement.','Opposition can protect privacy but escalate tensions.')],
  [('Publish verified testimonies and hold inclusive briefings','Issue a short coalition reassurance','Call for emergency restrictions on disputed information'),('Evidence-based engagement may build trust.','Reassurance may not answer documented grievances.','Suppression can harm dissent and participation.')],
  [('Join an oversight-led convoy plan','Accept a security-led rapid distribution','Withhold coalition endorsement pending protections'),('Participation can shape eligibility and delivery.','Speed may bypass unregistered households.','Non-cooperation may slow urgently needed supplies.')]],
 'military': [
  [('Secure immediate AI-led distribution corridors','Support a controlled pilot with manual verification','Delay deployment pending threat and privacy review'),('Speed may create exclusion and trust risks.','Pilot procedures permit checking without full rollout.','Review reduces some risks but slows assistance.')],
  [('Share operational control with community registration groups','Enforce existing identity requirements','Support escorted mobile registration teams'),('Shared authority may improve inclusion but complicate command.','Strict criteria can exclude undocumented residents.','Mobile teams can improve access under security constraints.')],
  [('Close access routes based on the AI warning','Conduct joint verification with civilian sources','Disregard the assessment and maintain routes'),('Precautionary restrictions can disrupt aid.','Verification balances uncertainty with preparedness.','Ignoring the signal can create a readiness gap.')],
  [('Request full identifiable humanitarian records','Negotiate limited, independently overseen access','Withdraw the data request'),('Broad access may undermine humanitarian confidentiality.','Limited access involves oversight and operational compromises.','Withdrawal may reduce surveillance risk but strain coordination.')],
  [('Release independently checked security evidence','Issue a short security assurance','Restrict circulation of disputed reports'),('Evidence can counter rumors but requires transparency.','Assurance alone may not resolve public concerns.','Controls can create backlash.')],
  [('Agree to a joint civilian-led convoy plan','Direct a centralized security-led delivery','Suspend the convoy pending enforceable guarantees'),('Shared planning distributes authority.','Centralized command can accelerate delivery with inclusion costs.','Suspension may increase immediate humanitarian need.')]],
 'technology': [
  [('Launch the registration platform immediately','Deploy a limited pilot with offline fallback','Pause rollout for external audit'),('Unverified subgroup accuracy risks systematic exclusion.','A pilot generates feedback but limits scale.','Auditing strengthens assurance but delays deployment.')],
  [('Give affected communities authority over eligibility design','Retain the existing automated eligibility model','Deploy mobile offline enrollment devices'),('Co-design may require rewriting the model.','Throughput may conceal unequal error rates.','Offline devices help access without changing rules.')],
  [('Recommend automatic access restrictions from the alert','Require independent human verification of the alert','Withdraw the warning without further review'),('An unverified alert should not become an automatic order.','Human verification can challenge uncertain classifications.','Withdrawal can create a preparedness gap.')],
  [('Provide complete identified records to government','Implement minimized access with independent audit logs','Refuse all identifiable data exports'),('Broad disclosure creates secondary-use risk.','Minimization requires technical and legal controls.','Refusal can cause operational conflict.')],
  [('Publish model limitations, audits, and error reports','Issue a short corporate assurance','Request suppression of disputed claims'),('Transparent reporting may expose shortcomings.','Assurance may be perceived as evasive.','Suppression can undermine credibility.')],
  [('Support jointly governed distribution with appeals','Optimize centralized rapid distribution','Suspend the system pending guarantees'),('Joint governance may reduce exclusion.','Optimization can sacrifice fairness for throughput.','Suspension may slow urgent aid.')]],
 'community': [
  [('Accept immediate automated registration','Organize a monitored pilot with offline options','Demand an independent community needs assessment'),('Speed may bypass neighbors lacking documentation.','A monitored pilot enables feedback and appeals.','Assessment can reveal gaps but slows aid.')],
  [('Co-lead redesign of eligibility criteria','Accept existing rules for immediate delivery','Organize neighborhood mobile-registration support'),('Resident authority can challenge exclusion.','Existing rules may leave neighbors unserved.','Local support may help without changing governance.')],
  [('Request immediate access restrictions','Seek joint verification with local witnesses','Reject the warning and keep routes open'),('Restrictions can isolate vulnerable households.','Local evidence can test uncertain security claims.','Dismissal may leave real risks unaddressed.')],
  [('Agree to share all registration data','Demand narrow independent oversight of disclosure','Organize refusal of any identifiable sharing'),('Broad sharing may expose households to surveillance.','Oversight protects some interests but takes time.','Refusal may trigger government retaliation.')],
  [('Hold open meetings and publish verified accounts','Offer brief community reassurance','Demand emergency removal of disputed claims'),('Open meetings may surface difficult truths.','Reassurance can leave grievances unresolved.','Censorship can reduce trust.')],
  [('Co-design the convoy and monitoring plan','Accept centralized security delivery','Withhold cooperation until safeguards are secured'),('Shared planning may improve access and legitimacy.','Rapid delivery may miss unregistered neighbors.','Withholding cooperation may delay assistance.')]],
}

ROLE_ROUND_CONTEXT = {
 'humanitarian': ['You must reconcile urgency with impartial access and protection.', 'Registration complaints now test whether your initial safeguards actually worked.', 'Security officials may act even without your consent; decide how to handle uncertainty.', 'Your agency holds sensitive records and faces a politically consequential request.', 'Public allegations include both errors and genuine grievances from previous rounds.', 'Your final plan must balance delivery speed, protection, and local oversight.'],
 'government': ['The cabinet wants visible progress and expects you to defend public spending.', 'Administrative legitimacy is at stake as excluded residents challenge the rules.', 'You face pressure to demonstrate control without undermining civilian services.', 'You must weigh security requests against confidentiality and public legitimacy.', 'Your ministry must respond to criticism without erasing legitimate complaints.', 'You are accountable for a politically visible final delivery decision.'],
 'women': ['Your coalition has local knowledge but limited formal control over procurement.', 'Affected households ask whether you can secure actual authority, not symbolic consultation.', 'Women and men report different exposure to checkpoints and profiling.', 'Survivors and undocumented households fear secondary uses of registration data.', 'Your coalition must decide how to present verified testimony amid rumors.', 'Your coalition must decide whether to endorse a final plan that may exclude some residents.'],
 'military': ['Your unit is asked to secure routes while aid agencies insist on civilian safeguards.', 'Identity controls may assist screening but also block residents without papers.', 'The AI warning is uncertain and based on dated imagery.', 'Your command seeks information but does not automatically have authority to obtain it.', 'Rumors threaten cooperation between security forces and residents.', 'You must weigh operational control against humanitarian independence.'],
 'technology': ['Your vendor has advertised strong overall accuracy without subgroup validation.', 'Complaints suggest the training data may underrepresent undocumented households.', 'An alert generated by your system is being treated as actionable intelligence.', 'Your company is asked to enable secondary use of sensitive humanitarian data.', 'Public criticism creates pressure to disclose limitations and error rates.', 'You must choose whether to prioritize throughput or accountable governance.'],
 'community': ['Residents need aid but some fear registration and loss of autonomy.', 'Neighbors report that people without documents or connectivity were missed.', 'Residents disagree about safety and the cost of movement restrictions.', 'People worry that aid records could be used for surveillance.', 'Community trust is strained by both misinformation and documented exclusion.', 'Residents need urgent deliveries but want a say in distribution rules.'],
}

ROLE_RESPONSES = {
 'government': 'Your choice changes the ministry’s relationship with aid agencies, security institutions, and residents.',
 'women': 'Your choice changes how the coalition can exercise influence and protect people overlooked by centralized systems.',
 'military': 'Your choice changes the balance between security authority, humanitarian access, and civilian trust.',
 'technology': 'Your choice changes the provider’s accountability, system legitimacy, and relationships with institutional clients.',
 'community': 'Your choice changes the community’s negotiating position and residents’ confidence in the response.',
 'humanitarian': 'Your choice changes humanitarian access, institutional cooperation, and protection safeguards.',
}

class Game:
    def __init__(self, seed: int = 17, role: str = 'humanitarian'):
        if role not in ACTORS:
            raise ValueError('Unknown role')
        self.rng = random.Random(seed)
        self.role = role
        self.round_number = 0
        self.metrics = dict(access=45, trust=50, participation=35, security=55,
                            exclusion=45, privacy=60, tension=40)
        self.groups = {'undocumented_women': 45, 'camp_residents': 50, 'host_community': 50}
        self.pending: list[ScheduledEffect] = []
        self.history: list[dict] = []
        self.audit: list[str] = []
        self.actor_positions = {key: 50 for key in ACTORS}
        self.last_actor_actions: list[str] = []
        self.hidden_threat = self.rng.choice(['credible', 'overstated'])

    @staticmethod
    def clamp(value: int) -> int:
        return max(0, min(100, value))

    def apply(self, changes: dict[str, int], group_changes: dict[str, int], source: str):
        for key, amount in changes.items():
            self.metrics[key] = self.clamp(self.metrics[key] + amount)
            self.audit.append(f'Round {self.round_number}: {source}: {key} {amount:+d}')
        for key, amount in group_changes.items():
            self.groups[key] = self.clamp(self.groups[key] + amount)
            self.audit.append(f'Round {self.round_number}: {source}: group {key} {amount:+d}')

    def start_round(self):
        if self.round_number >= len(ROUNDS):
            raise RuntimeError('Simulation finished')
        self.round_number += 1
        due = [e for e in self.pending if e.due_round == self.round_number]
        self.pending = [e for e in self.pending if e.due_round != self.round_number]
        for effect in due:
            self.apply(effect.changes, effect.groups, effect.description)
        return ROUNDS[self.round_number - 1]

    def available_choices(self):
        base = ROUNDS[self.round_number - 1].choices
        if self.role == 'humanitarian':
            from educational_content import HUMANITARIAN_CHOICE_CONTEXTS
            contexts=HUMANITARIAN_CHOICE_CONTEXTS[self.round_number-1]
            return [(a.title, contexts[i]) for i,a in enumerate(base)]
        titles, contexts = ROLE_DECISIONS[self.role][self.round_number - 1]
        return list(zip(titles, contexts))

    def adaptive_context(self):
        idx = self.round_number - 1
        lines = [ROLE_ROUND_CONTEXT[self.role][idx]]
        if self.history:
            prev = self.history[-1]
            lines.append(f"Previously, as {ACTORS[self.role][0]}, you chose: {prev['choice']}.")
            if prev['responses']:
                lines.append('Other actors responded: ' + ' '.join(prev['responses']))
            if self.metrics['trust'] < 45:
                lines.append('Community trust is now strained; residents may question further institutional assurances.')
            elif self.metrics['trust'] >= 60:
                lines.append('Relatively stronger community trust creates an opening for consultation.')
            if self.metrics['exclusion'] >= 50:
                lines.append('Digital exclusion remains elevated; documentation and access barriers require attention.')
            if self.metrics['tension'] >= 55:
                lines.append('Political tensions are elevated, increasing the risk of institutional obstruction.')
            if self.metrics['participation'] < 35:
                lines.append('Meaningful participation has weakened; decisions may lack representation of affected residents.')
            if self.metrics['privacy'] < 50:
                lines.append('Privacy safeguards have deteriorated; residents may hesitate to share information.')
            if self.metrics['access'] < 45:
                lines.append('Humanitarian access is under pressure, making delays especially consequential.')
            due = [e for e in self.pending if e.due_round == self.round_number]
            if due:
                lines.append('Earlier decisions have generated consequences that now require attention.')
        return '\n\n'.join(lines)

    def role_briefing(self, round_data: Round) -> str:
        # A role receives a bounded institutional lens; not all actors know the hidden threat.
        viewpoints = {
            'humanitarian': 'Your mandate is humanitarian access and impartial protection.',
            'government': 'Your cabinet expects stability and visible service delivery.',
            'women': 'Your coalition prioritizes voice, safety, and undocumented households.',
            'military': 'Your command is under pressure to prevent armed infiltration.',
            'technology': 'Your firm wants reliable deployment and protection from reputational risk.',
            'community': 'Residents want assistance without surveillance or coercion.',
        }
        return viewpoints[self.role] + '\nInformation available: ' + round_data.signal

    def other_actor_responses(self, choice_index: int):
        # Bounded rule-driven AI stand-ins: objectives, not generative-language AI.
        # Each response is independent of the hidden threat except security's response in round 3.
        self.last_actor_actions = []
        r = self.round_number
        if r == 1:
            if choice_index == 0:
                self.last_actor_actions.append('Technology provider promotes rapid rollout.')
                self.last_actor_actions.append("Women's coalition requests an appeals mechanism.")
                self.apply({'participation': -2}, {'undocumented_women': -3}, 'Institutional response: weak appeals')
            elif choice_index == 1:
                self.last_actor_actions.append('Community representatives offer pilot feedback.')
                self.apply({'trust': 2}, {}, 'Institutional response: pilot cooperation')
            else:
                self.last_actor_actions.append('Government minister criticizes delays.')
                self.apply({'tension': 5}, {}, 'Institutional response: government pressure')
        elif r == 2:
            if choice_index == 0:
                self.last_actor_actions.append('Government administrators resist sharing decision authority.')
                self.apply({'tension': 5}, {}, 'Institutional response: bureaucratic resistance')
            elif choice_index == 1:
                self.last_actor_actions.append("Women's coalition publicly challenges the eligibility rules.")
                self.apply({'trust': -4}, {}, 'Institutional response: exclusion challenge')
            else:
                self.last_actor_actions.append('Technology provider offers limited technical support.')
        elif r == 3:
            if choice_index == 0:
                self.last_actor_actions.append('Humanitarian agencies protest blanket restrictions.')
                self.apply({'access': -3}, {}, 'Institutional response: access dispute')
            elif choice_index == 1:
                self.last_actor_actions.append('Security command accepts a short verification window.')
                if self.hidden_threat == 'credible':
                    self.apply({'security': -4}, {}, 'Threat pressure during verification')
                else:
                    self.apply({'security': 2}, {}, 'Avoided unnecessary security escalation')
            else:
                self.last_actor_actions.append('Security command acts independently of the aid agency.')
                self.apply({'trust': -5}, {}, 'Institutional response: unilateral security action')
        elif r == 4:
            if choice_index == 1:
                self.last_actor_actions.append('Government legal adviser supports limited disclosure safeguards.')
                self.apply({'tension': -3}, {}, 'Institutional response: negotiated protocol')
            elif choice_index == 2:
                self.last_actor_actions.append('Government threatens to withhold operating permits.')
                self.apply({'access': -3}, {}, 'Institutional response: permit pressure')
            else:
                self.last_actor_actions.append('Community representatives question the confidentiality of aid records.')
        elif r == 5:
            if choice_index == 0:
                self.last_actor_actions.append("Women's coalition supplies independently verified testimonies.")
                self.apply({'trust': 3}, {}, 'Institutional response: verified testimony')
            elif choice_index == 2:
                self.last_actor_actions.append('Community groups organize against censorship.')
                self.apply({'tension': 5}, {}, 'Institutional response: censorship backlash')
            else:
                self.last_actor_actions.append('Local journalists continue investigating unresolved claims.')
        else:
            if choice_index == 0 and self.metrics['tension'] >= 55:
                self.last_actor_actions.append('Security command imposes last-minute conditions on the convoy.')
                self.apply({'access': -5}, {}, 'Institutional response: security conditions')
            elif choice_index == 1:
                self.last_actor_actions.append("Women's coalition warns that rapid delivery misses unregistered households.")
            else:
                self.last_actor_actions.append('Community representatives demand an emergency access plan.')

    def decide(self, choice_index: int):
        if self.round_number < 1 or self.round_number > len(ROUNDS):
            raise RuntimeError('Start a round first')
        if len(self.history) == self.round_number:
            raise RuntimeError('This round already has a decision')
        round_data = ROUNDS[self.round_number - 1]
        if not isinstance(choice_index, int) or not 0 <= choice_index < len(round_data.choices):
            raise ValueError('Choose a valid action number')
        audit_start = len(self.audit)
        action = round_data.choices[choice_index]
        display_choice = self.available_choices()[choice_index][0]
        self.apply(action.changes, action.group_changes, 'Player: ' + display_choice)
        for delay, changes, description, groups in action.delayed:
            self.pending.append(ScheduledEffect(self.round_number + delay - 1, changes, description, groups))
        self.other_actor_responses(choice_index)
        # Feedback loops: structural conditions amplify or reduce risks.
        if self.metrics['exclusion'] >= 55:
            self.apply({'trust': -3}, {'undocumented_women': -3}, 'Feedback: exclusion erodes trust')
        if self.metrics['participation'] >= 55 and self.metrics['exclusion'] <= 40:
            self.apply({'trust': 2}, {}, 'Feedback: participation improves legitimacy')
        # Tipping thresholds create non-linear institutional responses.
        if self.metrics['tension'] >= 70:
            self.apply({'access': -4}, {}, 'Threshold: high tension disrupts operations')
        if self.metrics['trust'] <= 30:
            self.apply({'access': -4}, {}, 'Threshold: low trust undermines registration')
        self.history.append({'round': self.round_number, 'title': round_data.title,
                             'choice': display_choice, 'base_pathway': action.title, 'role': self.role, 'metrics': self.metrics.copy(),
                             'groups': self.groups.copy(), 'responses': self.last_actor_actions.copy(), 'role_impact': ROLE_RESPONSES[self.role], 'audit_entries': self.audit[audit_start:].copy()})
        return action

    def report(self):
        print('\n--- ARDIN SITUATION REPORT ---')
        for key, name in METRICS.items():
            print(f'{name}: {self.metrics[key]}/100')
        print('Population access/well-being (illustrative):')
        for key, value in self.groups.items():
            print(f'  {key.replace("_", " ").title()}: {value}/100')

    def debrief(self):
        print('\n=== WPS DEBRIEF ===')
        for entry in self.history:
            print(f'Round {entry["round"]}: {entry["choice"]}')
        self.report()
        print('\nSecurity warning (revealed after play):', self.hidden_threat)
        print('Questions: Who gained decision-making authority? Who was excluded?')
        print('Which AI claims were uncertain, and what evidence was missing?')
        print('Where did actor resistance or delayed effects change outcomes?')
        print('How did outcomes differ for undocumented women and other residents?')
        print('\nNOTE: All numerical effects are illustrative educational assumptions.')
        print('AI-controlled actors here use transparent rules, not a language model.')


def play(seed: int = 17, role: str = 'humanitarian'):
    game = Game(seed=seed, role=role)
    print('AI × WPS — REPUBLIC OF ARDIN — ENGINE v0.2')
    print('Playing as:', ACTORS[role][0])
    print('Other actors are controlled by transparent simulation rules.')
    game.report()
    for _ in ROUNDS:
        current = game.start_round()
        print(f'\nROUND {game.round_number}: {current.title}')
        print(current.briefing)
        print(game.role_briefing(current))
        for i, action in enumerate(current.choices, 1):
            print(f'  {i}. {action.title}')
        while True:
            try:
                choice = int(input('Choose 1, 2, or 3: ')) - 1
                if not 0 <= choice < len(current.choices):
                    raise ValueError
                break
            except ValueError:
                print('Please enter 1, 2, or 3.')
        action = game.decide(choice)
        print('\nYou chose:', action.title)
        for response in game.last_actor_actions:
            print('OTHER ACTOR:', response)
        game.report()
    game.debrief()
    try:
        from reporting import export_report
        paths = export_report(game, folder="reports")
        print("\nDOWNLOADABLE REPORT FILES:")
        for path in paths:
            print(" ", path)
        print("Open ardin_report.html in Safari or Chrome. Use Print > Save as PDF for a PDF copy.")
    except Exception as exc:
        print("Report export failed:", exc)
    return game


if __name__ == '__main__':
    play()
