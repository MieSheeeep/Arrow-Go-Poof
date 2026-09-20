# Reveal Glow Design

## Goal

Give every successful arrow click immediate visual confirmation: the newly
revealed pixel flashes in its own bead colour on the click frame, then settles
to its normal revealed colour while the arrow flies out. Blocked clicks remain
unchanged and continue to use the existing red collision feedback.

## Behaviour

- A successful `Game.click()` already creates a `FlyOutAnimation` immediately.
- The UI uses that live fly-out animation as the source of the reveal effect;
  it does not delay path judgement or wait for the arrow to leave the board.
- For the first 0.22 seconds of the fly-out, the origin cell receives a
  rounded, same-colour highlight. Its alpha and brightness decrease smoothly
  from a brief peak to zero.
- The pixel colour comes from `Board.color_grid` through the existing
  `COLOR_MAP`, so each bead design supplies its own red, gold, blue, pink, or
  other highlight colour automatically.
- The effect is drawn after the normal board but before the moving arrow. This
  preserves the arrow's visibility while making the revealed pixel feel lit.
- Pause freezes the effect because `Game.update()` already freezes all live
  animations. Terminal states retain the effect only until their active
  animation duration ends.

## Architecture

No new game state is needed. `FlyOutAnimation` already contains its origin
cell and elapsed time. Add a small UI-only helper that maps animation progress
to a 0..1 reveal-glow strength and draws a translucent rounded overlay at the
animation's original cell. `_draw_animations()` owns the call, keeping
gameplay rules and rendering separate.

## Testing

- A new UI test creates a successful fly-out, draws at progress zero, advances
  past the glow duration, and verifies that only the early frame receives the
  brighter same-colour overlay.
- Existing animation and game tests continue to prove that timing and click
  judgement remain immediate.
