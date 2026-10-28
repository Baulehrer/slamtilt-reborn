# Amiga / PC bounded comparison

| Observed data | Result | Evidence |
|---|---|---|
| 14 base geometry layers, 42 normal/hit/render planes | Byte-identical after conversion | analysis/traces/amiga-pc-assets-comparison.json |
| 75 ball frames, ball mask, small/large score fonts | Byte-identical after conversion | same |
| Compressed DMD bank frames | RC4:1,712 match PC andsevenMean variants. Revision2 adds13Pirate frames, including12source variants. | analysis/traces/amiga-dmd-banks.json |
| DMD expansion | Original68k decoder plus original initialized LUT agrees for all1,719RC4bank frames; anadditional13Pirate frames includingoverlap are separatelyverified | analysis/traces/amiga-dmd-original.json |
| Mean repair animation | Amiga TIRE / PC TYRE; callback timeline28+25+50,10000000award identifies source bank | Mean.Bin0x65e28..0x65ec8; sourcebank0x6cd65; PCcallback0x4132d4 |
| Mean contact art | Twelve planar frames/31,488bytes, original positions and color indices preserved | analysis/traces/amiga-contact-frames.json |
| Flipper art | MeanL3/R3 andSpaceL2/R2 versusPC L1/R1 | decoded original flipper headers and selected input files |
| Demon lamp8 | Source24 rows versus25 native rows, transparent padding | original Raw lamp descriptor |
| Amiga versus PC physics/rules | UNKNOWN; the current port uses shared-native rules for both sources | No full Amiga gameplay trace captured |

No Windows assets are loaded for an Amiga import. PC files serve only as development comparison inputs. The decoder reads users’ original Amiga data; generated mapping tables contain offsets, not pixels. Demon uses the earlier uncompressed mapping path, not the compressed-bank proof. A Piratepanorama192×20andtwo5-tile16×20banksarealsoverified. Remaining individual fragments and full Amiga display timing/mask behavior are not established by these tests.
