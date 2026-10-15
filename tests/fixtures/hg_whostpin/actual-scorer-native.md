# Actual scorer native objects - w-hostpin

Source entries: interpreter selection `data/datasets/bird_minidev.py:257`; SQLite
`data/datasets/bird_minidev/verify/check.py:30`; JSON `:28`; trusted helper `:37`
then `data/scaffolds/scorer_input.py:14` (hashlib) and `:17` (tempfile).
The helper imports tempfile → shutil/random → compression, math and random
extensions; hashlib selects _hashlib/_blake2/_sha2; SQLite imports datetime.
The complete parent DT_NEEDED/PT_INTERP links and independent raw hashes are
in closure-files.md. File/line locators below refer to repository source.

| Mapped ELF destination | Fresh SHA-256 | Source entry | First raw trace line |
| --- | --- | --- | --- |
| `/lib/x86_64-linux-gnu/libc.so.6` | `b2cf6c33b74d2f22543b7a469a75b538911e690f769d0b238843a49465b83793` | `data/datasets/bird_minidev.py:257` | `bound-check.strace.txt:5682` |
| `/lib/x86_64-linux-gnu/libdl.so.2` | `3eaaa4aefd9c28f3867c96a427c3cbec9191cb61c4c9d0a2cb4a765d66064499` | `data/datasets/bird_minidev.py:257` | `bound-check.strace.txt:5663` |
| `/lib/x86_64-linux-gnu/libm.so.6` | `3dd5511ae94785c9f921429b0f2b2f7aabb461b6f0e6de6dfdbef15f24bdfee6` | `data/datasets/bird_minidev.py:257` | `bound-check.strace.txt:5675` |
| `/lib/x86_64-linux-gnu/libpthread.so.0` | `fbed9505adacada2abb37c6b43be2df6de81e742712c6025694ba48de62c7e78` | `data/datasets/bird_minidev.py:257` | `bound-check.strace.txt:5657` |
| `/lib/x86_64-linux-gnu/libutil.so.1` | `ee98a316fe33727cf23cc81d3a7f9628350d6ef75e905c7b713e5f5e68e177dc` | `data/datasets/bird_minidev.py:257` | `bound-check.strace.txt:5669` |
| `/lib64/ld-linux-x86-64.so.2` | `41daf7836f7fce21a40ca63a00c5caf21b05a35a76ccc075d86f1716212cdf01` | `data/datasets/bird_minidev.py:257` | `bound-check.strace.txt:5611` |
| `/mnt/8t/xubuqiang/anaconda3/bin/python3.12` | `0eb25a387ef43f21492b659f4865eae5bdaf8da30d6357097b2d9bb24873ebfb` | `data/datasets/bird_minidev.py:257` | `bound-check.strace.txt:5613` |
| `/mnt/8t/xubuqiang/anaconda3/lib/libbz2.so.1.0` | `4979469ae49ac144f62202f75bbdd69b17197aedb879d633337c8cf7e4aba301` | `data/scaffolds/scorer_input.py:17` | `bound-check.strace.txt:5901` |
| `/mnt/8t/xubuqiang/anaconda3/lib/libcrypto.so.3` | `8872fcd3e99e006d6a72d2fb55fad7bdaddeee5bddbc731223f1eed833eb5660` | `data/scaffolds/scorer_input.py:14` | `bound-check.strace.txt:5870` |
| `/mnt/8t/xubuqiang/anaconda3/lib/liblzma.so.5` | `503b2e072bbcea1bcc70eac2a522852fff337203253d2df83958144521d6e1c0` | `data/scaffolds/scorer_input.py:17` | `bound-check.strace.txt:5913` |
| `/mnt/8t/xubuqiang/anaconda3/lib/libsqlite3.so.0` | `71932eb5bf89092fbd2c900601fc9f24aa184d65038aaec2445fd11b1d923327` | `data/datasets/bird_minidev/verify/check.py:30` | `bound-check.strace.txt:5808` |
| `/mnt/8t/xubuqiang/anaconda3/lib/libz.so.1` | `0b0e682a9dc7fd4895a6783288f851b793dc89633f28714027974fa4d66f3914` | `data/scaffolds/scorer_input.py:17` | `bound-check.strace.txt:5832` |
| `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/lib-dynload/_bisect.cpython-312-x86_64-linux-gnu.so` | `7694659c2dea71e84ca42f0bc460dd8bad88a9971263182b91621a2aba08c00e` | `data/scaffolds/scorer_input.py:17` | `bound-check.strace.txt:5922` |
| `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/lib-dynload/_blake2.cpython-312-x86_64-linux-gnu.so` | `8d6f81f975efd43245211233d6350f55c7b9775a3af8c8279fd3ae78130a766a` | `data/scaffolds/scorer_input.py:14` | `bound-check.strace.txt:5877` |
| `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/lib-dynload/_bz2.cpython-312-x86_64-linux-gnu.so` | `1ba83c781a880da47da85fb7a89fb9add41b83936ede5f7d953ffbec984fcf92` | `data/scaffolds/scorer_input.py:17` | `bound-check.strace.txt:5896` |
| `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/lib-dynload/_datetime.cpython-312-x86_64-linux-gnu.so` | `0d768c77505d0e0764f91a84b7c9995f2d09ee47164ad54d90eb93a924673a8c` | `data/datasets/bird_minidev/verify/check.py:30` | `bound-check.strace.txt:5777` |
| `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/lib-dynload/_hashlib.cpython-312-x86_64-linux-gnu.so` | `5d00ef3921fc50cf555a78138c2ca2e7e733a1174dd71318cbea48ad523fa1fa` | `data/scaffolds/scorer_input.py:14` | `bound-check.strace.txt:5865` |
| `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/lib-dynload/_json.cpython-312-x86_64-linux-gnu.so` | `ce243e7213253aac36bc246d99dea848a53ee11b49a6b14190d3ab5bec2403d2` | `data/datasets/bird_minidev/verify/check.py:28` | `bound-check.strace.txt:5761` |
| `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/lib-dynload/_lzma.cpython-312-x86_64-linux-gnu.so` | `7f88e8f6da1a2d447e9ee5bfcece827ece8fc85329f4dce0f998cf046c8a57af` | `data/scaffolds/scorer_input.py:17` | `bound-check.strace.txt:5908` |
| `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/lib-dynload/_random.cpython-312-x86_64-linux-gnu.so` | `69dba6e4d4c736cda12dab1d3612b494fef03fc6159ac314d532ce9ad58c2825` | `data/scaffolds/scorer_input.py:17` | `bound-check.strace.txt:5927` |
| `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/lib-dynload/_sha2.cpython-312-x86_64-linux-gnu.so` | `61eba753529759d0a806757ce7a1e6d8bf465eb9ace5a9d787af346a6a7d5238` | `data/scaffolds/scorer_input.py:14` | `bound-check.strace.txt:5932` |
| `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/lib-dynload/_sqlite3.cpython-312-x86_64-linux-gnu.so` | `546a1b464dcf665bea56c74c90e6cdd15b5e9067cda94ab1224f13fcdab8dbdf` | `data/datasets/bird_minidev/verify/check.py:30` | `bound-check.strace.txt:5785` |
| `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/lib-dynload/math.cpython-312-x86_64-linux-gnu.so` | `67a2a81dec8bd6cb3ddf5057860e144afed0dcb36ad3d8ee6e174439607f9707` | `data/scaffolds/scorer_input.py:17` | `bound-check.strace.txt:5847` |
| `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/lib-dynload/zlib.cpython-312-x86_64-linux-gnu.so` | `701ac4d4e7b79e3541ad56d382d62c36efbc786a29659f33605fe59c876b0aa2` | `data/scaffolds/scorer_input.py:17` | `bound-check.strace.txt:5887` |
