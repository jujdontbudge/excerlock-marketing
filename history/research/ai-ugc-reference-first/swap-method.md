# Person swap on a real reference photo (working notes)

How we apply Kristian Jennings' method (see `video.md`) to make a character from one real photo. Working notes from the G66 tests (`raw/recast/g66/`), 2026-10-02.

## The method
- Attach one image only: the real reference photo, sent as the photo to edit. Why: v1 attached our character, physique and phone-case references, and the model invented a different gym, camera and pose.
- Write a short plain-text edit prompt: keep everything, change only who she is, add a few of her own accessories, remove any caption. Why: this is what the video does; long wish-lists read as "make a new photo".
- State the exact pose in words. Why: v2 kept the gym but had her stand up; v3 kept the pose once it was spelled out.
- Use Nano Banana Pro (`gemini-3-pro-image`) at 1K, its lowest size.
- Check every result side by side with the original, never on its own. Why: a standalone review called v1's different gym "intact".

## Facial expression is everything (captain, 2026-10-02)
- Analyse the reference face before writing the prompt: head angle and tilt, chin, where the pupils point, eyelids, brows, which mouth corner lifts, lip press or pout, cheek, dimple and mood. Copy it into the prompt in that detail. Why: the expression carries the attitude of the post; v3 swapped G66's playful upward side-eye smirk for a calm look at the phone, and the photo lost its character.
- Check the expression in a face crop of the original and the edit side by side.
- Don't write a generic "small smile, looking at the phone". Why: that is what replaced the real expression on v3.

## Look
- Young: state an age of 18 to 19 with youthful features. Why: "young woman" came out early 20s.
- Blonde: name the shade and say no dark roots. Why: "honey-blonde with slightly darker roots" came out bronde.
