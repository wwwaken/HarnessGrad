/**
 * The pure logic the UI is built on. Kept out of components so it can be tested without a
 * DOM, and so the three questions a researcher actually asks have named answers:
 *
 * * `curve.ts`   — "what does this run's curve look like, and is a series even measurable?"
 * * `compare.ts` — "which tasks moved?" — including the case where the score did not.
 * * `certify.ts` — "can I quote this run?"
 * * `launch.ts`  — "what argv would this form produce?"
 */
export * from "./presence";
export * from "./curve";
export * from "./compare";
export * from "./certify";
export * from "./launch";
export * from "./trace";
