export const accessCookieOptions = {
  httpOnly: true,
  sameSite: 'lax',
  secure: process.env.COOKIE_SECURE !== 'false',
  maxAge: Number(process.env.ACCESS_COOKIE_MAXAGE || 900000),
};
export const refreshCookieOptions = {
  httpOnly: true,
  sameSite: 'lax',
  secure: process.env.COOKIE_SECURE !== 'false',
  maxAge: Number(process.env.REFRESH_COOKIE_MAXAGE || 604800000),
};
