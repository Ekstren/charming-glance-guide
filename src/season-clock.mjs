export const S1_END = new Date('2026-08-30T06:00:00-07:00');
export const S2_END = new Date('2026-11-05T06:00:00-08:00');
// Season 3 rollover is a server-calendar projection until confirmed in game.
export const S3_START = S2_END;
export const S3_END = new Date('2027-02-25T06:00:00-08:00');
export const SERVER_START = new Date('2026-07-15T06:00:00-07:00');
export const seasonKeyAt = (ms=Date.now()) => ms < S1_END.getTime() ? 's1' : ms < S2_END.getTime() ? 's2' : 's3';