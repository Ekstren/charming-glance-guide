export const S1_END = new Date('2026-08-30T06:00:00-07:00');
export const S2_END = new Date('2026-11-05T06:00:00-08:00');
export const SERVER_START = new Date('2026-07-15T06:00:00-07:00');
export const seasonKeyAt = (ms=Date.now()) => ms < S1_END.getTime() ? 's1' : 's2';