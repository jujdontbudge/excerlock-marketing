# ExcerLock product

What the app does, how to position it and how to show it on screen. Shared by every section.
Answers come from the captain's product description. **Needs confirmation** marks behaviour that isn't decided or built yet.

## Positioning and language

ExcerLock helps people hit their fitness goals by blocking the apps they choose unless they meet an exercise condition.

The goal is to use people's attachment to their phones as motivation to exercise: make app access depend on walking, getting to the gym, staying at the gym, or hitting a step goal. The captain describes this as using phone addiction to make people addicted to exercise and help them hit their goals. This is the product's intended purpose, not a guarantee of a particular personal result.

Do not call the blocked apps "scrolling apps" in marketing or briefs. Use "apps," "selected apps," or name the actual app. Why: the captain rejects that wording; ExcerLock is a fitness-goal tool, not a walking-only scrolling restriction.

Explain the four modes distinctly:
- **While walking:** selected apps are available while the person is actively walking.
- **While at the gym:** selected apps are available while the person is physically at the gym.
- **Gym arrival:** selected apps unlock once the person arrives at the gym.
- **Step goal:** selected apps unlock after the person reaches their chosen step goal.

Do not reduce the product description to walking only. A particular video can demonstrate one condition without redefining the whole app.

## What the app does

### 1. What does ExcerLock block?

Users select the apps they want ExcerLock to block.
Examples include TikTok, Instagram, and other apps the user chooses.
ExcerLock should not be described as blocking the entire phone unless that becomes an actual feature.

### 2. Which controls are included in the MVP?

Users create a condition with:

- The activity: gym or walking.
- The schedule: when locking starts and ends.
- The action that unlocks the selected apps.

The planned unlock conditions are:

- Arrive at the gym.
- Remain physically at the gym.
- Spend a chosen amount of time at the gym.
- Walk actively.
- Reach a step target.
- Walk for a chosen duration.

### 3. Can users lock access until they reach a gym?

Yes.

### 4. Can users keep access locked except while physically at a gym?

Yes.

### 5. Can users require a minimum amount of time at the gym?

Yes.

### 6. Can users require a number of steps before access unlocks?

Yes.

### 7. Can users require a walking duration before access unlocks?

Yes.

### 8. Can access remain available only while the user is actively walking?

Yes.
This is the main feature to emphasize first.

### 9. Does active-walking access work on a treadmill?

Treadmill walking is essential to the product.

- If the user is holding the phone while walking, movement detection works directly.
- If the phone is propped up on the treadmill, the user can complete a camera scan showing that they are on the treadmill and then open another app.
- The camera-based treadmill unlock is a useful product demonstration, but it should not become the main marketing message.

### 10. How quickly does ExcerLock detect walking?

**Needs confirmation:** the exact detection time has not been measured.

### 11. What counts as walking?

Ordinary walking movement counts, including pacing back and forth inside a room.
That indoor behavior is intentional: a user can walk rather than remain seated while using a selected app.

**Needs confirmation:** the exact movement threshold.

### 12. When does access relock after movement stops?

Plan around approximately five seconds for now.
This timing is not confirmed, so it must remain an internal planning assumption until the implemented behavior has been measured.

### 13. Can users combine location, time, steps, and active movement?

Not generally in the MVP.
Combined conditions may be added later.
Marketing should present one condition at a time and should not imply that users can build complex combinations now.

### 14. Which permissions are required?

The required permissions are expected to include:

- Screen Time or app-blocking authorization for selected apps.
- Motion and fitness access for walking detection.
- Location access for gym conditions.
- Camera access for the propped-phone treadmill scan.
- Apple Health access for step totals.

Apple Health is the confirmed source for step totals.
The final permission list and when each permission is requested still need to be verified against the finished MVP.

### 15. What happens when a required permission is disabled?

The affected apps remain unlocked.
ExcerLock should explain which permission is missing and how to restore it rather than trapping the user behind a condition that cannot be measured.

### 16. What emergency, accessibility, safety, and essential-app exceptions exist?

None are currently defined.
Selected-app blocking means the user can leave essential apps unblocked.

**Needs confirmation:** decide whether the MVP needs an emergency override, accessibility accommodations, a cooldown, or protection against accidentally locking access without a usable unlock route.

### 17. What can be shown on screen today?

Current demonstrable moments include:

- The treadmill camera scan unlocking access while the phone is propped up.
- Instagram being locked and then becoming available.
- A widget showing that selected apps are locked.
- The gym-arrival unlock being triggered while Apple Maps shows the phone inside the gym radius.
- A gym widget.


## Main offer

### 1. Which feature should receive the first marketing focus?

The first focus is access while actively walking or moving.
Treadmill walking is the clearest initial use case.

Arriving at the gym is the secondary focus.
The ability to choose when locking starts and ends is an important product control, but not necessarily the lead marketing message.

### 2. Is active walking the main product promise?

Yes.
Active walking is the main promise for the first marketing route.
Gym arrival, gym duration, step goals, and walking-duration goals are supporting modes.

### 3. Is treadmill use central enough for its own positioning?

Yes.
People already scroll while using treadmills, and the product turns that existing behavior into a condition for continued access.
Treadmill users are the first clear market to examine.

### 4. What existing desires does this satisfy?

The captain identified these existing desires:

- Reduce screen time.
- Exercise more.
- Walk consistently.
- Reach a daily step goal.
- Lose weight.
- Become fitter or look better.
- Stay consistent.
- Follow through on personal goals.
- Develop greater personal agency.


### 5. What is the primary outcome?

The larger desired outcomes are weight loss and greater personal agency.
The immediate outcomes ExcerLock can measure more directly are:

- More active walking.
- More completed steps or walking time.
- More consistent treadmill or gym behavior.
- Less seated use of selected apps.


### 6. What transformation can be understood without technical explanation?

The intended transformations are:

- Consistently reaching 10,000 or another chosen number of steps.
- Walking or using the treadmill more consistently.
- Attending the gym more consistently.
- Spending less time scrolling while seated.
- Following through on chosen fitness and attention goals.

### 7. Which technical details create trust?

Useful trust details are:

- Users choose which apps are blocked.
- Users choose when the condition is active.
- The product clearly shows what action unlocks access.
- Walking start, walking stop, progress, and relocking behavior are visible.
- Treadmill behavior is explained separately for a held phone and a propped phone.
- Gym location and duration rules are stated accurately.

Details that probably distract from the first explanation are internal sensor architecture, implementation terminology, and every available mode at once.

### 8. What should one post ask the viewer to do?

ExcerLock has not been released yet.
One post has only one action:

- Continue swiping to complete the story.
- Learn or remember the app name.
- Visit or follow the profile for the future release.
- Join a waitlist if one is created.

- Don't ask for several actions in one post. Why: each extra ask splits attention from the one action that matters.

### 9. What should not be combined in one post?

- Don't combine two unlock conditions in one explanation (for example gym arrival and active walking). Why: the viewer has to understand the mechanism in one glance; two conditions blur it.
- Don't explain every mode at once. Why: same reason.

## Showing the app on screen

### 1. Which screen communicates the product most quickly?

The strongest primary candidates are:

- A selected app visibly locked while a walking requirement is active.
- A widget clearly showing that selected apps are locked and what unlocks them.
- A visible transition from locked to available as walking begins.

The treadmill camera scan is a strong secondary demonstration, not the main message.

### 2. Can viewers understand what is locked?

They should be able to see the selected app or apps clearly.
This must be verified against the current interface at slideshow size.

### 3. Can viewers understand why it is locked?

The screen or widget should name the active walking, gym, step, or duration condition.
If the current interface does not make that clear, the product moment needs supporting context.

### 4. Can viewers understand what action is required?

The action should be visible as walking, reaching the gym, remaining at the gym, reaching a step target, or completing a walking duration.
Only one condition should appear in each demonstration.

### 5. Is progress visible?

Widgets and product screens should show progress where the condition has measurable progress, such as steps, walking duration, or gym duration.

**Needs confirmation:** identify which progress states are already implemented and readable in a screenshot.

### 6. Is active walking visible?

It should be visible through an active state, movement indicator, or unlock transition.

**Needs confirmation:** identify the exact current screen or widget state.

### 7. Is the locked-to-available transition visible?

The captain says Instagram being locked and then unlocked can be demonstrated.

### 8. Is relocking after movement stops visible?

It should be demonstrable if the provisional five-second behavior is implemented.
**Needs confirmation:** the exact relock timing.

### 9. Can a notification communicate the product state?

Yes, this is planned.
ExcerLock notifications will tell users that:

- Their selected apps are locked.
- They reached a step milestone.
- Their progress changed.
- They reached a gym-time milestone.

The notification format is a strong candidate because Pedro specifically observed it introducing apps naturally.
The exact notification wording and visual design still need to be created.

### 10. Is there a meaningful widget?

Yes.
The captain identified a locked-state widget and a gym widget as demonstrable product moments.
Their readability and exact information still need visual review.

### 11. Is the interface readable in a vertical slideshow?

**Needs confirmation through visual review.**
Important text, app identity, progress, and the required action must remain readable on a phone screen without zooming.

### 12. What private information must be replaced?

Use demonstration data for:

- Exact home or gym locations.
- Map history.
- Health and step history.
- Personal schedules.
- Notifications from unrelated apps.
- Account names and profile images.
- Any camera frame containing another person without permission.
