# w-gymelig: frozen-pool two-point behavioral eligibility

FOUND: **89/89 families pass on every one of their 20 preserved rows**. All 1,780 reference answers return full credit 1, and all 1,780 empty answers return no credit 0. Constructor exceptions, scorer exceptions and refusals are each zero. This establishes this host-package control on this frozen pool only. Evidence: `tests/fixtures/hg_gymelig/verdicts.json:62` and exact command/stdout below; every row retains its actual returned scalar and Python type.

## Scope and custody

FOUND: the read-only input is `/mnt/20t/xubuqiang/datasets/reasoning_gym/pool.jsonl`, 3315981 bytes, SHA-256 `c0ff4eaef318cd59afcc61472ebe206362fc0211c4b589ed0d53946a569bd177` before and after scoring (`tests/fixtures/hg_gymelig/verdicts.json:13`, `tests/fixtures/hg_gymelig/verdicts.json:18`). Family names, seed 20261008 and size 20 are parsed as AST literals from `data/datasets/reasoning_gym/prepare.py:39`, `:44`, `:45`, `:49`; the generator module is never executed. Rows are read from the existing bytes in declared family-major order, with no regenerated entry or seed/order substitution (`tests/fixtures/hg_gymelig/control.py:76`). Coordinates and SHA-256 of each exact JSONL row excluding the newline bind the verdicts without exporting questions, references or metadata.

FOUND: installed distribution version is 0.1.25 and package root is `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/reasoning_gym` (`tests/fixtures/hg_gymelig/verdicts.json:4`, `tests/fixtures/hg_gymelig/package-members.json:2`). Invocation interpreter is `/mnt/8t/xubuqiang/anaconda3/bin/python3`; its resolved object is `/mnt/8t/xubuqiang/anaconda3/bin/python3.12`, SHA-256 `0eb25a387ef43f21492b659f4865eae5bdaf8da30d6357097b2d9bb24873ebfb` (`tests/fixtures/hg_gymelig/verdicts.json:5`). Current installed package observations hash 344 members, including imported Python sources/cached bytecode, inspected scorer/constructor sources and opened package resources. This is an observed-member inventory, **not** a complete transitive dependency/native closure (`tests/fixtures/hg_gymelig/package-members.json:3`). Existing wheel/source custody is retained; this worker did not acquire or reauthenticate distributions/upstream revisions.

Each family is instantiated with `reasoning_gym.create_dataset(family, size=20, seed=20261008)`, then scored by its resolved bound `dataset.score_answer(answer=..., entry=deepcopy(frozen_entry))`. The first call receives the row's own unchanged reference string; the second receives `""`. Copying each entry independently prevents a scorer mutation from contaminating the other point. No adapter reward conversion or binarization intervenes. Inherited `ProceduralDataset.score_answer` is the family's own resolved entry point where it has no override; the table names that implementation explicitly (`tests/fixtures/hg_gymelig/control.py:114`, `:129`, `:134`, `:145`; `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/reasoning_gym/factory.py:51`).

CPU execution binds one available CPU (observed affinity `[0]`), four thread-count environment settings to 1, CPU limit 300/310 seconds and address-space limit 4 GiB. CUDA devices are hidden; Python audit hooks reject network/child-process operations and writes outside scratch; a profile hook rejects package `__getitem__` so entries cannot be regenerated. No forbidden attempt was observed. These are local control guards, not a kernel network-denial or pristine-verifier receipt (`tests/fixtures/hg_gymelig/control.py:38`, `:52`, `:68`; `tests/fixtures/hg_gymelig/verdicts.json:34`, `:51`). Scorer/import stdout/stderr (215 bytes) was suppressed and retained only as length/digest, never as possible pool content (`tests/fixtures/hg_gymelig/verdicts.json:58`).

## Metric values and interpretation

The documented repository family eligibility contract is reference **1.0**, empty **0.0** (`data/datasets/reasoning_gym/prepare.py:13`; `tests/quality/test_reasoning_gym_official_scorer.py:134`). The package base implementation starts at 0.0, returns 1.0 for an exact nonempty reference, and can return a fractional length ratio (`/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/reasoning_gym/dataset.py:63`). Overrides retain their own scalar scoring semantics; the function identities, source locations and complete source-file digests below identify those implementations, without claiming all are binary metrics or uniformly documented. Their full-credit/no-credit targets in this control are 1/0; no alternative full-credit scale was observed.

Actual control outputs contain 3,540 Python floats and 20 Python integers. In `polynomial_equations`, the empty control returns integer `0` on every row; its references return float `1.0`. Every other control output is float `1.0` or `0.0`. These values and types are retained verbatim in the JSON record, including every row (`tests/fixtures/hg_gymelig/verdicts.json:18928`; exact record-validation command/output in `registry/w-gymelig-validation.txt`). This control does not probe partial-credit behavior or arbitrary submitted strings.

## Per-family results (89 rows)

All rows use indices 0–19. `Eligible` means the two equalities held on **all 20 frozen rows** for that family, not a guarantee about other generated tasks. Source paths in the entry-point column are relative to the exact installed package root above. `V:n` is `tests/fixtures/hg_gymelig/verdicts.json:n`; full source-file SHA-256 values are in the next section and the member inventory.

| Family | Called implementation; package file:line | Reference verdict | Empty verdict | Exceptions/refusals | Eligibility; evidence |
|---|---|---|---|---|---|
| `ab` | `reasoning_gym.algorithmic.ab.ABDataset.score_answer`; `algorithmic/ab.py:129` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:78 |
| `acre` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:403 |
| `aiw` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:728 |
| `arc_1d` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:1053 |
| `base_conversion` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:1378 |
| `basic_arithmetic` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:1703 |
| `bf` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:2028 |
| `binary_alternation` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:2353 |
| `binary_matrix` | `reasoning_gym.algorithmic.binary_matrix.BinaryMatrixDataset.score_answer`; `algorithmic/binary_matrix.py:102` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:2678 |
| `bitwise_arithmetic` | `reasoning_gym.arithmetic.bitwise_arithmetic.BitwiseArithmeticDataset.score_answer`; `arithmetic/bitwise_arithmetic.py:168` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:3003 |
| `caesar_cipher` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:3328 |
| `calendar_arithmetic` | `reasoning_gym.arithmetic.calendar_arithmetic.CalendarArithmeticDataset.score_answer`; `arithmetic/calendar_arithmetic.py:439` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:3653 |
| `chain_sum` | `reasoning_gym.arithmetic.chain_sum.ChainSumDataset.score_answer`; `arithmetic/chain_sum.py:119` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:3978 |
| `circuit_logic` | `reasoning_gym.logic.circuit_logic.CircuitLogicDataset.score_answer`; `logic/circuit_logic.py:400` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:4303 |
| `codeio` | `reasoning_gym.code.codeio.CodeIODataset.score_answer`; `code/codeio.py:225` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:4628 |
| `coin_flip` | `reasoning_gym.probability.coin_flip.CoinFlipDataset.score_answer`; `probability/coin_flip.py:113` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:4953 |
| `complex_arithmetic` | `reasoning_gym.algebra.complex_arithmetic.ComplexArithmeticDataset.score_answer`; `algebra/complex_arithmetic.py:168` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:5278 |
| `count_bits` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:5603 |
| `count_primes` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:5928 |
| `course_schedule` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:6253 |
| `cryptarithm` | `reasoning_gym.algorithmic.cryptarithm.CryptarithmDataset.score_answer`; `algorithmic/cryptarithm.py:287` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:6578 |
| `decimal_arithmetic` | `reasoning_gym.arithmetic.decimal_arithmetic.DecimalArithmeticDataset.score_answer`; `arithmetic/decimal_arithmetic.py:205` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:6903 |
| `decimal_chain_sum` | `reasoning_gym.arithmetic.decimal_chain_sum.DecimalChainSumDataset.score_answer`; `arithmetic/decimal_chain_sum.py:147` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:7228 |
| `dice` | `reasoning_gym.arithmetic.dice.DiceDataset.score_answer`; `arithmetic/dice.py:139` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:7553 |
| `family_relationships` | `reasoning_gym.graphs.family_relationships.FamilyRelationshipsDataset.score_answer`; `graphs/family_relationships.py:366` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:7878 |
| `figlet_font` | `reasoning_gym.cognition.figlet_fonts.FigletFontDataset.score_answer`; `cognition/figlet_fonts.py:201` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:8203 |
| `futoshiki` | `reasoning_gym.games.futoshiki.FutoshikiDataset.score_answer`; `games/futoshiki.py:635` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:8528 |
| `game_of_life` | `reasoning_gym.algorithmic.game_of_life.GameOfLifeDataset.score_answer`; `algorithmic/game_of_life.py:101` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:8853 |
| `game_of_life_halting` | `reasoning_gym.algorithmic.game_of_life_halting.GameOfLifeHaltingDataset.score_answer`; `algorithmic/game_of_life_halting.py:385` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:9178 |
| `gcd` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:9503 |
| `group_anagrams` | `reasoning_gym.algorithmic.group_anagrams.GroupAnagramsDataset.score_answer`; `algorithmic/group_anagrams.py:88` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:9828 |
| `gsm_symbolic` | `reasoning_gym.arithmetic.gsm_symbolic.gsm_symbolic.GSMSymbolicDataset.score_answer`; `arithmetic/gsm_symbolic/gsm_symbolic.py:160` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:10153 |
| `intermediate_integration` | `reasoning_gym.algebra.intermediate_integration.IntermediateIntegrationDataset.score_answer`; `algebra/intermediate_integration.py:251` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:10478 |
| `isomorphic_strings` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:10803 |
| `jugs` | `reasoning_gym.algorithmic.jugs.JugsDataset.score_answer`; `algorithmic/jugs.py:297` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:11128 |
| `kakurasu` | `reasoning_gym.games.kakurasu.KakurasuDataset.score_answer`; `games/kakurasu.py:187` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:11453 |
| `knight_swap` | `reasoning_gym.games.knight_swap.KnightSwapDataset.score_answer`; `games/knight_swap.py:316` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:11778 |
| `knights_knaves` | `reasoning_gym.logic.knights_knaves.KnightsKnavesDataset.score_answer`; `logic/knights_knaves.py:501` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:12103 |
| `largest_island` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:12428 |
| `lcm` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:12753 |
| `leg_counting` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:13078 |
| `letter_counting` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:13403 |
| `letter_jumble` | `reasoning_gym.algorithmic.letter_jumble.LetterJumbleDataset.score_answer`; `algorithmic/letter_jumble.py:143` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:13728 |
| `list_functions` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:14053 |
| `mahjong_puzzle` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:14378 |
| `manipulate_matrix` | `reasoning_gym.algorithmic.manipulate_matrix.ManipulateMatrixDataset.score_answer`; `algorithmic/manipulate_matrix.py:134` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:14703 |
| `maze` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:15028 |
| `mini_sudoku` | `reasoning_gym.games.mini_sudoku.MiniSudokuDataset.score_answer`; `games/mini_sudoku.py:209` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:15353 |
| `modulo_grid` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:15678 |
| `n_queens` | `reasoning_gym.games.n_queens.NQueensDataset.score_answer`; `games/n_queens.py:149` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:16003 |
| `needle_haystack` | `reasoning_gym.cognition.needle_haystack.NeedleHaystackDataset.score_answer`; `cognition/needle_haystack.py:119` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:16328 |
| `number_filtering` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:16653 |
| `number_format` | `reasoning_gym.arithmetic.number_format.NumberFormatDataset.score_answer`; `arithmetic/number_format.py:72` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:16978 |
| `number_sequence` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:17303 |
| `number_sorting` | `reasoning_gym.algorithmic.number_sorting.NumberSortingDataset.score_answer`; `algorithmic/number_sorting.py:102` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:17628 |
| `palindrome_generation` | `reasoning_gym.algorithmic.palindrome_generation.PalindromeDataset.score_answer`; `algorithmic/palindrome_generation.py:97` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:17953 |
| `palindrome_partitioning` | `reasoning_gym.algorithmic.palindrome_partitioning.PalindromePartitioningDataset.score_answer`; `algorithmic/palindrome_partitioning.py:97` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:18278 |
| `path_star` | `reasoning_gym.graphs.path_star.PathStarDataset.score_answer`; `graphs/path_star.py:61` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:18603 |
| `polynomial_equations` | `reasoning_gym.algebra.polynomial_equations.PolynomialEquationsDataset.score_answer`; `algebra/polynomial_equations.py:211` | 1.0, 20/20 | 0 (int), 20/20 | 0 / 0 | Eligible; V:18928 |
| `polynomial_multiplication` | `reasoning_gym.algebra.polynomial_multiplication.PolynomialMultiplicationDataset.score_answer`; `algebra/polynomial_multiplication.py:162` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:19253 |
| `pool_matrix` | `reasoning_gym.algorithmic.pool_matrix.PoolMatrixDataset.score_answer`; `algorithmic/pool_matrix.py:81` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:19578 |
| `products` | `reasoning_gym.arithmetic.products.ProductsDataset.score_answer`; `arithmetic/products.py:111` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:19903 |
| `quantum_lock` | `reasoning_gym.graphs.quantum_lock.QuantumLockDataset.score_answer`; `graphs/quantum_lock.py:173` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:20228 |
| `ransom_note` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:20553 |
| `rectangle_count` | `reasoning_gym.cognition.rectangle_count.RectangleCountDataset.score_answer`; `cognition/rectangle_count.py:136` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:20878 |
| `rotate_matrix` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:21203 |
| `rotten_oranges` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:21528 |
| `self_reference` | `reasoning_gym.logic.self_reference.SelfReferenceDataset.score_answer`; `logic/self_reference.py:358` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:21853 |
| `shortest_path` | `reasoning_gym.graphs.shortest_path.ShortestPathDataset.score_answer`; `graphs/shortest_path.py:125` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:22178 |
| `simple_equations` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:22503 |
| `simple_geometry` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:22828 |
| `simple_integration` | `reasoning_gym.algebra.simple_integration.SimpleIntegrationDataset.score_answer`; `algebra/simple_integration.py:98` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:23153 |
| `sokoban` | `reasoning_gym.games.sokoban.SokobanDataset.score_answer`; `games/sokoban.py:112` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:23478 |
| `spell_backward` | `reasoning_gym.algorithmic.spell_backward.SpellBackwardDataset.score_answer`; `algorithmic/spell_backward.py:67` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:23803 |
| `spiral_matrix` | `reasoning_gym.algorithmic.spiral_matrix.SpiralMatrixDataset.score_answer`; `algorithmic/spiral_matrix.py:130` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:24128 |
| `string_insertion` | `reasoning_gym.algorithmic.string_insertion.StringInsertionDataset.score_answer`; `algorithmic/string_insertion.py:79` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:24453 |
| `string_manipulation` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:24778 |
| `string_splitting` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:25103 |
| `string_synthesis` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:25428 |
| `sudoku` | `reasoning_gym.games.sudoku.SudokuDataset.score_answer`; `games/sudoku.py:228` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:25753 |
| `survo` | `reasoning_gym.games.survo.SurvoDataset.score_answer`; `games/survo.py:132` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:26078 |
| `syllogism` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:26403 |
| `time_intervals` | `reasoning_gym.arithmetic.time_intervals.TimeIntervalsDataset.score_answer`; `arithmetic/time_intervals.py:252` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:26728 |
| `tower_of_hanoi` | `reasoning_gym.games.tower_of_hanoi.HanoiDataset.score_answer`; `games/tower_of_hanoi.py:390` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:27053 |
| `tsumego` | `reasoning_gym.games.tsumego.TsumegoDataset.score_answer`; `games/tsumego.py:286` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:27378 |
| `word_ladder` | `reasoning_gym.algorithmic.word_ladder.WordLadderDataset.score_answer`; `algorithmic/word_ladder.py:237` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:27703 |
| `word_sequence_reversal` | `reasoning_gym.dataset.ProceduralDataset.score_answer`; `dataset.py:63` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:28028 |
| `word_sorting` | `reasoning_gym.algorithmic.word_sorting.WordSortingDataset.score_answer`; `algorithmic/word_sorting.py:126` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:28353 |
| `zebra_puzzles` | `reasoning_gym.logic.zebra_puzzles.ZebraDataset.score_answer`; `logic/zebra_puzzles.py:62` | 1.0, 20/20 | 0.0, 20/20 | 0 / 0 | Eligible; V:28678 |

## Scorer source identities and digests

FOUND: these are the 57 distinct scorer implementation source files resolved for the 89 families, with their exact observed SHA-256 values. Factory, constructor, module and resource members are also recorded in the complete observed-member inventory. `M:n` is `tests/fixtures/hg_gymelig/package-members.json:n`.

| Installed source (relative to package root) | SHA-256 | Evidence |
|---|---|---|
| `algebra/complex_arithmetic.py` | `32beb8f40a25aa781b96f6293f11bd4de8b59c903ee30ea11e5659d8d8310d2a` | M:82 |
| `algebra/intermediate_integration.py` | `74838f0224b504e369d3750183e6d96586ecd365fd618e98f11b8488260ed8ef` | M:87 |
| `algebra/polynomial_equations.py` | `d41b84e2daf73105922c4211d8a49307ae0b143c0bc58c20cbbdcd25852fcf1a` | M:92 |
| `algebra/polynomial_multiplication.py` | `4a2d9db4b720f17861b02d17add43255741b871ad4c161929ec6fd54f6112b20` | M:97 |
| `algebra/simple_integration.py` | `15e275301091a609745414f1e7b05a96dfe53ed19ed910ec2df065652299c698` | M:107 |
| `algorithmic/ab.py` | `a232e9cbf1cc7fb20f913cca845504d808578866734e085c9cffda12636bab65` | M:292 |
| `algorithmic/binary_matrix.py` | `0697d49b6cb8812731713e2d930469023e9281c8c4354400655376a0becb6491` | M:307 |
| `algorithmic/cryptarithm.py` | `9dfd7012e4fda20c15e62559b7a508d211992fa33fc8641ca76ef384119bb10f` | M:322 |
| `algorithmic/game_of_life.py` | `0cd5e37e542f2e956efcefb898ec84f4a1d34d44ba4b039e145fcb457e907f20` | M:327 |
| `algorithmic/game_of_life_halting.py` | `47c54e209b1ea551b191bf577bd0ad3a5eb3f94810174f2e69052a3f30706f28` | M:332 |
| `algorithmic/group_anagrams.py` | `85c3fe62b293f423b9c3c404afcfba53d50b4ef53e2e52caaed9c2a123adb35c` | M:342 |
| `algorithmic/jugs.py` | `9a14c33afbb2fcf0b182d80a2c300ef62f42a70b04768032550020c50dfe0d8d` | M:352 |
| `algorithmic/letter_jumble.py` | `1fc2b12a373460c72d9b5e0b31bd4f79c12082e708e6fd99470e91f853bec9b8` | M:362 |
| `algorithmic/manipulate_matrix.py` | `7203c8ad02bb74fe52a91b88a9fcaca17647735a9d32acba09b04718a0458093` | M:367 |
| `algorithmic/number_sorting.py` | `a481e06274f9a978b213d43abd87d04943b796d73582d4b6febcfbe6a0f369f1` | M:377 |
| `algorithmic/palindrome_generation.py` | `6823b3787d901f0135c6483546b416d49f107046432eebb14749b67f73d2f7de` | M:382 |
| `algorithmic/palindrome_partitioning.py` | `a1c218cdd2bb9e90a692be8bf7877a3b93e6230c0028b5c9f506de4d971a9f4a` | M:387 |
| `algorithmic/pool_matrix.py` | `36b24a7835769b132a22190f6477002b9ad516aa86c486e868b19e521eca8a9a` | M:392 |
| `algorithmic/spell_backward.py` | `a27f14e886fad4d7dd1bf0506644be70c095bb71201a5e8d71128647901d9773` | M:417 |
| `algorithmic/spiral_matrix.py` | `7d1b8f352b72b609dab9aed7c6e585581c86666421ba78a3145e7d97cd37ed39` | M:422 |
| `algorithmic/string_insertion.py` | `866e1de2b8fcd9f88de5b491e1b7e306a3db1041bf139cdbb79061b23fec40bf` | M:427 |
| `algorithmic/word_ladder.py` | `8a82e0dee96401a019b6842bb99c2300e1b64b4cc03051a3f22675364acd9f5e` | M:447 |
| `algorithmic/word_sorting.py` | `32d554acf0613b0cec4236a806165bebb426420a851a9e5468943a0cb8deff41` | M:457 |
| `arithmetic/bitwise_arithmetic.py` | `d4c0fa2bf34ed1610c4cb3b2ec6ea40bdaf2b190875c3b64536f21e5540eacb5` | M:622 |
| `arithmetic/calendar_arithmetic.py` | `ad06cec5be9c14889c4860482218aecba128815b1357a1ee410b3aac4be54120` | M:627 |
| `arithmetic/chain_sum.py` | `7e811214e9e31aa67eeb5490a0cf8eb275fceab609c4523bb38ceec9f8dbcb9f` | M:632 |
| `arithmetic/decimal_arithmetic.py` | `e56416e0c10bb55f46961e93ef55826f419d1a0186ff75b6bb367d098dcca245` | M:642 |
| `arithmetic/decimal_chain_sum.py` | `1a4b13aceb3fc50dce3921f109b9d5b0d53aaa9c6eafc7acb01dd2988c15cc3e` | M:647 |
| `arithmetic/dice.py` | `3b8f83d04f01b13526e2790245c09a52b2c0998c16baf92607b671d2459ba0d9` | M:652 |
| `arithmetic/gsm_symbolic/gsm_symbolic.py` | `511e30a979511719c65019082ea298e215f4fbfab7d7660b384fa51c0fd03ee1` | M:682 |
| `arithmetic/number_format.py` | `a30fb4f8086eff3a9fbc481e2dd423fa0d552502d3746c0a8bd2bff12e1b92e2` | M:697 |
| `arithmetic/products.py` | `63959e2c03580d8d408e2e91c2c30c7016d8ca2ad937fd5656e83c371d5dcbc0` | M:712 |
| `arithmetic/time_intervals.py` | `b42d9a9f992eead49d028f13e0ffd454b24676f92402e1a323cbabdd74d20100` | M:717 |
| `code/codeio.py` | `c573957be85a68179520b61cc70ebb22ab39027dd0a876b2f4402df9df6be1a2` | M:807 |
| `cognition/figlet_fonts.py` | `a39ae5e48acca9018a8d2d13d3e2543ffc2da7a8cf100c251f53dc956833500f` | M:1022 |
| `cognition/needle_haystack.py` | `c9f3c04bdff4b288a4265fdfacb1e7bc2b7c6d3dbe254c1dbdfb08924bad7bdc` | M:1032 |
| `cognition/rectangle_count.py` | `cbe4bb706e5db274cd9c2d600ce50e239572f700a6ba3a4043cf59f320f83769` | M:1042 |
| `dataset.py` | `480caacca5b12865e13bac68937687a799977e040ace5ae0496e71c1d77971e6` | M:1107 |
| `games/futoshiki.py` | `1e17d801b9695f35d04047bde037beae0e6b1e6622ef89b287ec5c2061c2db5e` | M:1317 |
| `games/kakurasu.py` | `32952922a3c863ba14acc2773230e18e2226e221cae093dd04956e7f86f69ab8` | M:1322 |
| `games/knight_swap.py` | `a9de444d885125e0e6d42de9c34a705c3a22c9fed670375927ee8fe182542e95` | M:1327 |
| `games/mini_sudoku.py` | `20b77f97b1f5a9aa364940311d6647c4fa3e2b69834995371e0b20dd9f818c0c` | M:1342 |
| `games/n_queens.py` | `2738aad6232b45f21e57c0cb6d58dbcd1752a97e95e7abb8cf8c1002a4bf4c64` | M:1347 |
| `games/sokoban.py` | `19bdaa006e58627dbc76c46ae7641e34b2c9305603b1e68d47640e51c7c6b4bb` | M:1362 |
| `games/sudoku.py` | `dcb9e0c968d33b0f7883390d7b3155aa7a6088fae9db48bba832ca9aea21f4e0` | M:1367 |
| `games/survo.py` | `6d506c11d914f8b1d7c910c26b8da9a44e9ad8bbec1b9cf595a426f8c8cf864a` | M:1372 |
| `games/tower_of_hanoi.py` | `6a983d45cd5ef3a6380b509ef7313af859defa52d02526b022f52fae85298eef` | M:1377 |
| `games/tsumego.py` | `5978a0f3b5b785e98b58190fb5ddf90403f16165094d2369d4a84f2a59daa021` | M:1382 |
| `graphs/family_relationships.py` | `b00459b1242416befddbb4c0bb6880d02bf1c967a1057f9c39a298d5a4bda455` | M:1462 |
| `graphs/path_star.py` | `ae55353009956240c0eacb5033753494c60c4b67ab29f12e77ed84ee66d9fe3a` | M:1472 |
| `graphs/quantum_lock.py` | `2f96d165fe0a33fb3dabdc92ffb99966fbcda41351d87f1c12df497da64311d8` | M:1477 |
| `graphs/shortest_path.py` | `40756d552a64f6c7b513e2e6eb2d57755e31f70b766fff62113f786165dcaabd` | M:1482 |
| `logic/circuit_logic.py` | `04858f961e50c87f16aab89e2f83b000c9577dd83704a7a205b919f92d14a56f` | M:1597 |
| `logic/knights_knaves.py` | `8837a3c6dfc72bb40db168b82ad6b3da45a08a4000a006fc306368b77b622705` | M:1672 |
| `logic/self_reference.py` | `8b0eebadba3c07a56a58fd9f88830be40b49cb94882a9cb595672ae337143424` | M:1682 |
| `logic/zebra_puzzles.py` | `41312f2635a0a7f920fd6a8006a9e8b1b7e4225d7900da504078b1fd5560e580` | M:1692 |
| `probability/coin_flip.py` | `a6e6ebe348bdd289bbf06bfe9360e4e1187453c82a973e2545b58a94a4b7b740` | M:1712 |

## Failure scope and outcome classes

ABSENT within an enumerated scope: reference failures, empty failures, scorer exceptions, constructor exceptions, refusals and non-eligible families in the recorded control for exactly the 89 table families × frozen indices 0–19 × the two answer points. The exact record-validation command in `registry/w-gymelig-validation.txt` enumerates these coordinates, independently recomputes aggregates, and prints the offending coordinate lists; each is `[]`. This is not an absence claim about untested package families, generated tasks, model outputs or arbitrary answers. No failed-family explanation or reference quotation is needed because that scope has no failures.

Outcome definitions are explicit in `tests/fixtures/hg_gymelig/control.py:114`: a finite numeric return is `score`, an exception is `exception` with its own type/message (never converted to zero), and a nonnumeric/nonfinite return is `refusal`. A constructor failure would leave both points `unexecuted`, separately from scorer exceptions. None of these exceptional classes occurred in this record (exact stdout below).

No legitimate empty-answer degeneracy was observed on these frozen rows. The package does have such semantics in a relevant scorer: `polynomial_equations` returns 1.0 when both parsed oracle and prediction solution lists are empty (`/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/reasoning_gym/algebra/polynomial_equations.py:233`; source digest above). That is a correct empty-set case under its own implementation, rather than automatically a defect. The observed 20 empty controls for this family all returned 0, so it is not an exclusion in this packet. Behavior on other/generated polynomial tasks is UNKNOWN here.

## Exact execution command and output

Working directory: `/mnt/20t/xubuqiang/hg-wt/w-gymelig`. The output directory was fresh and is retained outside git; replay must use a new nonexistent directory under the same scratch root. This is a synthetic control invocation, with no dataset run ID or launch receipt.

```sh
export TMPDIR=/mnt/20t/xubuqiang/hg-work/gymelig/tmp
export PYTHONDONTWRITEBYTECODE=1
export CUDA_VISIBLE_DEVICES=''
python3 tests/fixtures/hg_gymelig/control.py --output-dir /mnt/20t/xubuqiang/hg-work/gymelig/control-01 > /mnt/20t/xubuqiang/hg-work/gymelig/control-01.stdout.txt 2> /mnt/20t/xubuqiang/hg-work/gymelig/control-01.stderr.txt
cat /mnt/20t/xubuqiang/hg-work/gymelig/control-01.stdout.txt
cat /mnt/20t/xubuqiang/hg-work/gymelig/control-01.stderr.txt
```

Observed stdout (exact; exit 0, shell stderr empty):

```text
{"constructor_exceptions": 0, "eligible_families": 89, "empty_zero": 89, "empty_zero_rows": 1780, "exceptions": 0, "families_tested": 89, "non_eligible": [], "reference_full_credit": 89, "reference_full_credit_rows": 1780, "refusals": 0, "rows_tested": 1780, "score_calls": 3560}
{"blocked_events": [], "captured_output_bytes": 215, "package_members_hashed": 344, "package_version": "0.1.25", "pool_after": {"bytes": 3315981, "path": "/mnt/20t/xubuqiang/datasets/reasoning_gym/pool.jsonl", "sha256": "c0ff4eaef318cd59afcc61472ebe206362fc0211c4b589ed0d53946a569bd177"}, "pool_before": {"bytes": 3315981, "path": "/mnt/20t/xubuqiang/datasets/reasoning_gym/pool.jsonl", "sha256": "c0ff4eaef318cd59afcc61472ebe206362fc0211c4b589ed0d53946a569bd177"}}
```

The runner code and SHA are bound in `tests/fixtures/hg_gymelig/verdicts.json`; its copied verdict/member/stdout bytes were independently checked against the original scratch evidence. Record/privacy/digest/proposal checks, checker output, file sizes and commands are in `registry/w-gymelig-validation.txt`.

## Limits and proposed integration

FOUND is limited to this synthetic two-point behavioral control on the exact frozen pool using the currently installed host family entry points. It is **not a measured dataset run, not a model result, not the pristine verifier, and not an official-scorer-execution receipt**. It does **not authorize a diagnostic**, establish production admission, transitive/offline dependency closure, immutable runtime/native custody, arbitrary-answer robustness, partial-credit correctness or benchmark comparability. Existing tests that regenerate entries were deliberately not run; the pool was never regenerated or overwritten (`tests/fixtures/hg_gymelig/control.py:68`; exact output above).

UNKNOWN / not verified by this worker: original generation process/environment/date/hash-order/dependency metadata and exact reproduction; independent public seed-specific pool release; selected external export's continued availability; a resolved single split/side/run binding; deterministic transitive dependencies without scoring extras; pristine-verifier execution/ownership/private-input/export boundaries and runtime metric evidence. These remain obligations in the existing `registry/dataset-blockers.json:672`; no machine-wide ABSENT assertion is made. The first-five packet remains separate custody evidence and declares a mixed side and no execution authorization (`tests/fixtures/hg_wsel/reasoning_gym.json:7`, `:38`, `:47`). The synthetic family controls do not create a replacement selected launch manifest.

`registry/proposals/w-gymelig.json` replaces only the behavioral-eligibility sentence of the existing next_action; all other text is retained exactly, including original generation/reproduction, selected manifest/export, split/side/run binding, transitive dependencies/metric/runtime and explicit-opt-in pristine execution, private-input/export/ownership boundaries, withdrawn shared gates and withdrawn official-scorer-identity proof. The base next_action string SHA enables stale-proposal review. Parent integration is required; this worker makes no registry or journal edit and no status/history change. Checker output remains `{"valid": true, "datasets": 28, "shared_blockers": 0, "historical_records": 11, "production_authorized": false}` (exact command/output in `registry/w-gymelig-validation.txt`).
