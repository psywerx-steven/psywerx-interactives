# Topic Guide card artwork

The directory uses the user's approved 15-icon sheet, cropped without redrawing.
Icons are decorative companions to the existing linked titles. They add no
analytical tags, classification, episode membership, quotations, or corpus data.

## Stable mapping

The `ICON_CELLS` mapping in `scripts/cognitive_security/topic_guides.py` is keyed
by guide slug, **not** by directory position, category, list order, or numeric
cluster ID. This matters because the directory groups and reorders the guides.
The cell order in the approved sheet is:

| Row | Left to right |
| --- | --- |
| 1 | Assessment; Narrative; Cognitive Warfare; Influence Psychology; AI |
| 2 | Disinformation; Resilience; Deterrence; Campaign Planning; Audience Analysis |
| 3 | Data & Analytics; Ethics & Law; Workforce; Strategic Communication; Cyber |

## Asset preparation

The original approved sheet is 1536 x 1024 px. Crops are 282 x 282 px, centered
at x = 167, 464, 765, 1070, 1372 and y = 214, 510, 804, then resized to 176 px
with Lanczos resampling. The tiles are packed into one 880 x 528 px WebP asset
at quality 75. The single locally served sprite is 31,084 bytes; the builder
checks its SHA-256 fingerprint. There are no remote image dependencies.

Each icon is displayed at 80 px on desktop and 72 px on mobile. The approved
navy/cyan artwork is unchanged apart from cropping, resizing, and compression.
Fixed dimensions reserve space before the image loads. The sprite uses normal
CSS backgrounds and needs no JavaScript. Decorative spans are hidden from
screen readers, which retain the original linked guide titles and destinations.
Forced-colors mode hides the decoration, keeping the text and links.

Future guides can remain usable without artwork. Existing artwork cells must
not be silently reassigned when guides are sorted, grouped, or extended.

## Validation

Six new contract tests verify the mapping, sprite hash and dimensions, all
15 static icons, order independence, future-guide fallback, and preservation
of content counts and protected sources. Two additional browser tests check
all 15 cards at 1360, 390, and 320 px, successful WebP decoding, exact icon/link
pairings, no horizontal overflow, and JavaScript-disabled navigation.
