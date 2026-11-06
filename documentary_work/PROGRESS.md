# Transistor documentary — durable production state

The user wants one complete video, with a five-second hook, different paper-cut image per narrated sentence, deep English voice `voice-01`, smooth cross-dissolves and no excessive gaps. They previously approved using this public GitHub repository/branch for video delivery because sandbox downloads failed. Generated assets saved only in the sandbox were repeatedly lost between sessions, so the source pairs below are committed and backed up on the same public branch. They are therefore publicly accessible.

## Verified material

- `documentary/hook_smooth_scenes_01-19.mp4`: completed hook and scenes 1–19.
- `documentary/scenes_20-29.mp4`: completed scenes 20–29.
- `documentary_work/scenes/scene_50.jpg` through `scene_59.jpg` and matching `voice_50.mp3` through `voice_59.mp3`: 10 verified source pairs.
- All earlier source files for scenes 30–49 and 60–150, including the previously regenerated 130–139, were lost when a previous sandbox was reset. They are NOT available. Do not claim they are ready. The older long video repeats images and must not be used as a substitute.

## Remaining work

Recreate 30–49, 60–150, a total of 111 image/voice scene pairs. At most 10 images and 10 speech clips may be generated per turn, so at least 12 further turns are needed. Refer to the original 150-scene script and image prompts in the conversation. Write all assets to `documentary_work/scenes/`, then convert PNG images to 1280x720 JPEG quality 88, verify files, and commit and push them to the current branch after each batch to avoid another reset destroying work. Note that the repository is public.

When all scenes are generated, trim leading/trailing silence without cutting words, retain natural pauses inside sentences, align each picture to its corresponding voice, and apply smooth ~0.32-second cross-dissolves. Assemble scenes 30–150, then join with the two existing 1–29 videos into one mobile-compatible MP4, taking care of boundaries. User wants the final video only, not partial clips. Runtime will reflect speech without padding rather than the original 22-minute target. Validate the video and publish it on the existing branch; account for GitHub's 100 MB per-file limit.
