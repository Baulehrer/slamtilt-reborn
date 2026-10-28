/* Optional QA-only LD_PRELOAD probe. Never bundled with the game.
 * cc -shared -fPIC -O2 tools/reborn_sdl_stall_probe.c -ldl -o probe.so
 * Reports calls exceeding 50ms, including on-thread CPU time and switches.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/resource.h>
#include <time.h>
#include <unistd.h>

static uint64_t ns(clockid_t clock) {
    struct timespec t;
    clock_gettime(clock, &t);
    return (uint64_t)t.tv_sec * 1000000000 + t.tv_nsec;
}
#define MEASURE(name, args, call) \
bool name args { \
    static bool (*original) args; \
    if (!original) original = dlsym(RTLD_NEXT, #name); \
    struct rusage before, after; \
    getrusage(RUSAGE_THREAD, &before); \
    const uint64_t wall = ns(CLOCK_MONOTONIC), cpu = ns(CLOCK_THREAD_CPUTIME_ID); \
    const bool result = original call; \
    const uint64_t elapsed = ns(CLOCK_MONOTONIC) - wall; \
    if (elapsed > 50000000) { \
        getrusage(RUSAGE_THREAD, &after); \
        fprintf(stderr, "SDL_STALL pid=%d api=%s start_ns=%llu wall_ms=%.3f cpu_ms=%.3f voluntary=%ld involuntary=%ld\n", \
            getpid(), #name, (unsigned long long)wall, elapsed / 1e6, \
            (ns(CLOCK_THREAD_CPUTIME_ID) - cpu) / 1e6, \
            after.ru_nvcsw - before.ru_nvcsw, after.ru_nivcsw - before.ru_nivcsw); \
    } \
    return result; \
}

MEASURE(SDL_PollEvent, (void *event), (event))
MEASURE(SDL_RenderPresent, (void *renderer), (renderer))
MEASURE(SDL_UpdateTexture, (void *texture, const void *rect, const void *pixels, int pitch), (texture, rect, pixels, pitch))
MEASURE(SDL_PutAudioStreamData, (void *stream, const void *buf, int len), (stream, buf, len))
