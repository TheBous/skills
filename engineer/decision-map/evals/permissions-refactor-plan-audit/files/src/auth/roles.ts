export type Role = "OWNER" | "ADMIN" | "MEMBER";

export function requireRole(userRole: Role, allowed: Role[]): boolean {
  return allowed.includes(userRole);
}
