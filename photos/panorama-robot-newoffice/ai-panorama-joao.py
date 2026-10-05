#!/usr/bin/env python

'''
AI-assisted stitching
=====================

Based on panorama.py. Tries to stitch as many images as possible using:
  1. all images at once, sweeping stitcher parameters
  2. hierarchical stitching (stitch neighbours in pairs, then stitch the results)
  3. greedy chain (grow one panorama left to right, skipping images that fail)
The result with the most images wins.

Note: Stitcher.stitch() returns OK even when it silently drops images, so the
number of images actually used is read from stitcher.component().

Usage: python ai-panorama.py *-640x480.png
'''

# Python 2/3 compatibility
from __future__ import print_function

import itertools

import numpy as np
import cv2 as cv

import argparse
import sys

modes = (cv.Stitcher_PANORAMA, cv.Stitcher_SCANS)

parser = argparse.ArgumentParser(prog='ai-panorama.py', description='AI-assisted stitching.')
parser.add_argument('--output', default = 'ai-panorama.jpg',
    help = 'Resulting image. The default is `ai-panorama.jpg`.')
parser.add_argument('--match-conf', type = float, default = 0.3,
    help = 'Feature-matcher inlier confidence used only for the used/dropped diagnostic. Default 0.3.')
parser.add_argument('img', nargs='+', help = 'input images, in left-to-right order')

__doc__ += '\n' + parser.format_help()

# parameter sweep (strictest settings first, so the cleanest result wins)
SCALES = [1.0, 2.0]          # upscale inputs to give the feature detector more to work with
MODES = [('PANORAMA', cv.Stitcher_PANORAMA), ('SCANS', cv.Stitcher_SCANS)]
WAVES = [True, False]
CONFS = [1.0, 0.7, 0.5, 0.3, 0.1]


def report_used_images(imgs, names, match_conf=0.3):
    """Print which input images survive matching, so silently-dropped ones are visible.
    match_conf is the feature-matcher inlier confidence (typically 0.3-0.65),
    a different scale from the stitcher's own panoConfidenceThresh."""
    try:
        finder = cv.SIFT_create()
        features = [cv.detail.computeImageFeatures2(finder, img) for img in imgs]
        matcher = cv.detail.BestOf2NearestMatcher_create(False, match_conf)
        pairwise = matcher.apply2(features)
        matcher.collectGarbage()
        indices = cv.detail.leaveBiggestComponent(features, pairwise, match_conf)
        used = sorted(int(i) for i in np.array(indices).flatten())
        print("images used: %d of %d" % (len(used), len(imgs)))
        for i, name in enumerate(names):
            print("  %-40s %s" % (name, "USED" if i in used else "DROPPED"))
    except Exception as e:
        print("could not run match diagnostics:", e)


def try_stitch(imgs, scale, mode, wave, conf):
    """One stitch attempt. Returns (pano, used_indices) or (None, [])."""
    work = imgs
    if scale != 1.0:
        work = [cv.resize(i, None, fx=scale, fy=scale, interpolation=cv.INTER_CUBIC) for i in imgs]
    stitcher = cv.Stitcher.create(mode)
    stitcher.setPanoConfidenceThresh(conf)
    stitcher.setWaveCorrection(wave)
    stitcher.setRegistrationResol(0.6 * scale * scale)  # don't downscale the upscaled images
    try:
        status, pano = stitcher.stitch(work)
    except cv.error:
        return None, []
    if status != cv.Stitcher_OK or pano is None:
        return None, []
    used = sorted(int(i) for i in np.array(stitcher.component()).flatten())
    return pano, used


def stitch_best(imgs):
    """Sweep parameters; keep the attempt that uses the most images (stop early if all used).
    Returns (pano, used_indices, settings) or (None, [], None)."""
    best = (None, [], None)
    for scale, (mode_name, mode), wave, conf in itertools.product(SCALES, MODES, WAVES, CONFS):
        pano, used = try_stitch(imgs, scale, mode, wave, conf)
        if pano is not None and len(used) > len(best[1]):
            best = (pano, used, '%s, conf=%.1f, wave=%s, scale=%.0fx' % (mode_name, conf, wave, scale))
            if len(used) == len(imgs):
                break
    return best


def strategy_all(imgs, names):
    pano, used, settings = stitch_best(imgs)
    if pano is None:
        return None
    return pano, [names[i] for i in used], settings


def merge_pair(a, b):
    """Stitch two images; only accept the result if BOTH were actually used."""
    pano, used, _ = stitch_best([a, b])
    return pano if pano is not None and len(used) == 2 else None


def strategy_hierarchical(imgs, names):
    level = [(img, [n]) for img, n in zip(imgs, names)]
    merges = 0
    while len(level) > 1:
        nxt, i, progress = [], 0, False
        while i < len(level):
            if i + 1 < len(level):
                pano = merge_pair(level[i][0], level[i + 1][0])
                if pano is not None:
                    nxt.append((pano, level[i][1] + level[i + 1][1]))
                    merges += 1
                    progress = True
                    i += 2
                    continue
            nxt.append(level[i])
            i += 1
        level = nxt
        if not progress:
            break
    best = max(level, key=lambda x: len(x[1]))
    if len(best[1]) < 2:
        return None
    return best[0], best[1], 'hierarchical (%d merges)' % merges


def strategy_greedy(imgs, names):
    pano, used = imgs[0], [names[0]]
    for img, name in zip(imgs[1:], names[1:]):
        merged = merge_pair(pano, img)
        if merged is not None:
            pano, used = merged, used + [name]
        else:
            print("  greedy: skipped " + name)
    return (pano, used, 'greedy chain') if len(used) > 1 else None


def main():
    args = parser.parse_args()

    # read input images
    imgs = []
    for img_name in args.img:
        img = cv.imread(cv.samples.findFile(img_name))
        if img is None:
            print("can't read image " + img_name)
            sys.exit(-1)
        imgs.append(img)

    report_used_images(imgs, args.img, args.match_conf)

    best = None
    for label, strategy in [('all at once', strategy_all),
                            ('hierarchical', strategy_hierarchical),
                            ('greedy chain', strategy_greedy)]:
        print("trying: " + label)
        result = strategy(imgs, args.img)
        if result:
            print("  -> %d images stitched [%s]" % (len(result[1]), result[2]))
            if best is None or len(result[1]) > len(best[1]):
                best = result
        else:
            print("  -> failed")
        if best and len(best[1]) == len(imgs):
            break

    if best is None:
        print("Can't stitch any images")
        sys.exit(-1)

    pano, used, settings = best
    cv.imwrite(args.output, pano)
    print("stitching completed. %s saved!" % args.output)
    print("images stitched: %d of %d" % (len(used), len(imgs)))
    for name in args.img:
        print("  %-40s %s" % (name, "USED" if name in used else "DROPPED"))
    print("settings: " + settings)
    print("output size: %dx%d" % (pano.shape[1], pano.shape[0]))

    print('Done')


if __name__ == '__main__':
    print(__doc__)
    main()
    cv.destroyAllWindows()